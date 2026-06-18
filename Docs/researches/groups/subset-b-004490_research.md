# Research Report: subset-b-004490

This grouped report covers Intel Ethernet driver sources under the Ceph client source mirror. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ptp.c

## Purpose
`igb_ptp.c` implements Precision Time Protocol support for the Intel `igb` PCI Ethernet driver. It exposes a PHC through `ptp_clock_register()`, configures hardware timestamp filters, converts NIC timer values into kernel `ktime_t` hardware timestamps, manages SDP pins for external timestamp and periodic output features, and recovers from known timestamp latch hangs.

## Important APIs, Types, And Functions
The main public entry points are `igb_ptp_init()`, `igb_ptp_reset()`, `igb_ptp_stop()`, `igb_ptp_suspend()`, `igb_ptp_rx_hang()`, `igb_ptp_tx_hang()`, `igb_ptp_rx_pktstamp()`, `igb_ptp_rx_rgtstamp()`, `igb_ptp_hwtstamp_get()`, and `igb_ptp_hwtstamp_set()`. PTP clock operations are installed in `adapter->ptp_caps` and differ by MAC generation: 82576 uses a `cyclecounter`/`timecounter`, 82580/i350/i354 use a 40-bit timer with overflow work, and i210/i211 use seconds/nanoseconds SYSTIM registers directly. Pin support is handled by `igb_pin_direction()`, `igb_pin_extts()`, `igb_pin_perout()`, and feature callbacks for 82580 and i210.

## Control Flow
Probe calls `igb_ptp_init()`, which selects capabilities and function pointers by `hw->mac.type`, registers the PHC, initializes locks/work, and calls `igb_ptp_reset()`. Reset reapplies timestamp mode, initializes timer increment registers or writes the current wall clock into SYSTIM, enables timestamp interrupts, and schedules overflow maintenance where required. Timestamp ioctl changes enter through `igb_ptp_hwtstamp_set()`, which validates requested TX/RX modes and programs TSYNC, ETQF, FTQF, and related registers. TX timestamp completion is handled by `igb_ptp_tx_work()` or watchdog cleanup; RX timestamps are read either from inline packet headers or global RXSTMP registers.

## State And Persistence
Persistent driver state lives in `struct igb_adapter`: `ptp_clock`, `ptp_caps`, `ptp_flags`, `tmreg_lock`, `cc`, `tc`, `tstamp_config`, `ptp_tx_skb`, `ptp_tx_start`, `perout[]`, `sdp_config[]`, timeout counters, and PPS state. Hardware state is volatile and must be rebuilt after reset. The saved `tstamp_config` is the software shadow returned to users and replayed by `igb_ptp_reset()`.

## Dependencies And Integration Points
The file depends on Linux PTP, hwtstamp, net timestamping, workqueue, timecounter, and PCI MMIO APIs. It integrates with `igb` TX/RX paths through skb timestamp callbacks and with netdev timestamping ioctls through `igb_ptp_hwtstamp_get/set()`. SDP pin routing integrates with the PTP pin framework via `ptp_find_pin()` and `ptp_pin_desc`.

## Risks
The code is sensitive to register ordering, timer width overflow, and hardware generation differences. 82576 and 82580 require periodic timecounter updates to prevent stale conversion after SYSTIM wrap. Only one TX timestamp skb is tracked, so races around `ptp_tx_skb` and `__IGB_PTP_TX_IN_PROGRESS` must remain carefully ordered. RX/TX timestamp valid bits can wedge hardware until cleared by watchdog paths. Incorrect filter programming can silently broaden filters to all packets on newer hardware.

## Test Signals
Useful validation includes PHC registration logs, `phc2sys`/`ptp4l` operation, `ethtool -T`, timestamp ioctl filter tests, TX timestamp timeout counters, RX hang clear counters, suspend/resume and reset tests, and SDP EXTS/PEROUT/PPS tests on hardware supporting those pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_xsk.c

## Purpose
`igb_xsk.c` implements AF_XDP zero-copy support for `igb`. It binds and unbinds `xsk_buff_pool` instances to queue IDs, switches RX ring software metadata between skb buffers and zero-copy XDP buffers, processes zero-copy RX descriptors through XDP programs, transmits AF_XDP descriptors, and provides the netdev XSK wakeup hook.

## Important APIs, Types, And Functions
External entry points include `igb_xsk_pool()`, `igb_xsk_pool_setup()`, `igb_alloc_rx_buffers_zc()`, `igb_clean_rx_ring_zc()`, `igb_clean_rx_irq_zc()`, `igb_xmit_zc()`, and `igb_xsk_wakeup()`. Internal helpers perform ring quiesce/restart (`igb_txrx_ring_disable()`, `igb_txrx_ring_enable()`), metadata reallocation (`igb_realloc_rx_buffer_info()`), descriptor filling (`igb_fill_rx_descs()`), skb construction for XDP_PASS (`igb_construct_skb_zc()`), and XDP execution (`igb_run_xdp_zc()`).

## Control Flow
Pool setup validates the queue, DMA maps the AF_XDP pool, disables the queue pair if the interface is running with XDP enabled, reallocates RX buffer metadata to zero-copy format, re-enables rings, and wakes RX NAPI. Disable reverses the process and DMA unmaps the pool. During RX cleaning, each completed descriptor supplies an `xdp_buff`; optional inline PTP timestamp headers are stripped, the XDP program is run, and results are either redirected, transmitted back, consumed, or converted into an skb for the normal stack. TX reads AF_XDP TX descriptors with `xsk_tx_peek_release_desc_batch()`, DMA syncs each payload, builds advanced TX descriptors, and updates the hardware tail.

## State And Persistence
State is per ring: `rx_buffer_info_zc`, `rx_buffer_info`, `xsk_pool`, descriptor indices, ring flags, XDP program pointer, and queue stats. Pool DMA mappings are persistent until pool disable. Need-wakeup state is maintained through `xsk_set_rx_need_wakeup()` and `xsk_clear_rx_need_wakeup()` when the pool requests that mode.

## Dependencies And Integration Points
This file depends on AF_XDP pool APIs, generic XDP redirect/TX APIs, BPF tracing, NAPI, DMA synchronization, and existing `igb` ring configuration and timestamp helpers. It integrates with `igb_ptp_rx_pktstamp()` for inline RX hardware timestamps, `igb_finalize_xdp()` for XDP TX/redirect finalization, and interrupt generation through EICS/ICS writes in `igb_xsk_wakeup()`.

## Risks
The pool switch path temporarily disables live queues and must restore both descriptor state and NAPI state on failures. RX zero-copy paths must not leak XDP buffers across PASS, DROP, REDIRECT, and TX outcomes. The code relies on descriptor length zeroing and DMA barriers to avoid stale descriptor consumption. `igb_xmit_zc()` currently sets report status on every descriptor, which is explicitly noted as a possible performance optimization. Need-wakeup handling must avoid leaving user space asleep when buffers or TX work remain.

## Test Signals
Run AF_XDP zero-copy bind/unbind tests, XDP_PASS/DROP/TX/REDIRECT programs, `xdpsock` RX/TX need-wakeup modes, queue restart while link is up, and pool setup failure injection. Counters for RX allocation failures, XDP exceptions, TX completions, and packet delivery through NAPI/GRO are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/Makefile

## Purpose
This Makefile builds the Intel 82576/I350 Virtual Function Ethernet driver when `CONFIG_IGBVF` is enabled.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_IGBVF) += igbvf.o` and composes the module from `vf.o`, `mbx.o`, `ethtool.o`, and `netdev.o`.

## Control Flow
Kbuild includes this file from the parent driver tree. If the kernel configuration enables `IGBVF`, the listed objects are linked into `igbvf.o`; otherwise no module object is emitted.

## State And Persistence
No runtime state is stored here. The only persistent behavior is the object composition contract used by Kbuild.

## Dependencies And Integration Points
The object list defines the main integration boundaries: VF hardware operation setup (`vf.o`), PF/VF mailbox transport (`mbx.o`), ethtool support (`ethtool.o`), and the PCI/netdev driver (`netdev.o`).

## Risks
Missing an object from the list would produce link failures or silently omit driver features. Adding new source files in this directory requires updating this Makefile.

## Test Signals
Build coverage with `CONFIG_IGBVF=m` and `CONFIG_IGBVF=y` should produce `igbvf.ko` or built-in driver objects without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/defines.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/defines.h

## Purpose
`defines.h` centralizes `igbvf` hardware constants: descriptor alignment, RX/TX descriptor status bits, device control/status fields, queue-enable bits, SRRCTL layout, DCA flags, speed/duplex values, and driver-local error codes.

## Important APIs, Types, And Functions
The file is macro-only. Key definitions include descriptor multiples (`REQ_TX_DESCRIPTOR_MULTIPLE`, `REQ_RX_DESCRIPTOR_MULTIPLE`), RX status and error masks (`E1000_RXD_STAT_*`, `E1000_RXDEXT_STATERR_*`), `E1000_RXDEXT_ERR_FRAME_ERR_MASK`, reset and link/speed bits (`E1000_CTRL_RST`, `E1000_STATUS_*`), advanced TX bits, maximum frame sizes, SRRCTL descriptor type and buffer size fields, queue enable bits, and `E1000_VF_INIT_TIMEOUT`.

## Control Flow
There is no direct control flow. These constants are consumed by `netdev.c`, `vf.c`, and the hardware register wrappers to encode register writes and decode descriptor writebacks.

## State And Persistence
No state is stored. The constants define how volatile hardware state is interpreted.

## Dependencies And Integration Points
The header is included by `vf.h`, which makes its constants available throughout the `igbvf` driver. It depends on common kernel bit macros such as `BIT()` through included headers in the includer chain.

## Risks
Incorrect constants can corrupt descriptor processing, interrupt programming, or reset behavior. The RX error mask controls packet drop decisions, so accidental changes can pass corrupted frames or drop valid traffic. Descriptor multiple values must remain compatible with hardware and ethtool ring resizing.

## Test Signals
Compile tests catch missing macros; functional tests should include RX checksum/error handling, jumbo MTU configuration, ethtool ring resizing alignment, queue enable/disable, and link speed reporting on VF hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/ethtool.c

## Purpose
`ethtool.c` exposes the VF driver's user-facing diagnostics and tunables through `struct ethtool_ops`. It reports link settings, selected registers, statistics, ring sizes, interrupt coalescing, driver info, and a simple link self-test while rejecting unsupported operations such as EEPROM, pause, WOL, and link mode changes.

## Important APIs, Types, And Functions
The central registration function is `igbvf_set_ethtool_ops()`. Important callbacks include `igbvf_get_link_ksettings()`, `igbvf_get_regs()`, `igbvf_get_ringparam()`, `igbvf_set_ringparam()`, `igbvf_diag_test()`, `igbvf_get_coalesce()`, `igbvf_set_coalesce()`, `igbvf_get_ethtool_stats()`, `igbvf_get_strings()`, and `igbvf_nway_reset()`. `igbvf_gstrings_stats[]` maps visible stat names to adapter fields and base counters.

## Control Flow
Etthool requests enter the callback table. Ring resizing validates requested counts, clamps and aligns them, serializes against reset using `__IGBVF_RESETTING`, and if running, brings the interface down, allocates replacement resources, swaps ring structs, and brings the interface back up. Coalescing converts requested microseconds into EITR units or adaptive modes. The link self-test checks link through the mailbox-protected MAC operation and reports failure when `STATUS.LU` is absent.

## State And Persistence
Etthool operations read and write `adapter->msg_enable`, `requested_itr`, `current_itr`, ring `count`, and hardware EITR registers. Stats are derived from `adapter->stats` minus base fields because VF counters do not clear on read.

## Dependencies And Integration Points
The file integrates with netdev-private `igbvf_adapter`, PCI device identity, NAPI/ring resource functions from `netdev.c`, and mailbox-protected link checks in `vf.c`. The callback table is attached to the netdev during probe.

## Risks
Ring resizing is high risk because MSI-X handlers keep ring struct pointers; the code preserves those pointers by copying replacement content into existing ring allocations. Error handling after partial resize still brings the device up, so tests should cover allocation failures. Coalescing writes directly to the RX ring ITR register and must match the interrupt setup state. Stats pointer arithmetic depends on correct offsets and field sizes.

## Test Signals
Use `ethtool -i`, `-k`, `-S`, `-g/-G`, `-c/-C`, `-t`, and `-d` on a VF. Verify ring counts persist across down/up, invalid coalescing values fail with `EINVAL`, unsupported operations return `EOPNOTSUPP`, and stats advance monotonically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/igbvf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/igbvf.h

## Purpose
`igbvf.h` is the main private header for the Intel VF driver. It defines driver limits, interrupt moderation constants, ring and adapter structures, board metadata, state bits, feature flags, descriptor access macros, and cross-file function prototypes.

## Important APIs, Types, And Functions
Core types include `struct igbvf_buffer`, `union igbvf_desc`, `struct igbvf_ring`, `struct igbvf_adapter`, and `struct igbvf_info`. Constants define default/min/max descriptor counts, ITR profiles, RX thresholds, VLAN/mac-filter limits, and `IGBVF_MAX_MAC_FILTERS`. Public prototypes expose lifecycle and resource APIs such as `igbvf_up()`, `igbvf_down()`, `igbvf_reinit_locked()`, `igbvf_setup_rx_resources()`, `igbvf_setup_tx_resources()`, and `igbvf_update_stats()`.

## Control Flow
The header does not execute logic, but it shapes control flow by defining state bits (`__IGBVF_TESTING`, `__IGBVF_RESETTING`, `__IGBVF_DOWN`) and the adapter fields used by reset, watchdog, NAPI, TX/RX, ethtool, and PCI probe/remove paths.

## State And Persistence
`struct igbvf_adapter` is the persistent per-netdev state. It tracks timers/work, active VLANs, ring pointers, hardware state, netdev/PCI pointers, stats, MSI-X entries, mailbox-backed hardware, WOL/PBA values, feature flags, link state, and reset timing. `struct igbvf_ring` stores descriptor memory, DMA address, indices, NAPI object, interrupt moderation state, per-ring stats, and a partially assembled RX skb.

## Dependencies And Integration Points
The header includes Linux netdevice, timer, VLAN, IO, and type headers plus `vf.h`. It is included by `netdev.c`, `ethtool.c`, and other driver-local files, binding VF hardware abstractions to kernel networking APIs.

## Risks
Structure layout and shared state are central to concurrency correctness. Ring fields are accessed from interrupt, NAPI, netdev, and ethtool contexts. Any change to buffer union semantics can break TX/RX DMA unmapping. Feature flags must remain synchronized with netdev feature changes and hardware workarounds.

## Test Signals
Build coverage is the first signal. Runtime coverage should exercise state transitions, ring allocation/free, VLAN filter restoration, MAC filter updates, reset while traffic is active, and stats updates across link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/igbvf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.c

## Purpose
`mbx.c` implements the VF side of the PF/VF mailbox protocol. It provides posted read/write operations, polling for PF acknowledgements or messages, read-to-clear bit preservation, mailbox lock acquisition, and initialization of `hw->mbx.ops`.

## Important APIs, Types, And Functions
The exported function is `e1000_init_mbx_params_vf()`. Important internal operations include `e1000_poll_for_msg()`, `e1000_poll_for_ack()`, `e1000_read_posted_mbx()`, `e1000_write_posted_mbx()`, `e1000_read_v2p_mailbox()`, `e1000_check_for_bit_vf()`, `e1000_check_for_msg_vf()`, `e1000_check_for_ack_vf()`, `e1000_check_for_rst_vf()`, `e1000_obtain_mbx_lock_vf()`, `e1000_write_mbx_vf()`, and `e1000_read_mbx_vf()`.

## Control Flow
Posted writes call the raw write op, then poll until PFACK or timeout. Posted reads poll until PFSTS, then read mailbox memory. Raw writes first obtain VF ownership via `V2PMAILBOX.VFU`, clear stale ACK/message bits, copy up to `size` words into `VMBMEM`, update counters, and signal PF with `REQ`. Raw reads acquire ownership, copy words out, acknowledge with `ACK`, and update receive counters.

## State And Persistence
State is kept in `hw->mbx`: timeout, delay, mailbox size, operation pointers, and statistics. Read-to-clear V2P bits are cached in `hw->dev_spec.vf.v2p_mailbox` so a status bit is not lost when multiple checks inspect the register. Timeout is set to zero after polling failure, causing future posted sends to fail until reset reinitializes mailbox communication.

## Dependencies And Integration Points
The file depends on register wrappers from `regs.h`, mailbox constants from `mbx.h`, `udelay()`, and `hw->mbx_lock` held by callers. `vf.c` uses the ops to request reset, MAC/VLAN/multicast/filter changes, LPE changes, and link-status communication with the PF.

## Risks
Mailbox operations are race-prone because PF and VF share the buffer and status bits are read-to-clear. Callers must hold `hw->mbx_lock`; lockdep assertions enforce this for raw read/write. Timeout zeroing can make a VF appear permanently unable to communicate until reset. Message size is not internally bounded beyond caller-supplied `size`, so callers must respect `E1000_VFMAILBOX_SIZE`.

## Test Signals
Validate VF reset handshake, MAC address programming, VLAN add/remove, multicast updates, link checks, and PF reset notifications. Useful counters are `msgs_tx`, `msgs_rx`, `acks`, `reqs`, and `rsts`; timeout paths should be tested with PF unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.h

## Purpose
`mbx.h` defines the PF/VF mailbox register bits, message encoding, timeouts, and the initialization prototype used by `igbvf`.

## Important APIs, Types, And Functions
The header exports `e1000_init_mbx_params_vf()`. It defines V2P mailbox bits such as `REQ`, `ACK`, `VFU`, `PFU`, `PFSTS`, `PFACK`, `RSTI`, and `RSTD`; message type modifiers `ACK`, `NACK`, and `CTS`; timeout constants; and VF-originated commands such as reset, set MAC address, set multicast, set VLAN, and set LPE.

## Control Flow
There is no executable flow. The constants drive mailbox state checks in `mbx.c` and command construction/parsing in `vf.c`.

## State And Persistence
No state is stored here. The constants define persistent protocol compatibility with the PF driver and hardware.

## Dependencies And Integration Points
The header includes `vf.h`, which creates a circular-looking but guarded local dependency between hardware type definitions and mailbox operation declarations. It is used by both `mbx.c` and `vf.c`.

## Risks
Protocol bit changes would break compatibility with PF mailbox handling. `E1000_VFMAILBOX_SIZE` constrains all command buffers, and the `MSGINFO` field is overloaded for command-specific metadata such as multicast count or add/remove operations.

## Test Signals
Compile tests catch missing symbols; runtime signals include successful VF reset ACK, MAC/VLAN/multicast command ACK/NACK behavior, and link CTS handling after PF resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/netdev.c

## Purpose
`netdev.c` is the main Intel VF network driver implementation. It registers the PCI driver, creates the netdev, manages TX/RX descriptor rings, handles MSI-X interrupts and NAPI, implements reset/open/close/MTU/MAC/VLAN/filter operations, updates VF statistics, handles watchdog and TX timeout recovery, and supports suspend/resume plus PCI error recovery.

## Important APIs, Types, And Functions
Key lifecycle functions are `igbvf_probe()`, `igbvf_remove()`, `igbvf_open()`, `igbvf_close()`, `igbvf_up()`, `igbvf_down()`, `igbvf_reinit_locked()`, and `igbvf_reset()`. RX/TX paths include `igbvf_alloc_rx_buffers()`, `igbvf_clean_rx_irq()`, `igbvf_clean_tx_irq()`, `igbvf_xmit_frame()`, `igbvf_tso()`, `igbvf_tx_csum()`, `igbvf_tx_map_adv()`, and `igbvf_tx_queue_adv()`. Interrupt and polling functions include `igbvf_request_msix()`, `igbvf_configure_msix()`, `igbvf_intr_msix_tx()`, `igbvf_intr_msix_rx()`, `igbvf_msix_other()`, and `igbvf_poll()`. Netdev ops are collected in `igbvf_netdev_ops`.

## Control Flow
Probe enables PCI memory access, maps BAR0, initializes software and hardware ops, sets features, performs a PF-mediated reset/MAC read, initializes timers/work, resets hardware, registers the netdev, and initializes stats baselines. Opening allocates rings, configures hardware, requests MSI-X vectors, enables NAPI/interrupts, and starts the watchdog. RX interrupts schedule NAPI; NAPI cleans RX descriptors, builds skbs, handles checksum/VLAN, returns buffers, and reenables interrupts. TX maps skb data/frags into descriptors, optionally emits context descriptors for TSO/checksum/VLAN, updates the tail, and completion interrupts reclaim DMA mappings and wake the queue. Watchdog checks link through mailbox, updates carrier/stats, flushes stalled TX on link loss, and kicks RX cleanup. Reset paths serialize on `__IGBVF_RESETTING` and run down/up around PF reset handshakes.

## State And Persistence
The netdev-private `igbvf_adapter` owns persistent driver state: rings, MSI-X entries, NAPI, timers, work items, active VLAN bitmap, netdev features, mailbox-backed hardware state, counters, link speed/duplex, and reset state bits. Ring state includes DMA-coherent descriptors, per-buffer skb/page DMA mappings, producer/consumer indices, interrupt throttle values, and stats. VF hardware counters do not clear on read, so software tracks last and base values.

## Dependencies And Integration Points
The file integrates with PCI core, netdev ops, NAPI/GRO, DMA mapping, skb offload helpers, VLAN core, ethtool registration, mailbox/MAC ops from `vf.c` and `mbx.c`, and hardware register constants from `vf.h`/`regs.h`. The PCI ID table binds Intel 82576 VF and I350 VF devices.

## Risks
Concurrency spans hard IRQ, NAPI, timers, workqueues, ethtool, and netdev operations. Reset serialization is essential. RX packet-split page reuse and DMA unmapping must stay balanced. TX descriptor accounting needs gaps to avoid tail/head ambiguity. PCI error recovery and suspend/resume must not leave interrupts or NAPI enabled against freed rings. Mailbox failures can prevent link/MAC/VLAN operations. The code supports MSI-X only; failure to allocate three vectors prevents operation.

## Test Signals
Exercise probe/remove, open/close, traffic under RX/TX checksum and TSO, VLAN add/remove, multicast/unicast filters, MTU changes up to 9216, link up/down, PF reset, VF reset, TX timeout, suspend/resume, PCI error recovery, ethtool ring resize/coalescing, and stats monotonicity. Watch for DMA mapping errors, allocation failures, carrier changes, and reset loop logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/regs.h

## Purpose
`regs.h` defines the VF-visible Intel register map and MMIO access macros used by `igbvf`.

## Important APIs, Types, And Functions
The file defines offsets for control/status, interrupt registers, IVAR, queue descriptor registers, DCA controls, receive address registers, VF statistics, V2P mailbox, and mailbox memory. Queue register macros such as `E1000_RDBAL(_n)`, `E1000_RDLEN(_n)`, `E1000_RXDCTL(_n)`, `E1000_TDBAL(_n)`, and `E1000_TXDCTL(_n)` encode hardware's split register layout for queues below and above index 4. Access macros `er32`, `ew32`, `array_er32`, `array_ew32`, and `e1e_flush()` wrap `readl()`/`writel()`.

## Control Flow
There is no executable control flow. These macros are invoked throughout `netdev.c`, `vf.c`, `mbx.c`, and `ethtool.c` for hardware access.

## State And Persistence
No software state is stored. The macros read and write MMIO-backed device state through `hw->hw_addr`.

## Dependencies And Integration Points
The macros assume the local variable name `hw` points to `struct e1000_hw`. This convention is used throughout the driver. Register offsets integrate the VF network path, interrupts, stats, and mailbox protocol with hardware.

## Risks
The `hw` implicit-variable style is concise but fragile during refactors. Incorrect offsets can corrupt hardware state or access the wrong queue. Register reads can have side effects, especially interrupt and mailbox status registers. Queue macro layout must match supported VF devices.

## Test Signals
Build tests catch missing register macros. Runtime validation includes ethtool register dump, interrupt delivery, ring enable/disable, mailbox communication, VF stats reads, and successful packet I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.c

## Purpose
`vf.c` implements VF-specific MAC operations and PF-mediated configuration commands. It initializes operation tables, resets the VF, obtains permanent MAC address information from the PF, reports link state, and requests MAC, multicast, unicast, VLAN, and maximum packet length changes through the mailbox.

## Important APIs, Types, And Functions
The public entry points are `e1000_init_function_pointers_vf()` and `e1000_rlpml_set_vf()`. Internal callbacks installed into `hw->mac.ops` include `e1000_reset_hw_vf()`, `e1000_init_hw_vf()`, `e1000_check_for_link_vf()`, `e1000_get_link_up_info_vf()`, `e1000_update_mc_addr_list_vf()`, `e1000_rar_set_vf()`, `e1000_read_mac_addr_vf()`, `e1000_set_uc_addr_vf()`, and `e1000_set_vfta_vf()`.

## Control Flow
Software initialization installs MAC and mailbox init callbacks. Reset asserts `CTRL.RST`, waits for PF reset indications to clear, enables mailbox timeout, sends `E1000_VF_RESET`, and reads the PF response containing the permanent MAC address or a NACK. MAC/VLAN/multicast/LPE changes build mailbox command buffers, send them with posted writes, and parse ACK/NACK responses. Link checks notice PF reset or mailbox timeout, read hardware `STATUS.LU`, consume PF CTS messages, and may request a driver reset if communication needs reinitialization.

## State And Persistence
Hardware identity and operations live in `struct e1000_hw`. MAC state includes `addr`, `perm_addr`, type, RAR count, MTA count, and `get_link_status`. Mailbox timeout state determines whether PF communication is considered live. The permanent MAC persists in `hw->mac.perm_addr` after PF reset response.

## Dependencies And Integration Points
The file uses mailbox ops from `mbx.c`, register macros from `regs.h`, constants from `mbx.h`/`defines.h`, and kernel Ethernet address helpers. `netdev.c` calls these operations under `hw->mbx_lock` for reset, filter programming, VLAN restore, MTU/LPE changes, and link watchdog checks.

## Risks
Most configuration is at PF discretion, so NACKs and timeouts must be handled gracefully. Multicast programming truncates to 30 hashes due to mailbox size. Link status can be stale because the VF cannot read PHY state directly. MAC filter additions can fail with `ENOSPC`. Reset sequencing depends on PF responsiveness and the mailbox timeout being restored only after reset.

## Test Signals
Validate PF-assigned MAC address, random fallback when missing, VF MAC changes accepted/rejected by PF, VLAN add/remove NACK handling, multicast filter programming, LPE updates on MTU changes, link up/down reporting, and behavior during PF reset or PF driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.h

## Purpose
`vf.h` defines the VF hardware abstraction for `igbvf`: supported PCI IDs, advanced RX/TX descriptor layouts, MAC and mailbox operation tables, VF stats layout, hardware state structure, and prototypes shared by `vf.c`, `mbx.c`, and `netdev.c`.

## Important APIs, Types, And Functions
Core definitions include `union e1000_adv_rx_desc`, `union e1000_adv_tx_desc`, `struct e1000_adv_tx_context_desc`, `enum e1000_mac_type`, `struct e1000_vf_stats`, `struct e1000_mac_operations`, `struct e1000_mbx_operations`, `struct e1000_mbx_info`, `struct e1000_dev_spec_vf`, and `struct e1000_hw`. Exported prototypes are `e1000_rlpml_set_vf()` and `e1000_init_function_pointers_vf()`.

## Control Flow
The header does not execute code but enables polymorphic hardware behavior through function pointer tables. `netdev.c` calls `hw->mac.ops.*` without knowing whether the underlying VF is 82576 or I350-style.

## State And Persistence
`struct e1000_hw` stores MMIO pointers, MAC state, mailbox state, device-specific VF mailbox cache, PCI identity fields, and the mailbox spinlock. `struct e1000_vf_stats` stores base, last, and accumulated values for VF counters that do not clear on read.

## Dependencies And Integration Points
The header includes PCI, delay, interrupt, Ethernet, `regs.h`, and `defines.h`, and includes `mbx.h` after core type definitions so mailbox structs can reference `struct e1000_hw`. It is the common hardware contract used by all `igbvf` implementation files.

## Risks
Descriptor layout must match hardware exactly; any packing or field change would break DMA interpretation. Operation pointer contracts require callers to hold the mailbox lock for PF-mediated actions. The included headers form a tight dependency cycle that should be changed cautiously.

## Test Signals
Build and sparse coverage are important. Runtime tests should validate descriptor TX/RX operation, stats rollover accounting, mailbox initialization, and device ID matching for both 82576 VF and I350 VF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/Makefile

## Purpose
This Makefile builds the Intel I225/I226 2.5G Ethernet Controller driver when `CONFIG_IGC` is enabled and optionally includes LED support when `CONFIG_IGC_LEDS` is enabled.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_IGC) += igc.o`, composes `igc-y` from core source files such as `igc_main.o`, `igc_mac.o`, `igc_i225.o`, `igc_base.o`, `igc_nvm.o`, `igc_phy.o`, `igc_diag.o`, `igc_ethtool.o`, `igc_ptp.o`, `igc_dump.o`, `igc_tsn.o`, and `igc_xdp.o`, and conditionally appends `igc_leds.o`.

## Control Flow
Kbuild evaluates the configuration symbols and links the selected objects into the `igc` module or built-in object.

## State And Persistence
No runtime state is stored. The persistent contract is module composition and optional LED object inclusion.

## Dependencies And Integration Points
The object list reflects the driver's subsystems: main PCI/netdev, MAC/NVM/PHY, diagnostics and ethtool, PTP, dump support, TSN, XDP/AF_XDP, and LEDs.

## Risks
Forgetting to list a new implementation file causes unresolved symbols or missing feature code. Conditional LED support must match declarations in `igc.h` and call sites in main driver code.

## Test Signals
Build the driver with `CONFIG_IGC=m/y` and with `CONFIG_IGC_LEDS` both enabled and disabled. Link errors are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc.h

## Purpose
`igc.h` is the main private header for the Intel I225/I226 driver. It defines queue limits, adapter/ring/q_vector state, TX/RX buffer structures, PTP and AF_XDP metadata, TSN/FPE fields, NFC filter structures, feature flags, helper macros, and cross-module prototypes.

## Important APIs, Types, And Functions
Important types include `struct igc_adapter`, `struct igc_ring`, `struct igc_q_vector`, `struct igc_tx_buffer`, `struct igc_rx_buffer`, `struct igc_tx_timestamp_request`, `struct igc_xdp_buff`, `struct igc_nfc_rule`, and `struct igc_fpe_t`. Key helpers/macros include `igc_desc_unused()`, `igc_rss_type()`, `igc_test_staterr()`, `igc_rx_bufsz()`, `igc_rx_pg_order()`, `txring_txq()`, and descriptor accessors `IGC_RX_DESC`, `IGC_TX_DESC`, and `IGC_TX_CTXTDESC`. Prototypes cover up/down, open/close, ring resources, RSS, reset, stats, XSK wakeup, PTP, NFC, LED setup, and queue control.

## Control Flow
The header has only inline helpers, but it defines how data flows among implementation files. TX/RX paths share `struct igc_ring`; interrupts group rings through `struct igc_q_vector`; PTP paths use `tx_tstamp[]`, `tmreg_lock`, `timecounter`, and pin descriptors; TSN paths use gate and credit fields in each ring; XDP/AF_XDP paths use `xdp_prog`, `xdp_rxq`, and `xsk_pool`.

## State And Persistence
`struct igc_adapter` is the persistent per-device state spanning netdev, PCI, hardware stats, queue arrays, timers, workqueues, link state, interrupt masks, RSS indirection, PTP clock, hwtstamp config, TSN/Qbv/Qav/FPE settings, NFC rules, LED state, and firmware version. Rings persist descriptor memory, DMA addresses, queue indices, tail registers, flags, producer/consumer indices, stats, and XDP pool state.

## Dependencies And Integration Points
The header pulls in PCI, netdevice, ethtool, SCTP, PTP, timecounter, timestamping, hrtimer, and XDP APIs plus `igc_hw.h`. It is shared by the driver's main, ethtool, PTP, TSN, XDP, base, and diagnostics code.

## Risks
This is a high-blast-radius header: changes can affect almost every `igc` subsystem. Ring and adapter fields are accessed from IRQ, NAPI, workqueue, timer, rtnl, and ethtool contexts. TSN, PTP, XDP, and AF_XDP fields interact with queue scheduling and timestamping, so layout and locking comments must be respected. Several flag values overlap semantically and must be interpreted in the right field.

## Test Signals
Build all `igc` objects, run traffic across all queues, RSS, XDP/AF_XDP, PTP timestamping, TSN offloads, ethtool stats/ring/coalesce, reset, suspend/resume, and LED configurations. Lockdep and KCSAN are useful for shared adapter/ring state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.c

## Purpose
`igc_base.c` provides base hardware operations for Intel I225/I226-class controllers. It resets MAC hardware, initializes NVM/MAC/PHY invariants, sets up copper link, initializes hardware filters, powers down PHY when safe, flushes RX FIFOs for manageability errata, classifies device IDs, and publishes the `igc_base_info` operation bundle.

## Important APIs, Types, And Functions
Externally visible functions include `igc_power_down_phy_copper_base()`, `igc_rx_fifo_flush_base()`, `igc_is_device_id_i225()`, `igc_is_device_id_i226()`, and the `igc_base_info` constant. Internal operations include `igc_reset_hw_base()`, `igc_init_nvm_params_base()`, `igc_setup_copper_link_base()`, `igc_init_mac_params_base()`, `igc_init_phy_params_base()`, `igc_get_invariants_base()`, `igc_acquire_phy_base()`, `igc_release_phy_base()`, and `igc_init_hw_base()`.

## Control Flow
Driver setup calls `igc_base_info.get_invariants`, which classifies device IDs as `igc_i225`, sets copper media, initializes MAC ops, NVM parameters, I225-specific NVM parameters, and PHY parameters. Hardware init initializes receive addresses, clears multicast and unicast hash tables, sets up link/flow control, and clears counters. Hardware reset disables PCIe master, masks interrupts, disables RX/TX, waits, asserts `CTRL.RST`, waits for auto-read completion, masks interrupts again, and clears pending causes. RX FIFO flush temporarily disables RX queues, rejects incoming packets while flushing, restores queue and RX control state, and clears generated counters.

## State And Persistence
State is stored in `struct igc_hw`: MAC type and ops, NVM properties, PHY properties, bus function, and device-specific semaphore behavior. Hardware register state is rewritten during reset/init, including interrupt masks, RCTL/TCTL, MTA/UTA tables, RLPML, RFCTL, and queue controls.

## Dependencies And Integration Points
The file depends on `igc_hw.h`, `igc_i225.h`, `igc_mac.h`, `igc_base.h`, and `igc.h`. It uses shared MAC/PHY/NVM helpers such as `igc_disable_pcie_master()`, `igc_get_auto_rd_done()`, `igc_setup_link()`, `igc_clear_hw_cntrs_base()`, and GPY PHY accessors. Main probe code consumes `igc_base_info`.

## Risks
Reset and FIFO flush sequences are timing-sensitive and register-order-sensitive. `igc_reset_hw_base()` deliberately logs but continues after auto-read failure to support blank/no EEPROM cases, so callers must handle partially initialized NVM contexts. Device ID classification controls the entire operation table. RX FIFO workaround must restore prior RX queue state to avoid traffic loss.

## Test Signals
Validate cold probe, reset, link setup, blank-NVM devices, I225/I226 device ID detection, manageability-enabled RX FIFO flush, PHY reset/read, MTA/UTA clearing, and counter clearing. Hardware logs for PCIe master disable and auto-read completion are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.h

## Purpose
`igc_base.h` declares base helper functions and defines advanced TX/RX descriptor layouts and SRRCTL bit helpers for the I225/I226 driver.

## Important APIs, Types, And Functions
The header declares `igc_rx_fifo_flush_base()`, `igc_power_down_phy_copper_base()`, `igc_is_device_id_i225()`, and `igc_is_device_id_i226()`. It defines `union igc_adv_tx_desc`, `struct igc_adv_tx_context_desc`, `union igc_adv_rx_desc`, advanced TX command/timestamp bits, `IGC_RAR_ENTRIES`, and SRRCTL field macros such as `IGC_SRRCTL_BSIZEPKT()`, `IGC_SRRCTL_BSIZEHDR()`, and `IGC_SRRCTL_DESCTYPE_ADV_ONEBUF`.

## Control Flow
There is no direct control flow. The descriptor definitions are consumed by TX/RX paths, and the declared helpers are implemented in `igc_base.c`.

## State And Persistence
No software state is stored. Descriptor layouts define the DMA contract between driver memory and hardware. SRRCTL macros define how RX buffer sizing and descriptor type are persisted in hardware registers.

## Dependencies And Integration Points
The header is included by base and main driver code. It depends on Linux endian types and bitfield helpers made available through includers. It complements `igc.h`, which provides descriptor accessors and ring/adapter state around these layouts.

## Risks
Descriptor structures must match hardware byte-for-byte. Incorrect command bits can break timestamping, VLAN insertion, checksum offload, TSO, or descriptor writeback. SRRCTL helper units are encoded in KB or 64-byte granularity; callers must pass sizes that match those expectations.

## Test Signals
Compile tests catch type visibility issues. Runtime tests include TX/RX traffic, VLAN/TSO/checksum offloads, PTP TX timestamp descriptor selection, and RX buffer-size configuration across MTUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.h -->

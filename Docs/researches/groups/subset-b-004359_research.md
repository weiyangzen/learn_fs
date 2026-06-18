# Research Group: subset-b-004359

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2_fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2_fw.h

## Purpose
`bnx2_fw.h` is a small firmware-support header for the older Broadcom/QLogic `bnx2` Ethernet driver. It defines static `struct cpu_reg` initializer tables for the on-chip microcontrollers used by the device firmware loader and reset paths. The file does not contain executable logic; it binds symbolic register constants from the bnx2 register definitions into per-processor register layouts consumed elsewhere by the driver.

## Important APIs, Types, and Data
- `cpu_reg_com` describes the Completion Processor register block: mode, halt/step values, state, GPR base, event mask, program counter, instruction, breakpoint, scratchpad base, and MIPS view base.
- `cpu_reg_cp` describes the Command Processor with the same `struct cpu_reg` fields mapped to `BNX2_CP_*` registers.
- `cpu_reg_rxp` describes the RX Processor register block.
- `cpu_reg_tpat` describes the TX Patch-up Processor register block.
- `cpu_reg_txp` describes the TX Processor register block.
- All tables use `.mips_view_base = 0x8000000`, so consumers can treat the firmware CPU memory window consistently across these processors.

## Control Flow
There is no local control flow. The driver code that halts, steps, clears state, reads/writes GPRs, loads firmware, or dumps microcontroller state selects one of these constant structures and performs MMIO against the addresses embedded here.

## State and Persistence Behavior
The constants are compile-time `static const` data. They do not mutate driver state and do not persist anything. The runtime state affected by their consumers is hardware state: firmware CPU mode/state registers, scratchpad memory, event masks, program counters, and instruction/breakpoint registers.

## Dependencies and Integration Points
- Depends on `struct cpu_reg` and the `BNX2_*` register macros being defined before inclusion.
- Integrates with the bnx2 firmware initialization and diagnostic paths that need a uniform description of the COM, CP, RXP, TPAT, and TXP processor register blocks.
- The register addresses must match the firmware image and the silicon generation expected by the bnx2 driver.

## Risks
- Incorrect register mappings can halt or program the wrong microcontroller block, causing device initialization failures or corrupting firmware execution.
- Since the file is pure static data, compile-time type checking is limited to field names and scalar values; semantic mistakes surface only during hardware bring-up or firmware diagnostics.
- Changes must be synchronized with the corresponding bnx2 register header and firmware loader code.

## Test Signals
- Driver probe/load succeeds on bnx2 hardware and firmware CPUs leave soft-halt/reset as expected.
- Firmware reload, reset, and diagnostic dump paths read coherent program counter/state values for each processor.
- Build coverage catches missing `struct cpu_reg` fields or renamed `BNX2_*` constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/Makefile

## Purpose
This Kbuild makefile declares the Broadcom/QLogic `bnx2x` 10-Gigabit Ethernet driver object composition. It controls which compilation units are linked into `bnx2x.o` for the kernel configuration and adds SR-IOV support objects only when `CONFIG_BNX2X_SRIOV` is enabled.

## Important APIs, Types, and Build Targets
- `obj-$(CONFIG_BNX2X) += bnx2x.o` builds the driver as built-in or module according to the kernel config symbol.
- `bnx2x-y` lists the always-included objects: main probe/control, link management, common fast/load logic, ethtool, stats, DCB, slowpath, and self-test support.
- `bnx2x-$(CONFIG_BNX2X_SRIOV)` conditionally adds `bnx2x_vfpf.o` and `bnx2x_sriov.o` for virtual function and PF/VF mailbox support.

## Control Flow
There is no runtime flow in this file. At build time, Kbuild expands the config-controlled variables and links the selected object files into the final driver object.

## State and Persistence Behavior
The file only affects build artifacts. It does not define runtime state, persistence, or module parameters directly. Its choices determine which code paths exist in the resulting kernel/module.

## Dependencies and Integration Points
- Depends on the kernel Kbuild object aggregation model.
- `bnx2x_cmn.o` supplies common load/unload, queue, RX/TX, NAPI, interrupt, feature, and PM helpers declared by `bnx2x_cmn.h`.
- `bnx2x_main.o` typically owns probe/remove/netdev registration and calls into the common code.
- Conditional SR-IOV objects must stay in sync with `#ifdef CONFIG_BNX2X_SRIOV` declarations in headers such as `bnx2x.h`, `bnx2x_cmn.h`, and `bnx2x_sriov.h`.

## Risks
- Omitting a required object causes unresolved symbols at link time or disabled runtime features.
- Adding an object unconditionally when it depends on config-gated headers can break builds for non-SR-IOV configurations.
- Moving common functionality between files requires updating this makefile and all declarations together.

## Test Signals
- `CONFIG_BNX2X=m` and `CONFIG_BNX2X=y` builds link successfully.
- Builds with `CONFIG_BNX2X_SRIOV=y` include PF/VF mailbox symbols; builds without it do not require SR-IOV objects.
- Module load smoke tests confirm all always-linked subsystems initialize through the expected object set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x.h

## Purpose
`bnx2x.h` is the central private header for the Broadcom/QLogic Everest `bnx2x` Ethernet driver. It defines the main driver state object, chip-family predicates, MMIO/shared-memory accessors, ring geometry, queue indexing, fast-path data structures, slow-path data structures, feature flags, multi-function mode helpers, and cross-file prototypes. Most implementation files in the driver include this header to share a single contract for device state and hardware programming.

## Important APIs, Types, and Data
- Version and config constants: `DRV_MODULE_VERSION`, `BNX2X_BC_VER`, `DRV_MODULE_NAME`, debug masks, and `enum bnx2x_int_mode`.
- MMIO/shared-memory helpers: `REG_RD/WR`, `REG_RD_IND/REG_WR_IND`, DMAE helper macros, `SHMEM_RD/WR`, `SHMEM2_RD/WR`, `MF_CFG_RD/WR`, and `DOORBELL_RELAXED`.
- Chip and function identity: `struct bnx2x_common` plus `CHIP_IS_E1/E1H/E2/E3`, `CHIP_REV_*`, `BP_PATH`, `BP_PORT`, `BP_FUNC`, `BP_VN`, and related firmware mailbox index macros.
- Fast-path rings and queues:
  - `struct sw_rx_bd`, `struct sw_tx_bd`, `struct sw_rx_page`, and `union db_prod` wrap host-side buffer metadata and doorbell producer state.
  - `struct bnx2x_fp_txdata` tracks one TX queue/COS ring, including descriptor ring DMA address, producer/consumer counters, CID, doorbell payload, and status-block consumer pointer.
  - `struct bnx2x_fastpath` tracks one RX/TX/NAPI context, status block shortcuts, RX BD/CQE/SGE rings, TPA/GRO state, queue identifiers, producers/consumers, and allocation pool.
- Aggregation and offload data: `struct bnx2x_agg_info`, `enum bnx2x_tpa_mode_t`, TPA/GRO sizing constants, SGE bit-vector macros, TX checksum/GSO `XMIT_*` flags, and ring transition macros such as `NEXT_TX_IDX`, `NEXT_RX_IDX`, and `NEXT_RCQ_IDX`.
- Slow path:
  - `struct bnx2x_slowpath` holds ramrod data buffers, DMAE commands, stats buffers, writeback data, and management firmware message payloads.
  - `struct bnx2x_sp_objs` groups MAC, VLAN, and queue slowpath objects.
  - `enum sp_rtnl_flag` and `enum bnx2x_iov_flag` define deferred service flags.
- Main persistent driver state: `struct bnx2x` contains fastpath arrays, netdev/pci handles, status blocks, slowpath rings, event rings, state flags, link state, multi-function config, CNIC/FCoE/iSCSI hooks, DMAE/statistics state, firmware image/init data, SR-IOV state, DCB/PTP state, VLAN registration, UDP tunnel ports, and firmware capability/version fields.
- Public prototypes export operations implemented across the driver: MAC/VLAN programming, function init, GPIO, DMAE, FLR cleanup, slowpath posting, coalescing, PHY/link helpers, PTP, NVRAM, and VLAN reconfiguration.

## Control Flow
The header does not implement the top-level control flow, but it defines the state machine and invariants used by the control flow:
- Driver lifecycle moves through `BNX2X_STATE_CLOSED`, opening phases, `BNX2X_STATE_OPEN`, closing phases, diagnostic, and error states.
- Queue loops (`for_each_eth_queue`, `for_each_rx_queue`, `for_each_tx_queue`, CNIC variants) encode which fastpath entries participate depending on FCoE/CNIC state and `NO_FCOE_FLAG`.
- Ring macros encode wraparound and next-page descriptor slots for TX, RX BD, RX CQE, and RX SGE rings.
- Chip predicates steer runtime branches for HC versus IGU interrupt blocks, E1x versus E2/E3 status block layouts, RSS/hash ownership, offload mode, and multi-function behavior.

## State and Persistence Behavior
`struct bnx2x` is the long-lived per-device state anchored from `netdev_priv()`. It persists while the PCI device is bound and stores:
- MMIO mappings, doorbell base, DMA-coherent slowpath/status/statistics/ring buffers, and firmware pointers.
- Runtime control state such as `state`, `flags`, `recovery_state`, `sp_state`, `sp_rtnl_state`, queue counts, interrupt mode flags, and link reporting cache.
- Management-firmware shared-memory metadata such as mailbox sequence, pulse sequence, multi-function config, driver capability flags, and OS driver state.
- Offload integrations for CNIC, FCoE, DCB, SR-IOV, PTP, RSS, VXLAN/Geneve, VLAN filters, MAC/VLAN credit pools, and statistics.
Hardware-persistent effects happen through macros that write registers, shared memory, doorbells, and firmware command areas; the header centralizes address calculation but leaves sequencing to implementation files.

## Dependencies and Integration Points
- Includes Linux PCI, netdevice, DMA, PTP, timestamping, and MDIO APIs.
- Includes generated/hardware-specific headers: `bnx2x_hsi.h`, `bnx2x_reg.h`, `bnx2x_fw_defs.h`, `bnx2x_mfw_req.h`, plus link, slowpath, DCB, stats, and VF/PF headers.
- Integrates with `../cnic_if.h` for storage offload clients.
- Provides the shared data contract consumed by `bnx2x_main.c`, `bnx2x_cmn.c`, `bnx2x_link.c`, `bnx2x_sp.c`, `bnx2x_stats.c`, `bnx2x_dcb.c`, `bnx2x_ethtool.c`, SR-IOV files, and self-tests.

## Risks
- The ring geometry macros are tightly coupled to hardware page sizes and descriptor formats. Incorrect counts or next-page handling can corrupt DMA rings.
- `struct bnx2x` is very large and cross-cutting; field changes can silently affect fast path cache locality, lifecycle cleanup, or config-gated builds.
- MMIO and shared-memory macros do no runtime bounds checking. Callers must enforce chip generation, function identity, and mailbox availability.
- Multi-function and storage-only helper predicates feed queue counts, bandwidth limits, link reporting, and feature restrictions; regressions can affect other PFs/VFs on the same device.
- Many state bits are shared between interrupt, NAPI, workqueue, rtnl, management firmware, and recovery paths, so ordering assumptions and locks are critical.

## Test Signals
- Compile coverage across `CONFIG_BNX2X`, `CONFIG_BNX2X_SRIOV`, `CONFIG_DCB`, PTP, and FCoE-related kernel options.
- Probe/open/close cycles on E1x, E2, and E3 devices validate chip predicates, status block layouts, queue counts, and ring geometry.
- RSS, multi-COS, FCoE/CNIC, SR-IOV, VLAN filtering, DCB, PTP, and UDP tunnel feature tests exercise the major state fields.
- Stress tests for MTU changes, feature toggles, reset/recovery, suspend/resume, and TX timeout show whether state transitions and cleanup remain coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.c

## Purpose
`bnx2x_cmn.c` implements the common runtime body of the `bnx2x` driver: fast-path RX/TX processing, NAPI polling, IRQ setup, queue sizing, queue memory allocation, NIC load/unload, CNIC/FCoE queue bring-up, link reporting, RSS setup, netdev feature changes, MTU changes, PM suspend/resume, and several hardware context/coalescing helpers. It is the bridge between netdev callbacks and the lower-level hardware, firmware, slowpath, and link-management modules.

## Important APIs, Types, and Functions
- Queue and NAPI setup:
  - `bnx2x_calc_num_queues()` clamps requested/default RSS queues and forces a single queue in kdump.
  - `bnx2x_set_num_queues()` computes Ethernet plus CNIC queue counts.
  - `bnx2x_set_real_num_queues()` publishes real TX/RX queue counts to netdev, accounting for FCoE.
  - `bnx2x_add_all_napi()`, `bnx2x_add_all_napi_cnic()`, enable/disable helpers, and `bnx2x_poll()` wire NAPI to fastpath rings.
- TX completion and transmit:
  - `bnx2x_tx_int()` consumes hardware TX completions, frees descriptors/SKBs via `bnx2x_free_tx_pkt()`, completes BQL accounting, and wakes stopped queues when descriptors become available.
  - `bnx2x_start_xmit()` maps SKB data/frags, builds start/parse/data BDs, handles checksum/TSO/tunnel offloads, rings the doorbell, and stops the queue when descriptor space drops below `MAX_DESC_PER_TX_PKT`.
  - Helper paths include `bnx2x_xmit_type()`, `bnx2x_pkt_req_lin()`, `bnx2x_tx_split()`, parse-BD checksum/GSO helpers, and `bnx2x_select_queue()`.
- RX receive and aggregation:
  - `bnx2x_rx_int()` consumes completed CQEs up to NAPI budget, handles slowpath ramrod CQEs, normal packets, errors, VLAN tags, RX checksum, RX hash, PTP timestamps, and TPA start/stop.
  - `bnx2x_tpa_start()` and `bnx2x_tpa_stop()` manage LRO/GRO aggregation bins and SGE fragments.
  - `bnx2x_alloc_rx_data()`, `bnx2x_alloc_rx_sge()`, `bnx2x_fill_frag_skb()`, `bnx2x_build_skb()`, and `bnx2x_gro_receive()` implement buffer allocation and GRO handoff.
- Interrupts:
  - `bnx2x_enable_msix()`, `bnx2x_enable_msi()`, `bnx2x_setup_irqs()`, `bnx2x_req_msix_irqs()`, `bnx2x_free_irq()`, and `bnx2x_msix_fp_int()` manage MSI-X/MSI/INTx selection and fastpath scheduling.
  - `bnx2x_netif_start()` and `bnx2x_netif_stop()` sequence NAPI and interrupt enable/disable.
- Load/unload:
  - `bnx2x_nic_load()` is the main open/load path. It initializes queue state, allocates memory, negotiates MCP load, initializes hardware/function objects, requests IRQs, sets queues/RSS/MAC/VLAN/RX mode/PTP/link/DCB, starts TX, starts timers, and optionally loads CNIC.
  - `bnx2x_nic_unload()` is the main close/unload path. It marks management state, stops VF/CNIC/TX/timers/stats, drains TX, closes VF or PF chip resources, disables interrupts/NAPI, squeezes objects, frees SKBs/rings/memory, updates MCP state, and handles parity recovery flags.
  - `bnx2x_load_cnic()` brings up CNIC/FCoE-related queues after base NIC load.
- Memory management:
  - `bnx2x_alloc_mem_bp()`/`bnx2x_free_mem_bp()` allocate long-lived arrays for fastpaths, slowpath objects, stats, TX queues, MSI-X table, and ILT.
  - `bnx2x_alloc_fp_mem_at()`/`bnx2x_free_fp_mem_at()` allocate and free per-queue status blocks, TX rings, RX rings, CQ rings, SGE rings, and initial RX buffers.
  - `bnx2x_alloc_fw_stats_mem()`/`bnx2x_free_fw_stats_mem()` manage the firmware statistics request/data DMA buffer.
- Link, features, and misc:
  - `bnx2x_link_report()`, `__bnx2x_link_report()`, `bnx2x_get_mf_speed()`, and PHY lock helpers report carrier and speed/duplex/flow-control state.
  - `bnx2x_rss()` and `bnx2x_init_rss()` program RSS configuration through PF slowpath or VF/PF mailbox.
  - `bnx2x_setup_tc()` and `__bnx2x_setup_tc()` configure traffic classes and priority-to-COS mapping.
  - `bnx2x_change_mac_addr()`, `bnx2x_change_mtu()`, `bnx2x_fix_features()`, `bnx2x_set_features()`, `bnx2x_tx_timeout()`, `bnx2x_suspend()`, and `bnx2x_resume()` implement netdev/PM-facing callbacks.
  - `bnx2x_set_ctx_validation()`, `bnx2x_update_coalesce_sb_index()`, `bnx2x_get_c2s_mapping()`, and `bnx2x_schedule_sp_rtnl()` provide shared hardware/context utilities.

## Control Flow
Open/load flow:
1. `bnx2x_nic_load()` sets opening state, resets link-report cache, prepares ILT for PFs, zeroes fastpaths while preserving NAPI/TPA allocations, sizes RX buffers, allocates base and per-FP memory, allocates firmware stats memory, and initializes VF state if needed.
2. It updates real netdev queues, sets initial TC mapping, adds/enables NAPI, marks PF load, asks MCP for a load code or uses `bnx2x_load_count` when there is no MCP, checks firmware compatibility, initializes function objects and hardware.
3. It initializes pre-IRQ state, requests interrupts, performs post-IRQ init, initializes slowpath objects and SR-IOV, starts the function, sends `LOAD_DONE`, configures coalescing, sets up leading and nondefault queues, initializes RSS, configures MAC/VLAN/RX mode/PTP/link/DCB, starts TX, starts the periodic timer, loads CNIC if enabled, waits for slowpath completion, and returns open.

Receive flow:
1. An MSI-X fastpath interrupt disables the status block interrupt and schedules NAPI.
2. `bnx2x_poll()` completes TX first for all COS queues, then calls `bnx2x_rx_int()` if RX work exists.
3. `bnx2x_rx_int()` reads CQEs with an `rmb()` after the completion marker, dispatches slowpath events, TPA start/stop, or normal RX. Normal RX either copies tiny jumbo-mode packets or replaces the RX buffer, builds an SKB, sets protocol/hash/checksum/VLAN/timestamp metadata, and submits through GRO.
4. Producers are written back to firmware with `bnx2x_update_rx_prod()`, which uses a write barrier before posting producer values.

Transmit flow:
1. `bnx2x_start_xmit()` selects the TX queue from `skb_get_queue_mapping()`, checks descriptor availability, determines checksum/GSO/tunnel type, linearizes packets that violate firmware fetch limits, maps the linear segment, and builds start plus parse BDs.
2. For E2/E3 tunnel or checksum offloads it fills E2 parse descriptors and optional second parse descriptors; for E1x it fills E1x parse descriptors. It maps fragments into data BDs, records total packet size, updates BQL, increments packet producer, issues write barriers, updates doorbell producer, writes the doorbell, and optionally stops the queue.
3. `bnx2x_tx_int()` later observes hardware consumer status, frees all BDs/SKBs for completed packets, updates consumers, and wakes the queue under TX lock when space returns.

Unload flow:
1. `bnx2x_nic_unload()` marks OS/MFW state disabled, handles recovery special cases, changes state away from open before disabling TX, notifies VFs and CNIC, stops TX and timers, saves stats, drains TX unless in recovery, and closes VF or PF chip resources.
2. It squeezes remaining slowpath objects, clears SP state, frees SKBs/SGEs/TPA pools/FP memory/CNIC memory/base memory, marks closed, updates management version, and sets/reset recovery gate flags based on parity attentions.

## State and Persistence Behavior
- Mutates long-lived `struct bnx2x` fields: `state`, queue counts, `port.pmf`, `nic_stopped`, `cnic_loaded`, `force_link_down`, `last_reported_link`, `fw_seq`, `fw_drv_pulse_wr_seq`, `rx_ring_size`, `fw_stats_*`, `sp_state`, `sp_rtnl_state`, `lin_cnt`, PTP state, and multi-function config.
- Maintains per-queue producers/consumers for TX packets/BDs, RX BDs/CQEs/SGEs, status block indices, NAPI state, and TPA aggregation bins.
- Allocates and frees DMA-coherent descriptor/status/statistics rings and maps/unmaps SKB/page data for device DMA.
- Persists state into hardware and management firmware via MMIO registers, doorbells, shared-memory driver flags, OS driver state, load/unload commands, pulse mailbox, coalescing memory, RSS/classification ramrods, and link/DCB configuration.
- Uses memory barriers around hardware-owned rings and status blocks: `smp_rmb()` after TX status reads, `rmb()` after RX CQE completion markers/status-block reads, and `wmb()` before posting RX/TX producers and doorbells.

## Dependencies and Integration Points
- Linux networking: netdev queues, NAPI, GRO, VLAN acceleration, checksum offload, GSO/TSO, BQL, traffic classes, carrier state, feature negotiation, MTU changes, TX timeout, and PM hooks.
- Linux PCI/DMA/IRQ APIs: coherent allocations, streaming DMA mapping, MSI-X/MSI/INTx requests, power states, and config space.
- Driver internals: `bnx2x.h`, `bnx2x_cmn.h`, `bnx2x_init.h`, `bnx2x_sp.h`, link/PHY functions, stats, DCB, SR-IOV/VF-PF mailbox, CNIC interface, PTP helpers, and management firmware commands.
- Hardware firmware: status blocks, slowpath ramrods, RSS configuration, function state transitions, MCP load/unload protocol, shared memory, DCBX, AFEX, FCoE/iSCSI queues, and coalescing RAM.

## Risks
- Ordering bugs around status blocks, CQE markers, producer writes, or doorbells can cause missed interrupts, stale packet metadata, descriptor corruption, or permanent TX queue stalls.
- Error unwind in `bnx2x_nic_load()` spans many partially initialized subsystems; missing one cleanup step can leak DMA memory, leave NAPI registered, or keep MCP state inconsistent.
- TPA/GRO aggregation state depends on correct SGE replacement and page reference handling; allocation failures and DMA mapping failures must preserve ring consistency.
- TX offload descriptor construction is chip-generation dependent and handles VLANs, tunnels, IPv4/IPv6, TCP/UDP, GSO, and timestamping. Small mistakes can produce bad packets or firmware fetch violations.
- Queue shrinking after allocation failures moves fastpath/TX structures; bugs can leave stale pointers or mismatched queue indices.
- Multi-function, SR-IOV, CNIC/FCoE, storage-only personality, and recovery modes all change queue counts and cleanup behavior, increasing cross-feature regression risk.

## Test Signals
- Build tests across SR-IOV, DCB, PTP, FCoE/CNIC, and non-SR-IOV configs.
- Probe/open/close/reload cycles, including forced allocation failures where possible, validate load error paths and queue shrinking.
- RX/TX traffic under checksum, TSO/GSO, VLAN, VXLAN/Geneve encapsulation, jumbo MTU, LRO/GRO_HW, RSS, and multi-COS modes.
- Interrupt mode coverage for MSI-X multi-vector, single MSI-X fallback, MSI, and INTx.
- Stress tests for NAPI budget exhaustion, TX queue stop/wake, MTU/feature changes while running, suspend/resume, TX timeout recovery, parity recovery, and CNIC/FCoE load/unload.
- Hardware counters and netdev stats should show no RX checksum spikes, TX timeouts, DMA mapping leaks, or persistent stopped queues during sustained traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.h

## Purpose
`bnx2x_cmn.h` declares the common `bnx2x` driver API and defines shared inline helpers used by the common runtime, main driver, slowpath, link, ethtool, and optional offload paths. It is the public internal interface for NIC load/unload, queue setup, interrupts, memory allocation, netdev callbacks, CNIC integration, RSS, link reporting, filtering, hardware locks, and ring/status-block primitives.

## Important APIs, Types, and Functions
- Allocation macros:
  - `BNX2X_PCI_ALLOC`, `BNX2X_PCI_FALLOC`, and `BNX2X_PCI_FREE` wrap coherent DMA allocation/free for buffers addressed by firmware/hardware.
  - `BNX2X_FREE` frees normal kernel heap pointers and clears them.
- Lifecycle and hardware declarations:
  - `bnx2x_nic_load()`, `bnx2x_nic_unload()`, `bnx2x_chip_cleanup()`, `bnx2x_pre_irq_nic_init()`, `bnx2x_post_irq_nic_init()`, `bnx2x_alloc_mem()`, `bnx2x_free_mem()`, and CNIC variants.
  - MCP and firmware helpers such as `bnx2x_send_unload_req()`, `bnx2x_send_unload_done()`, `bnx2x_fw_command()`, `bnx2x_drv_pulse()`, and `bnx2x_compare_fw_ver()` through related headers/C file use.
- Queue and netdev operations:
  - `bnx2x_setup_queue()`, `bnx2x_setup_leading()`, `bnx2x_set_num_queues()`, `bnx2x_start_xmit()`, `bnx2x_select_queue()`, `bnx2x_tx_int()`, `bnx2x_change_mtu()`, `bnx2x_set_features()`, `bnx2x_tx_timeout()`, `bnx2x_setup_tc()`, and `__bnx2x_setup_tc()`.
- Link and filtering:
  - `bnx2x_initial_phy_init()`, `bnx2x_link_set()`, `bnx2x_force_link_reset()`, `bnx2x_link_test()`, `bnx2x__link_status_update()`, `bnx2x_link_report()`, `bnx2x_get_mf_speed()`, `bnx2x_set_eth_mac()`, `bnx2x_set_rx_mode_inner()`, and VLAN/MAC cleanup helpers.
- Interrupt/status-block inline helpers:
  - `bnx2x_update_rx_prod()` posts RX BD/CQE/SGE producers after a write barrier.
  - `bnx2x_igu_ack_sb_gen()`, `bnx2x_hc_ack_sb()`, `bnx2x_ack_sb()`, `bnx2x_hc_ack_int()`, `bnx2x_igu_ack_int()`, and `bnx2x_ack_int()` abstract HC versus IGU interrupt blocks.
  - `bnx2x_update_fpsb_idx()`, `bnx2x_has_tx_work_unload()`, `bnx2x_tx_avail()`, `bnx2x_tx_queue_has_work()`, `bnx2x_has_tx_work()`, and `bnx2x_has_rx_work()` read ring/status state.
- Ring and object inline helpers:
  - `bnx2x_free_rx_sge()`, NAPI deletion helpers, MSI disable, SGE mask initialization, `bnx2x_reuse_rx_data()`, `bnx2x_set_next_page_rx_bd()`, `bnx2x_free_rx_sge_range()`, and RX memory pool cleanup.
  - `bnx2x_func_start()`, `bnx2x_set_fw_mac_addr()`, `bnx2x_init_vlan_mac_fp_objs()`, `bnx2x_init_bp_objs()`, `bnx2x_init_txdata()`, CNIC ID helpers, `bnx2x_clean_tx_queue()`, `bnx2x_wait_sp_comp()`, `bnx2x_mtu_allows_gro()`, and management flag/link sync helpers.

## Control Flow
This header shapes several key flows:
- RX producer flow: callers replenish RX rings and call `bnx2x_update_rx_prod()`, which writes BD/CQE/SGE producers to USTORM memory only after descriptors and buffers are visible.
- Interrupt acknowledgement flow: callers use `bnx2x_ack_sb()` and `bnx2x_ack_int()` without duplicating HC/IGU differences; the helper derives IGU segment selection for backward-compatible versus normal interrupt modes.
- Queue work detection: NAPI and unload paths use `bnx2x_has_rx_work()`, `bnx2x_tx_queue_has_work()`, and `bnx2x_has_tx_work_unload()` to decide whether to poll, drain, or wait.
- Function start flow: `bnx2x_func_start()` prepares a slowpath function-start command, sets multi-function, BD-mode, network COS, tunnel port, inner RSS, and class-fail parameters, then calls the function state machine.
- Object initialization flow: `bnx2x_init_bp_objs()` and `bnx2x_init_vlan_mac_fp_objs()` connect slowpath objects to DMA ramrod buffers, pending bits, function IDs, client IDs, and credit pools.

## State and Persistence Behavior
- The allocation macros mutate pointer and DMA-address variables by clearing them on free and logging physical/virtual addresses when debug masks enable it.
- Inline helpers mutate fastpath ring producers/consumers, SGE masks, RX buffer metadata, status block acknowledgements, function start ramrod data, slowpath object state, credit pools, and management firmware shared-memory driver flags.
- Hardware-visible persistence occurs through MMIO writes to USTORM producer memory, HC/IGU acknowledgement registers, VLAN ethertype registers in BD mode, and shared-memory driver flags.
- `bnx2x_wait_sp_comp()` observes `bp->sp_state` under `netif_addr_lock_bh()` with memory barriers and waits for slowpath pending bits to clear, creating a synchronization point for filtering/object commands.

## Dependencies and Integration Points
- Includes Linux types, PCI, netdevice, etherdevice, and IRQ headers.
- Includes `bnx2x.h` for the primary state contract and `bnx2x_sriov.h` for SR-IOV declarations.
- Exports common functions implemented in `bnx2x_cmn.c` and functions implemented in other bnx2x compilation units (`bnx2x_main.c`, link, slowpath, stats, DCB, SR-IOV, ethtool, and self-test files).
- Integrates with netdev callbacks, CNIC offload control, firmware ramrods, management firmware shared memory, interrupt controller abstractions, and hardware ring memory.

## Risks
- The allocation/free macros assume the local variable name `bp` exists; using them outside that convention would break compilation or free through the wrong device.
- Ring helpers rely on exact producer/consumer arithmetic and next-page descriptor layout from `bnx2x.h`; any mismatch can corrupt hardware rings.
- Interrupt acknowledgement helpers must choose the correct HC/IGU path and segment, or interrupts can be lost or repeatedly asserted.
- `bnx2x_wait_sp_comp()` can time out if pending bits are not cleared by completion handling; callers must ensure interrupts/completions are still serviced while waiting.
- Inline object initialization encodes chip and multi-function policy; changes can affect MAC/VLAN/RSS credit accounting across PFs/VFs.

## Test Signals
- Compile coverage catches declaration drift between this header and implementation files.
- Runtime tests should verify RX producer updates, NAPI interrupt re-enable, TX drain on unload, function start ramrods, RSS setup, MAC/VLAN filtering, and CNIC/FCoE queue initialization.
- Interrupt-mode tests across HC/IGU and MSI-X/MSI/INTx validate acknowledgement helpers.
- Slowpath stress, including multicast/UC list updates and feature reloads, should not trigger `bnx2x_wait_sp_comp()` timeouts.
- Memory fault injection around coherent allocation and RX/TX buffer allocation should unwind without leaks or stale DMA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_cmn.h -->

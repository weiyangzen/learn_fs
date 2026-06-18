# Research: subset-b-004460

## Files

- `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_nvm.c`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_prototype.h`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ptp.c`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_register.h`
- `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_trace.h`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_nvm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_nvm.c

## Purpose

`i40e_nvm.c` implements i40e non-volatile memory and Shadow RAM access for the Intel 40GbE driver. It initializes NVM metadata, arbitrates firmware-owned NVM resources through AdminQ, reads and writes Shadow RAM either through `GLNVM_SRCTL` or AdminQ, calculates and validates the software checksum, and exposes the NVM update command state machine used by management/update paths. The file treats "NVM" as FLASH mapped through Shadow RAM and centralizes the locking and firmware completion behavior required to avoid corrupting persistent adapter configuration.

## Important APIs, Types, and Functions

- `i40e_init_nvm()` reads `I40E_GLNVM_GENS` to determine Shadow RAM size and `I40E_GLNVM_FLA` to distinguish normal from blank programming mode. Blank mode sets `hw->nvm.blank_nvm_mode` and returns `-EIO`.
- `i40e_acquire_nvm()` and `i40e_release_nvm()` wrap `i40e_aq_request_resource()` and `i40e_aq_release_resource()` for `I40E_NVM_RESOURCE_ID`, including wait/retry logic based on `I40E_GLVFGEN_TIMER` and firmware-provided timeout.
- `i40e_read_nvm_word()`, `i40e_read_nvm_buffer()`, and `i40e_read_nvm_module_data()` are the exported read APIs. They select AdminQ or SRCTL access based on `I40E_HW_CAP_AQ_SRCTL_ACCESS_ENABLE` and acquire a read lock when `I40E_HW_CAP_NVM_READ_REQUIRES_LOCK` is set.
- `i40e_update_nvm_checksum()` and `i40e_validate_nvm_checksum()` use `i40e_calc_nvm_checksum()` to maintain the Shadow RAM checksum word while skipping VPD and PCIe alternate auto-load regions.
- `i40e_nvmupd_command()` is the public dispatcher for update commands described by `struct i40e_nvm_access`; it delegates to `i40e_nvmupd_state_init()`, `i40e_nvmupd_state_reading()`, and `i40e_nvmupd_state_writing()`.
- `i40e_nvmupd_check_wait_event()` and `i40e_nvmupd_clear_wait_state()` bridge asynchronous AdminQ events back into the NVM update state machine.

## Control Flow

Initialization first calculates `hw->nvm.sr_size` from a register-encoded power-of-two KB value and rejects unsupported blank NVM mode. Most normal reads enter through `i40e_read_nvm_word()` or `i40e_read_nvm_buffer()`: optional NVM resource acquisition, dispatch to an internal caller-locking helper, then release. SRCTL reads poll the done bit, write address plus start, poll again, and extract read data. AdminQ reads validate that a single command does not exceed one sector or cross a sector boundary, then issue `i40e_aq_read_nvm()` with byte offsets.

Buffer AdminQ reads split the caller request into sector-limited transactions and only set `last_command` on the final chunk. Module-data reads first resolve a module pointer, reject invalid or outside-Shadow-RAM pointers, then read a relative pointer and fetch the final data buffer.

Checksum flow allocates one sector-sized virtual buffer, reads VPD and PCIe alternate module pointers, iterates every Shadow RAM word, reloads a sector buffer at each sector boundary, skips the checksum word plus the two variable regions, and returns `I40E_SR_SW_CHECKSUM_BASE - sum`. Validation holds the NVM read lock across checksum calculation and checksum-word read.

NVM update flow starts by validating `cmd->command`, transaction bits, module pointer bits, and data size. Single-transaction reads/writes acquire and release around one command. Multi-command read starts in `INIT`, acquires NVM, transitions to `READING`, continues with `READ_CON`, and releases on `READ_LCB`. Multi-command write starts with `WRITE_SNT`, waits for an AdminQ completion, transitions into `WRITING`, and continues with `WRITE_CON`, `WRITE_LCB`, or checksum commands. Wait states reject most commands with `-EBUSY`; an offset of `0xffff` cancels/clears a wait. AdminQ execute commands optionally stash the expected follow-up opcode in `hw->nvm_wait_opcode`.

## State and Persistence Behavior

The persistent hardware state is the adapter NVM/FLASH content and Shadow RAM checksum. In-memory state lives primarily in `struct i40e_hw`: `hw->nvm.sr_size`, `timeout`, `blank_nvm_mode`, `hw_semaphore_timeout`, AdminQ write-back descriptors, NVM update state, wait opcode, release-on-done flag, event descriptor, and temporary NVM buffer. The NVM semaphore is firmware-global and can be held across multi-command transactions; failure to release it blocks other PFs and management agents. The update state machine is intentionally sticky across calls so user space can stream update chunks and poll completion status.

## Dependencies and Integration Points

This file depends on `i40e_prototype.h`, `i40e_alloc.h`, `i40e_type.h` definitions, AdminQ commands from common i40e code, register constants from `i40e_register.h`, Linux delay helpers, bitfield extraction, and driver debug logging. It integrates with firmware through AdminQ NVM read/update/erase/resource commands and with interrupt/AdminQ event handling through `i40e_nvmupd_check_wait_event()`. Other i40e code calls the exported NVM APIs for probe-time identity/configuration reads, flash update, checksum validation, and management-tool NVM update operations.

## Risks

- NVM update correctness depends on exact state transitions and AdminQ event delivery. Missing `i40e_nvmupd_check_wait_event()` calls can leave the driver in wait state or keep the NVM semaphore held.
- `i40e_nvmupd_get_aq_result()` assumes `hw->nvm_buff.va` is valid if a data remainder exists. Callers must only request result bytes matching prior AdminQ execution.
- The read/write helpers log but do not always immediately return distinct `-EINVAL` for sector/limit violations inside the low-level AdminQ helper; callers see the initialized `-EIO`.
- Multi-write retry on firmware `EBUSY` relies on `hw->nvm.hw_semaphore_timeout` and one retry. Timer wrap or stale semaphore timeout would affect recovery.
- Checksum calculation trusts module pointers enough to define skipped windows. Corrupt pointers can cause incorrect skip coverage even though reads themselves are bounded by Shadow RAM size.
- Direct SRCTL path has no outer semaphore in `i40e_read_nvm_buffer()` unless AdminQ access is enabled; this matches capability expectations but is sensitive to hardware generation.

## Test Signals

Useful validation includes successful probe with NVM init in normal mode, `ethtool -e` or equivalent Shadow RAM reads across sector boundaries, checksum validate/update on known-good adapters, firmware flash update flows covering single and multi-command read/write/checksum transactions, AdminQ event timeout/cancel paths, and concurrent PF/resource acquisition contention. Kernel logs with `I40E_DEBUG_NVM` enabled should show no stuck `I40E_NVMUPD_STATE_*_WAIT`, no repeated semaphore timeout, and no checksum mismatch after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_prototype.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_prototype.h

## Purpose

`i40e_prototype.h` is the shared declaration surface for i40e common code. It collects function prototypes that are needed before or outside the standard operations structures, especially AdminQ setup, AdminQ command wrappers, switch/VSI/filter/PHY/DCB/NVM/DDP helpers, hardware reset/common initialization helpers, and firmware/API version predicates. It is a central coupling point between implementation files such as `i40e_common.c`, `i40e_adminq.c`, `i40e_nvm.c`, DDP/profile code, VF/virtchnl handling, and higher-level PF driver code.

## Important APIs, Types, and Functions

- AdminQ lifecycle and command send path: `i40e_init_adminq()`, `i40e_shutdown_adminq()`, `i40e_clean_arq_element()`, `i40e_asq_send_command()`, `i40e_asq_send_command_atomic()`, and `_v2()` with explicit AQ status reporting.
- Firmware/control AdminQ helpers: firmware version, register debug read/write, PHY capabilities/config, link restart/info, driver version send, default VSI, switch config, resource request/release, LLDP/DCB, UDP tunnels, MAC address programming, and port TX suspend/resume.
- VSI/filter/switching helpers: add/update VSI, promiscuous mode variants, VLAN scoped promiscuous controls, VEB operations, MAC/VLAN add/remove v1/v2, cloud filters, control packet filters, and flow-control drop filter helpers.
- NVM surface: `i40e_init_nvm()`, `i40e_acquire_nvm()`, `i40e_release_nvm()`, read buffer/word/module APIs, checksum update/validate, NVM update command dispatch, and wait event clearing.
- Common hardware helpers: shared code init, PF reset, hardware clear, PXE mode clear, link status/update, MAC/PBA reads, PCI config data, queue preconfiguration, filter control, RX control register access, PHY register clause 22/45 access, DDP/profile write/rollback/flash.
- Inline helpers: `i40e_virtchnl_link_speed()` maps `enum i40e_aq_link_speed` to `enum virtchnl_link_speed`; firmware/AdminQ API version helpers compare `hw->aq.*` version fields.

## Control Flow

The header has no runtime control flow beyond inline predicates and link-speed conversion. Its functional role is compile-time orchestration: C files include it to share common entry points without circular dependencies. The inline link-speed conversion uses a switch that returns a virtchnl speed for recognized AdminQ speeds and `VIRTCHNL_LINK_SPEED_UNKNOWN` otherwise. Version helpers use straightforward major/minor comparisons and negate greater-or-equal checks for less-than.

## State and Persistence Behavior

The header itself persists no state, but most prototypes mutate or query `struct i40e_hw`, AdminQ rings, firmware state, switch/VSI state, PHY state, NVM/FLASH, DDP profiles, and adapter registers. Because this declaration surface is broad, signature stability is important: changing parameter ownership, endianness, length units, or status conventions affects many implementation files. The inline helpers read `hw->aq.api_maj_ver`, `api_min_ver`, `fw_maj_ver`, and `fw_min_ver`, so those fields must be initialized before version-gated logic uses them.

## Dependencies and Integration Points

The file includes Linux ethtool declarations, virtchnl definitions from `linux/avf/virtchnl.h`, `i40e_debug.h`, and `i40e_type.h`. It exposes i40e common code to PF driver, VF compatibility paths, AdminQ implementation, NVM update code, DCB/LLDP handling, flow director/filter logic, PHY access, DDP package loading, and ethtool flash paths. It also ties i40e link-speed representation to the virtchnl ABI used when reporting link information to virtual functions.

## Risks

- As a shared header, it can hide large blast radius. A prototype change can silently require updates in several subsystems and out-of-tree users.
- Many AdminQ APIs take raw buffers and lengths. Mismatched byte/word units, endian handling, or lifetime assumptions are not enforced by this header.
- Several operations expose firmware or persistent hardware mutation, especially NVM, PHY, DDP, switch, and MAC/VLAN helpers. Callers must satisfy locking and reset-state preconditions documented in implementation files rather than here.
- Inline version comparisons assume initialized version fields; use before AdminQ discovery could gate features incorrectly.
- The `i40e_virtchnl_link_speed()` mapping must stay aligned with both AdminQ enum values and virtchnl ABI additions.

## Test Signals

Build coverage is the primary signal for this header: all i40e compilation units should compile without prototype drift. Runtime signals include successful AdminQ init/shutdown, link reporting to VFs at every supported speed, firmware/API version-gated features taking expected branches, NVM update paths linking to `i40e_nvm.c`, and DDP/ethtool flash paths resolving declared helpers. Static analysis should focus on raw buffer length handling and mismatched status-code conventions across implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_prototype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ptp.c

## Purpose

`i40e_ptp.c` implements IEEE 1588/PTP hardware timestamp support for i40e devices. It registers the adapter PHC with Linux PTP, reads/writes and adjusts the hardware clock, configures hardware timestamp filters for netdev timestamping, handles Tx/Rx timestamp extraction and watchdog cleanup, configures external timestamp/PPS/perout pins on supported 25G devices, and preserves PTP time across device resets.

## Important APIs, Types, and Functions

- Clock operations registered in `ptp_clock_info`: `i40e_ptp_adjfine()`, `i40e_ptp_adjtime()`, `i40e_ptp_gettimex()`, and `i40e_ptp_settime()`.
- Netdev hwtstamp entry points: `i40e_ptp_hwtstamp_get()` and `i40e_ptp_hwtstamp_set()`.
- Timestamp data path helpers: `i40e_ptp_tx_hwtstamp()`, `i40e_ptp_rx_hwtstamp()`, `i40e_ptp_tx_hang()`, `i40e_ptp_rx_hang()`, and `i40e_ptp_get_rx_events()`.
- Clock lifecycle: `i40e_ptp_init()`, `i40e_ptp_stop()`, `i40e_ptp_set_increment()`, `i40e_ptp_save_hw_time()`, and `i40e_ptp_restore_hw_time()`.
- Pin support: `enum i40e_ptp_pin`, `enum i40e_ptp_gpio_pin_state`, `struct i40e_ptp_pins_settings`, `i40e_ptp_alloc_pins()`, `i40e_ptp_free_pins()`, `i40e_ptp_set_pins()`, and `i40e_ptp_feature_enable()`.
- Constants define the base increment and link-speed multipliers: 40G/25G/no link use 1.6 ns, 10G/5G use 3.2 ns, 1G uses 32 ns, and 100M disables PHC progression.

## Control Flow

Initialization starts in `i40e_ptp_init()`. The driver reads `PRTTSYN_CTL0.PF_ID` and only enables PTP on the PF assigned to the port timesync block. It initializes locks, creates or reuses a PHC through `i40e_ptp_create_clock()`, enables timesync bits in `PRTTSYN_CTL0/CTL1`, programs the link-speed-dependent increment, reapplies saved hwtstamp configuration, restores hardware time using the saved time plus monotonic reset delta, and configures the 1PPS signal.

HWTSTAMP setup flows through `i40e_ptp_hwtstamp_set()` into `i40e_ptp_set_timestamp_mode()`. That function configures external trigger behavior, enables event interrupts, initializes EXTS work, validates Tx type, broadens supported Rx filters where hardware cannot match exactly, clears latched timestamp registers, toggles Tx timestamp interrupts, and updates `PRTTSYN_CTL1` message type and UDP recognition bits. `i40e_ptp_hwtstamp_get()` returns the shadow `pf->tstamp_config`.

PHC reads latch low then high time registers and optionally capture system pre/post timestamps. Writes program low then high because hardware updates on high write. Small time adjustments use `I40E_PRTTSYN_ADJ`; large adjustments read, add a `timespec64` delta, write full time, and reprogram 1PPS. Frequency adjustment recalculates the increment from `I40E_PTP_40GB_INCVAL * pf->ptp_adj_mult` and `adjust_by_scaled_ppm()`.

Tx timestamp flow uses `__I40E_PTP_TX_IN_PROGRESS` as a bit lock and `pf->ptp_tx_skb` as the pending packet. On interrupt, `i40e_ptp_tx_hwtstamp()` reads `TXTIME_L/H`, converts ns to `skb_shared_hwtstamps`, clears the bit before notifying the stack, and frees the skb. `i40e_ptp_tx_hang()` frees a stale skb after roughly one second. Rx timestamp flow reads status, verifies the descriptor-provided latch index is set, clears the tracked latch flag, reads `RXTIME_L/H`, and stores the converted timestamp on the skb. `i40e_ptp_rx_hang()` clears latches that have remained set for over one second.

Pin flow is limited to a specific 25G SFP28 subsystem and normally PF0. PTP core pin requests are translated into internal pin states, checked against an allowed pin/LED state table, written to GPIO control registers, and followed by timing-event reset.

## State and Persistence Behavior

The file maintains `pf->ptp_clock`, `pf->ptp_caps`, `pf->tstamp_config`, `pf->ptp_tx`, `pf->ptp_rx`, pending Tx skb state, latch event flags/timestamps, timestamp timeout counters, pin settings, and reset-time snapshots. Hardware state includes PRTTSYN time, increment, adjust, Tx/Rx latch registers, external event registers, interrupt enables, GPIO/LED routing, and PF ownership in `PRTTSYN_CTL0`. Across resets, `i40e_ptp_save_hw_time()` snapshots PHC time and monotonic start; `i40e_ptp_restore_hw_time()` adds elapsed monotonic time before restoring registers.

## Dependencies and Integration Points

The implementation depends on Linux PTP, net timestamping, sk_buff timestamp APIs, workqueues, locks, jiffies, `ptp_classify.h`, `posix-clock.h`, i40e PF/VSI structures, i40e device IDs, register macros, and AdminQ link info. It integrates with the netdev hwtstamp ioctl/netlink path, Tx/Rx interrupt and clean paths, periodic service/watchdog tasks, reset/suspend/resume handling, and platform-specific GPIO pins. It also uses `I40E_HW_CAP_PTP_L4` to decide whether Layer 4 PTP filters can be enabled.

## Risks

- Hardware timestamp latches are scarce and can block future timestamps if not cleared. The watchdogs mitigate this but dropped frames or missed interrupts can still lose timestamps.
- Tx timestamp state relies on correct bit-lock ordering around `pf->ptp_tx_skb`; premature notification before clearing the bit could cause timestamp request races, which the code explicitly avoids.
- PTP register access must be serialized with `tmreg_lock` for time operations and `ptp_rx_lock` for Rx latch state. Missing those locks in future changes would risk inconsistent time or latch accounting.
- `i40e_ptp_set_timestamp_mode()` broadens Rx filters. User space must inspect the returned config to see the effective mode.
- 100 Mbps link sets increment multiplier to zero and warns once, effectively stopping the PHC.
- Pin configuration depends on a hard-coded allowed state table and PF0 ownership. Unsupported combinations return errors or no-op on non-PF0 paths.
- `i40e_ptp_set_timestamp_mode()` contains `regval &= 0`, intentionally clearing AUX bits before setting event level; future edits should treat it as full reinitialization, not a masked update.

## Test Signals

Validation should cover PHC registration and removal, `phc2sys`/`testptp` get/set/adjfine/adjtime operations, hwtstamp get/set with supported and unsupported filters, Tx and Rx timestamp delivery under traffic, watchdog counters for stale Tx/Rx timestamp latches, link-speed changes updating PHC rate, reset preserving PHC time within expected drift, PF ownership rejection on non-owning PFs, and pin/perout/extts/PPS behavior on the supported 25G PTP-pin device. Kernel logs should show PHC enabled/removed and no repeated timestamp hang warnings during normal PTP traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_register.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_register.h

## Purpose

`i40e_register.h` defines i40e memory-mapped register offsets, index formulas, bit shifts, and masks used by the PF driver and shared code. It is the hardware address map for AdminQ rings, DCB, firmware/reset status, GPIO/MDIO, HMC, interrupts, queue control, NVM/Shadow RAM, PCI capability/configuration, energy-efficient Ethernet, packet filtering/RSS/Flow Director, statistics, PTP/timesync, malicious-driver detection, virtualization allocation, wake/power management, and X722-specific redefinitions.

## Important APIs, Types, and Macros

- `I40E_MASK(mask, shift)` creates 32-bit masks and underpins nearly every field definition.
- AdminQ registers include `I40E_PF_ATQ*`, `I40E_PF_ARQ*`, queue head/tail/base/length fields, enable/overflow/critical bits, and global ATQ critical bits.
- Global/port reset and firmware status include `I40E_GL_FWSTS`, recovery mode masks for XL710/X722, `I40E_GLGEN_RSTAT`, `I40E_GLGEN_RSTCTL`, `I40E_GLGEN_RTRIG`, `I40E_PFGEN_CTRL`, and VF reset status/triggers.
- GPIO/MDIO support includes `I40E_GLGEN_GPIO_CTL()`, GPIO set controls, MDIO/I2C select, MSCA/MSRWD fields, and pin function masks used by PTP pin code.
- Interrupt support includes PF/VF dynamic control, ICR0/ICR0_ENA cause bits, queue interrupt cause controls, linked-list registers, ITR registers, and timesync/adminq/reset/malicious detect bits.
- LAN queue and virtualization mapping include QRX/QTX enable/tail/head/control, PF/VSI/VF queue allocation and mapping tables.
- NVM registers include `I40E_GLNVM_FLA`, `I40E_GLNVM_GENS`, `I40E_GLNVM_SRCTL`, `I40E_GLNVM_SRDATA`, and `I40E_GLNVM_ULD`.
- PTP registers include `I40E_PRTTSYN_CTL0/1`, increment, time, adjust, Tx/Rx timestamp, event, auxiliary, target, and clock-output registers.
- Statistics registers cover global port, switch, VSI, and VEB traffic counters with high/low 32-bit halves.

## Control Flow

There is no executable control flow. The macros encode address arithmetic and field extraction constants for callers using `rd32()`, `wr32()`, `FIELD_GET()`, and bit operations. Indexed macros such as `I40E_QRX_ENA(_Q)`, `I40E_PFINT_DYN_CTLN(_INTPF)`, `I40E_GLV_*(_i)`, or `I40E_PRTTSYN_RXTIME_H(_i)` define how software walks hardware tables. Reset comments (`POR`, `CORER`, `GLOBR`, `PFR`, `VFR`, `EMPR`, etc.) document which hardware reset domains affect each register and guide reset-time reprogramming.

## State and Persistence Behavior

The header itself holds no state, but every macro refers to persistent or semi-persistent hardware state. Some registers reset only on power-on or global reset, while others reset on PF, VF, core, or EMP reset. This distinction affects driver persistence: PTP configuration must be restored after resets, NVM registers expose flash-backed Shadow RAM state, queue registers define live DMA state, interrupt masks define event delivery, and statistics registers accumulate hardware counters until cleared by reset or read/write semantics. Duplicate/redefined entries near the end for X722 and selected NVM/filter registers indicate family-specific compatibility pressure.

## Dependencies and Integration Points

All low-level i40e implementation files depend on this header either directly or through `i40e_type.h`/common includes. The NVM file uses `GLNVM_*` and the global timer. The PTP file uses `PRTTSYN_*`, `PFINT_ICR0_ENA_TIMESYNC`, and GPIO constants. AdminQ code uses PF AQ registers. Interrupt setup uses PF/VF INT and QINT registers. Queue setup/teardown uses QRX/QTX and LAN mapping registers. Statistics collection uses GLPRT/GLSW/GLV/GLVEBTC counters. Reset and error handling use firmware status, malicious detect, and reset registers.

## Risks

- Register macros are trusted constants. A wrong offset, index stride, mask width, or reset-domain assumption can cause silent hardware misprogramming.
- `I40E_MASK` is 32-bit. It is suitable for these register fields but should not be reused for wider values without care.
- Indexed macros rely on callers enforcing documented index ranges in comments. The macro itself does not bound-check queue, VSI, VF, port, or counter indices.
- Some macro names are duplicated or redefined near the end (`I40E_GLNVM_FLA`, `I40E_GLNVM_ULD`, `I40E_PRTQF_FD_INSET`). This can be intentional for family compatibility, but future edits risk compiler redefinition warnings or inconsistent values.
- The header's breadth means unrelated driver areas can be affected by a single change. Register edits should be reviewed against hardware specifications and existing call sites.

## Test Signals

Tests are mostly hardware and integration signals: AdminQ initializes and processes commands, resets complete, interrupts fire and are masked/unmasked correctly, queues enable/disable and pass traffic, NVM Shadow RAM reads work, PTP timestamps progress and latch, GPIO pin settings affect supported boards, statistics counters update, VFs receive mapped queues/interrupts, and malicious detect/error registers report sane values under fault injection. Build logs should be checked for macro redefinition warnings, and static review should compare changed offsets/masks to the hardware datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_trace.h

## Purpose

`i40e_trace.h` defines Linux ftrace/tracepoint instrumentation for i40e. It provides wrapper macros so shared code can call tracepoints by logical name, then declares trace events for NAPI polling, Tx cleanup, Rx cleanup, and transmit attempts/drops. The header follows kernel tracepoint conventions for loadable modules by using a special include guard and `TRACE_INCLUDE_FILE`/`TRACE_INCLUDE_PATH` before including `trace/define_trace.h`.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM i40e` names the trace subsystem.
- `i40e_trace(trace_name, args...)` expands to `trace_i40e_<trace_name>(args...)`.
- `i40e_trace_enabled(trace_name)` expands to the generated enabled predicate for a tracepoint.
- `TRACE_EVENT(i40e_napi_poll)` records NAPI budget, per-ring budget, Rx/Tx cleaned counts, completion booleans, interrupt number, current CPU, q-vector name, netdev name, and IRQ affinity mask.
- `DECLARE_EVENT_CLASS(i40e_tx_template)` is reused by `i40e_clean_tx_irq` and `i40e_clean_tx_irq_unmap`, recording ring, descriptor, buffer, and netdev.
- `DECLARE_EVENT_CLASS(i40e_rx_template)` is reused by `i40e_clean_rx_irq` and `i40e_clean_rx_irq_rx`, recording ring, RX descriptor, XDP buffer, and netdev.
- `DECLARE_EVENT_CLASS(i40e_xmit_template)` is reused by `i40e_xmit_frame_ring` and `i40e_xmit_frame_ring_drop`, recording skb, ring, and netdev.

## Control Flow

The header has compile-time tracepoint generation flow rather than normal runtime control flow. During compilation, the trace macros generate event structures, fast assignment code, print formats, and `trace_i40e_*` call sites. At runtime, when call sites invoke `i40e_trace()`, the generated tracepoint either records the fields if enabled or is skipped by the tracepoint machinery. The first fields in the Tx event class intentionally match `TP_PROTO` to support BCC `tplist` argument parsing.

## State and Persistence Behavior

No driver state is persisted here. Tracepoints expose transient runtime state: NAPI scheduling and completion, queue vector CPU/IRQ affinity, descriptor and buffer addresses, skb pointers, and netdev names. The `NO_DEV` fallback avoids dereferencing a missing NAPI netdev name. When tracing is disabled, overhead should remain low; when enabled, trace buffers outside the driver persist event samples according to kernel tracing configuration.

## Dependencies and Integration Points

The file depends on Linux `tracepoint.h` and on i40e types visible at inclusion sites: `struct napi_struct`, `struct i40e_q_vector`, `struct i40e_ring`, `struct i40e_tx_desc`, `struct i40e_tx_buffer`, `union i40e_16byte_rx_desc`, `struct xdp_buff`, and `struct sk_buff`. It integrates with the kernel tracing subsystem, ftrace/perf/BPF tooling, and i40e datapath call sites in NAPI, Tx cleanup, Rx cleanup, and xmit/drop paths. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE i40e_trace` are required because this trace header lives in the driver directory rather than `include/trace/events`.

## Risks

- Tracepoint field expressions dereference ring and netdev pointers. Call sites must only invoke these tracepoints when those objects are valid.
- Trace output includes kernel pointers. Pointer formatting is standard for tracepoints, but observability policy depends on kernel pointer restrictions and tracing permissions.
- Changing event field order or names can break BPF/perf scripts that rely on the existing tracepoint ABI.
- The include guard intentionally differs from normal headers. Simplifying it can break multi-read trace generation.
- Tracepoint overhead is usually low when disabled, but enabled tracing in high-rate Tx/Rx paths can perturb performance.

## Test Signals

Build success is the first signal because trace headers are sensitive to macro ordering. Runtime validation includes enabling `i40e:i40e_napi_poll`, `i40e:i40e_clean_tx_irq`, `i40e:i40e_clean_rx_irq`, and `i40e:i40e_xmit_frame_ring*` via ftrace/perf, generating traffic, and confirming events include expected netdev names, queue names, budgets, cleaned counts, descriptor pointers, and drops. BPF `tplist` compatibility should be checked after changing event prototypes or field ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_trace.h -->

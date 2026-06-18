# subset-b-004493 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ptp.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ptp.c

## Purpose
`igc_ptp.c` implements PTP hardware clock support for Intel IGC i225-class devices. It exposes PHC time adjustment, read, set, periodic output, external timestamp, PPS, hardware Rx/Tx timestamping, AF_XDP timestamp completion, PCIe PTM cross timestamping, and reset/suspend preservation for the device time registers.

## Important APIs, Types, and Functions
The public driver entry points are `igc_ptp_init()`, `igc_ptp_stop()`, `igc_ptp_suspend()`, `igc_ptp_reset()`, `igc_ptp_hwtstamp_set()`, `igc_ptp_hwtstamp_get()`, `igc_ptp_tx_tstamp_event()`, `igc_ptp_tx_hang()`, `igc_ptp_rx_pktstamp()`, and `igc_ptp_clear_xsk_tx_tstamp_queue()`. PTP clock operations are wired through `adapter->ptp_caps`: `igc_ptp_adjfine_i225()`, `igc_ptp_adjtime_i225()`, `igc_ptp_gettimex64_i225()`, `igc_ptp_getcyclesx64()`, `igc_ptp_settime_i225()`, `igc_ptp_feature_enable_i225()`, and optionally `igc_ptp_getcrosststamp()`. TX timestamp state lives in `adapter->tx_tstamp[]` entries with register masks, register addresses, backing `skb` or XSK metadata, and timeout counters.

## Control Flow
Initialization configures the four hardware TX timestamp register slots, creates SDP pin descriptors, fills PTP clock capabilities, initializes locks, seeds time preservation state, and registers the PHC. Timestamp mode changes pass through `igc_ptp_set_timestamp_mode()`, which toggles TX and RX hardware register bits and per-ring `IGC_RING_FLAG_TX_HWTSTAMP`. TX completion is interrupt driven: `igc_ptp_tx_tstamp_event()` takes `ptp_tx_lock`, reads `TSYNCTXCTL`, drains timestamp registers, applies link-speed latency corrections, reports timestamps to `skb_tstamp_tx()` or AF_XDP metadata, then frees the held buffer. A special register-0 workaround reads `TXSTMPH_0` even when register 0 was not initially ready, then detects races by comparing `TXSTMPL_0` before and after the workaround read.

## State and Persistence Behavior
PTP time is hardware state in `SYSTIM*`, `TIMINCA`, `TIMADJ`, `TSAUXC`, `TSSDP`, timestamp control registers, and PTM registers. Driver shadow state includes `tstamp_config`, `perout[]`, `pps_sys_wrap_on`, `prev_ptp_time`, `ptp_reset_start`, `ptp_flags`, timeout counters, and pending TX timestamp buffers. Suspend saves PHC time and stops PTM when the PCI device is present. Reset restores timestamp mode, PTM/PTP registers, and PHC time by adding elapsed wall time to the saved timestamp.

## Dependencies and Integration Points
The file integrates with Linux PTP, netdev hwtstamp configuration, PCIe PTM, X86 ART cross timestamping, AF_XDP metadata, IGC register accessors, TX/RX ring flags, NAPI wakeups through `igc_xsk_wakeup()`, and netdevice logging. It depends heavily on constants from IGC register and bitfield headers.

## Risks and Edge Cases
PTP paths are concurrency-sensitive: `tmreg_lock`, `free_timer_lock`, `ptm_lock`, and `ptp_tx_lock` protect different register sets and request queues. TX timestamp register 0 has an explicit hardware interrupt erratum workaround. XSK pending timestamp cleanup must run before XDP pool teardown to avoid stale buffer references. Periodic output start times are forced into the future to avoid programming an already elapsed target. Cross timestamping is disabled for unsupported PTM paths and i225-V because of noted lockup risk.

## Test Signals
Useful tests include PHC register/get/set/adjfine checks, hwtstamp set/get for supported and unsupported filters, TX timestamp timeout injection, AF_XDP metadata timestamp completion, XSK pool disable with pending timestamps, reset/suspend/resume PHC continuity, PPS/perout/extts pin assignment conflicts, and PTM cross timestamp success/failure on PTM-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_regs.h

## Purpose
`igc_regs.h` is the register map and low-level MMIO access header for the IGC Ethernet driver. It gives symbolic offsets for core device control, interrupts, RX/TX rings, statistics, filtering, timestamping, TSN, PCIe PTM, wake, EEE, LTR, and PHY/NVM related registers.

## Important APIs, Types, and Functions
The header defines `IGC_*` register offsets and indexed offset macros such as `IGC_RDBAL(_n)`, `IGC_TDBAL(_n)`, `IGC_EITR(_n)`, `IGC_SRRCTL(_n)`, `IGC_TXQCTL(_n)`, and `IGC_TQAVCC(_n)`. It declares `struct igc_hw` and `u32 igc_rd32(struct igc_hw *hw, u32 reg)`. Access helpers are `wr32(reg, val)`, `rd32(reg)`, `wrfl()`, `array_wr32()`, `array_rd32()`, and `IGC_REMOVED()`.

## Control Flow
There is no runtime control flow beyond the write/read helper macros. `wr32()` snapshots `hw->hw_addr` with `READ_ONCE()`, checks `IGC_REMOVED()`, and writes with `writel()`. `rd32()` delegates to `igc_rd32()`. `wrfl()` reads `IGC_STATUS` to flush posted writes.

## State and Persistence Behavior
The file does not store state itself. Its definitions describe persistent device MMIO state and are used by other driver modules to mutate runtime hardware state. The helpers avoid MMIO writes after the device memory address has been removed.

## Dependencies and Integration Points
Every IGC module that touches hardware depends on this header, including PTP (`SYSTIM`, `TSYNCTXCTL`, PTM), TSN (`TQAVCTRL`, Qbv/Qav registers), ring setup, statistics, filters, NVM, wake, EEE, and interrupt handling. It assumes bit macros such as `BIT()` and `GENMASK()` are available through included driver/kernel headers.

## Risks and Edge Cases
Incorrect offsets or indexed strides can corrupt unrelated device state. `wr32()` silently skips writes after removal, so callers must still handle device teardown races. `rd32()` behavior depends on `igc_rd32()` handling removed hardware safely. Register definitions are shared across many features, so changes have wide blast radius.

## Test Signals
Build coverage is the primary signal. Runtime smoke tests should include probe/remove, reset, interrupt setup, RX/TX ring bring-up, hwtstamp/PTP, TSN offload, ethtool stats, wake/EEE paths, and device removal under load to exercise the MMIO helper assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.c

## Purpose
`igc_tsn.c` implements IGC Time-Sensitive Networking offload programming: frame preemption, MAC merge verification packets, taprio/Qbv gate scheduling, ETF/launchtime support, credit-based shaper/Qav setup, strict queue priority, RX/TX packet buffer sizing, and i226-specific retry-buffer workarounds.

## Important APIs, Types, and Functions
Public entry points are `igc_fpe_init()`, `igc_fpe_clear_preempt_queue()`, `igc_fpe_save_preempt_queue()`, `igc_fpe_get_supported_frag_size()`, `igc_tsn_adjust_txtime_offset()`, `igc_tsn_is_taprio_activated_by_user()`, `igc_tsn_reset()`, and `igc_tsn_offload_apply()`. Internal helpers build and transmit SMD-V/SMD-R frames, map preemptible traffic classes to queues, compute new TSN flags, program TX arbitration, update RX packet buffer sizes, disable TSN registers to defaults, and enable full TSN offload register state.

## Control Flow
FPE initialization installs `ethtool_mmsv_ops`. Ettool MAC merge callbacks update `adapter->fpe.tx_enabled` and can send verification/response SMD frames through a selected TX ring. TSN configuration is applied via `igc_tsn_offload_apply()`: if enabling or disabling TSN would change hardware TX mode while the netdev is running, it schedules an adapter reset; otherwise it calls `igc_tsn_reset()` directly. `igc_tsn_reset()` adds or removes the empty MAC filter needed by preemption, computes TSN flags, disables offload if none are active, or writes the complete TSN register set.

## State and Persistence Behavior
Driver state lives in adapter flags, `taprio_offload_enable`, `strict_priority_enable`, `base_time`, `cycle_time`, `qbv_count`, each TX ring's start/end time, CBS, launchtime, and preemptible flags, plus `adapter->fpe` MAC merge state. Hardware state is in `TQAVCTRL`, `GTXOFFSET`, `TXPBS`, `RXPBS`, `DTXMXPKTSZ`, `TXQCTL`, `STQT`, `ENDQT`, `QBVCYCLET`, `BASET`, `TXARB`, `TQAVCC`, `TQAVHC`, and i226 `RETX_CTL`. Reset paths reconstruct hardware state from driver state.

## Dependencies and Integration Points
The file integrates with ethtool MAC merge verification, tc-mqprio preemptible TC configuration, taprio/launchtime ring settings, IGC TX descriptor formatting, DMA mapping, queue locks, netdev queue accounting, and hardware helpers from `igc.h`, `igc_base.h`, and register definitions.

## Risks and Edge Cases
SMD frame injection uses atomic allocation, DMA mapping, queue locks, descriptor availability, and TX flush ordering. TSN base time is adjusted if already in the past; i226 future scheduling uses `FUTSCDDIS` and an hrtimer path, making timing sensitive. CBS is only configured for queues 0 and 1. FPE queue state depends on `tx_enabled`, `pmac_enabled`, and saved preemptible TCs. Reset scheduling is required when the hardware TX mode changes.

## Test Signals
Exercise taprio enable/disable with base times in the past and future, CBS on queues 0/1 and ignored queues 2/3, launchtime-only mode, strict priority and reversed arbitration, MAC merge verification exchange, preemptible TC mapping from mqprio, i225 versus i226 register behavior, and reset while TSN settings are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.h

## Purpose
`igc_tsn.h` declares the public TSN/FPE interface for the IGC driver and provides inline helpers for MAC merge packet recognition and SMD-V TX descriptor inspection.

## Important APIs, Types, and Functions
It defines `IGC_RX_MIN_FRAG_SIZE`, `SMD_FRAME_SIZE`, `enum igc_txd_popts_type` with `SMD_V` and `SMD_R`, and declares the static key `igc_fpe_enabled`. Public declarations cover FPE initialization, preempt queue tracking, supported fragment size selection, TSN offload apply/reset, launchtime offset adjustment, and taprio activation query. Inline helpers are `igc_fpe_is_pmac_enabled()`, `igc_fpe_handle_mpacket()`, and `igc_fpe_transmitted_smd_v()`.

## Control Flow
The header has simple inline control flow. `igc_fpe_is_pmac_enabled()` requires both the static key and adapter PMAC state. `igc_fpe_handle_mpacket()` extracts SMD type from RX descriptor status, accepts only verify/response SMD frames, validates a zero-filled 60-byte mpacket, reports the matching ethtool MAC merge event, and consumes the frame. `igc_fpe_transmitted_smd_v()` reads TX descriptor popts to detect transmitted verification frames.

## State and Persistence Behavior
No state is stored in the header. It reads adapter FPE state, RX descriptor status, and TX descriptor fields. Runtime FPE/TSN state is maintained in `igc_tsn.c` and adapter/ring structures.

## Dependencies and Integration Points
The header depends on packet scheduler types, ethtool MAC merge events, IGC descriptor bit definitions, `mem_is_zero()`, field extraction helpers, and adapter/ring structures supplied by the including driver headers. It is consumed by RX/TX paths that need to identify MAC merge mpackets.

## Risks and Edge Cases
The mpacket helper assumes SMD-V/SMD-R frames are exactly 60 zero bytes; malformed frames with valid SMD status are still consumed after the SMD type check even if no ethtool event is emitted. Static-key gating in `igc_fpe_is_pmac_enabled()` must match the global feature enable lifecycle. The include guard closing comment names `_IGC_BASE_H_`, which is cosmetic but misleading.

## Test Signals
Compile TSN/FPE users, inject RX descriptors for SMD-V, SMD-R, and non-SMD packets, verify ethtool MAC merge events, confirm malformed SMD frames are consumed as coded, and test TX descriptor detection for SMD-V versus SMD-R.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.c

## Purpose
`igc_xdp.c` handles XDP program attachment and AF_XDP zero-copy pool setup for IGC queues. It coordinates ring/NAPI quiescing when XDP state changes, updates netdev XDP redirect features, validates AF_XDP frame sizing, maps/unmaps UMEM DMA, and marks RX/TX rings for zero-copy operation.

## Important APIs, Types, and Functions
The public functions are `igc_xdp_set_prog()` and `igc_xdp_setup_pool()`. Internal helpers are `igc_xdp_enable_pool()` and `igc_xdp_disable_pool()`. The code uses `adapter->xdp_prog`, per-ring `IGC_RING_FLAG_AF_XDP_ZC`, `xsk_pool_dma_map()`, `xsk_pool_dma_unmap()`, `xsk_get_pool_from_qid()`, `igc_disable_rx_ring()`, `igc_disable_tx_ring()`, `igc_enable_rx_ring()`, `igc_enable_tx_ring()`, `napi_disable()`, `napi_enable()`, and `igc_xsk_wakeup()`.

## Control Flow
XDP program changes reject jumbo MTUs, compute whether queue restart is needed based on old and new XDP enabled state, disable each RX/TX ring and NAPI if running, atomically swap the BPF program, drop the old reference, update redirect target features, then re-enable NAPI and rings. AF_XDP pool enable validates queue IDs and frame size, maps the pool for DMA, optionally quiesces the queue pair if the interface is running with XDP enabled, sets zero-copy flags on both rings, restarts the queue pair, and wakes RX. Disable does the reverse: look up the pool, optionally quiesce, unmap DMA, clear flags, and restart.

## State and Persistence Behavior
The file updates runtime-only state: `adapter->xdp_prog`, netdev XDP feature flags, ring zero-copy flags, and DMA mapping state owned by the XSK pool. No persistent state exists. Running rings are temporarily stopped and restarted to make state transitions coherent.

## Dependencies and Integration Points
It integrates with Linux BPF/XDP, AF_XDP socket pools, VLAN sizing assumptions, netdev feature advertising, IGC ring enable/disable helpers, NAPI lifecycle, PCI device DMA attributes, and the IGC XSK wakeup path.

## Risks and Edge Cases
Jumbo frames are unsupported. AF_XDP frame size must hold a full Ethernet frame plus double VLAN tags because the driver does not support multi-buffer XDP. Queue ID validation must cover both RX and TX queue counts. If `igc_xsk_wakeup()` fails after re-enabling a pool, the code unmaps DMA and returns an error, so flag cleanup and ring state should be scrutinized. Program swaps rely on `xchg()` and correct BPF reference ownership.

## Test Signals
Test XDP attach/detach while down and running, jumbo MTU rejection, redirect feature toggling, AF_XDP pool enable/disable with invalid queues and small frames, DMA map failure, wakeup failure, and repeated pool transitions while packets are flowing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.h

## Purpose
`igc_xdp.h` declares the IGC XDP and AF_XDP setup interface and provides a small inline predicate for XDP-enabled adapter state.

## Important APIs, Types, and Functions
The header declares `igc_xdp_set_prog()` for BPF program attach/detach and `igc_xdp_setup_pool()` for AF_XDP pool enable/disable by queue. `igc_xdp_is_enabled()` returns whether `adapter->xdp_prog` is non-NULL.

## Control Flow
There is no complex control flow. The inline helper is a boolean pointer check used by pool setup and other driver paths to decide whether XDP-specific queue handling is active.

## State and Persistence Behavior
The header owns no state. It reads `adapter->xdp_prog`, which is runtime-only and managed by `igc_xdp.c`.

## Dependencies and Integration Points
It depends on declarations for `struct igc_adapter`, `struct bpf_prog`, `struct netlink_ext_ack`, and `struct xsk_buff_pool` from including headers. It is included by IGC control paths that need to attach XDP programs or configure AF_XDP zero-copy pools.

## Risks and Edge Cases
The predicate reports only attached BPF program state, not AF_XDP pool state. Callers that need zero-copy state must inspect ring flags or pool bindings separately.

## Test Signals
Compile all callers, verify attach/detach paths use the declarations correctly, and ensure callers do not treat `igc_xdp_is_enabled()` as an AF_XDP pool predicate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/Makefile

## Purpose
The ixgbe `Makefile` defines how the Intel 10GbE PCI Express driver object is built and which feature-specific objects are included for kernel configuration options.

## Important APIs, Types, and Functions
It sets `subdir-ccflags-y += -I$(src)`, builds `ixgbe.o` when `CONFIG_IXGBE` is enabled, and lists core objects such as `ixgbe_main.o`, common/MAC/PHY modules, PTP, XSK, E610 support, devlink support, firmware update support, and devlink regions. Conditional object additions are controlled by `CONFIG_IXGBE_DCB`, `CONFIG_IXGBE_HWMON`, `CONFIG_DEBUG_FS`, `CONFIG_FCOE:m=y`, and `CONFIG_IXGBE_IPSEC`.

## Control Flow
There is no runtime control flow. Kbuild evaluates configuration symbols and appends the matching object files into the composite `ixgbe-y` object list.

## State and Persistence Behavior
The file has build-system state only. It does not affect runtime persistence, but it determines whether optional runtime features are present in a given kernel build.

## Dependencies and Integration Points
The Makefile integrates the ixgbe subdirectory with Linux Kbuild. The inclusion of `devlink/devlink.o`, `devlink/region.o`, `ixgbe_fw_update.o`, and `ixgbe_e610.o` makes the newer E610/devlink feature surface part of the base driver when `CONFIG_IXGBE` is enabled.

## Risks and Edge Cases
Conditional feature objects must match preprocessor declarations and stubs in headers. Adding an object without its dependent config or missing an object for an enabled declaration can break link. The `CONFIG_FCOE:m=y` expression is unusual and should be validated against intended built-in/module combinations.

## Test Signals
Build ixgbe across combinations of DCB, HWMON, DEBUG_FS, FCOE, IPSEC, and base IXGBE as built-in and module. Link errors are the primary failure signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.c

## Purpose
`devlink.c` adds devlink integration for ixgbe physical functions. It exposes device identity and firmware versions, supports E610 flash update and firmware activation reload through EMP reset, allocates the adapter through `devlink_alloc()`, and registers a physical devlink port with a PCI DSN based switch ID.

## Important APIs, Types, and Functions
`struct ixgbe_info_ctx` stores formatted version strings and pending E610 inactive bank metadata. Version helpers format DSN, OROM, ETRACK, firmware API/build/security revision, NVM, and netlist versions. `ixgbe_devlink_info_get()` is the devlink info callback. E610-specific callbacks are `ixgbe_devlink_info_get_e610()` and `ixgbe_devlink_pending_info_get_e610()`. Reload operations are `ixgbe_devlink_reload_empr_start()` and `ixgbe_devlink_reload_empr_finish()`. Public lifecycle functions are `ixgbe_allocate_devlink()` and `ixgbe_devlink_register_port()`.

## Control Flow
Info retrieval allocates a context, refreshes E610 firmware version if needed, publishes serial number and board ID, publishes running OROM and bundle ID, then for E610 discovers device capabilities, reads inactive bank versions for pending updates, and publishes running and stored firmware component versions. Firmware activation reload is E610-only: reload down checks pending updates and EMP reset availability, triggers `ixgbe_aci_nvm_update_empr()`, and reload up polls `FWSM` until firmware valid, records the performed action, clears mismatch/rollback flags, and refreshes firmware version.

## State and Persistence Behavior
The file creates runtime devlink objects (`adapter->devlink`, `adapter->devlink_port`) and reads firmware/NVM state from hardware. Flash update and EMP reload alter persistent device firmware banks through helpers in the firmware update code, while this file mainly exposes metadata and triggers activation. Adapter flags for API mismatch and rollback are cleared after successful reload.

## Dependencies and Integration Points
It integrates with Linux devlink info, flash update, reload, and port APIs; PCI DSN; ixgbe EEPROM/NVM helpers; E610 Admin Command Interface helpers; PLDM image flashing; and adapter allocation used by probe. It depends on `devlink.h` declarations and `ixgbe_fw_update.h`.

## Risks and Edge Cases
Most extended version reporting is E610-specific and must not run on older MACs. Pending inactive bank reads are best effort and clear the pending flag on read failure, which can hide stored version details. EMP reset is rejected if no pending update exists or if firmware disables EMP reset. Reload finish uses fixed 500 ms polling up to 10 seconds and returns `-ETIME` if firmware valid never appears.

## Test Signals
Use `devlink info` on legacy ixgbe and E610 devices, flash image update with pending versions, `devlink reload action fw_activate`, no-pending reload rejection, EMP-disabled rejection, firmware-valid timeout injection, and devlink port registration failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.h

## Purpose
`devlink.h` declares the small ixgbe devlink interface used by probe, teardown, and E610 region setup code.

## Important APIs, Types, and Functions
The header declares `ixgbe_allocate_devlink()`, `ixgbe_devlink_register_port()`, `ixgbe_devlink_init_regions()`, and `ixgbe_devlink_destroy_regions()`.

## Control Flow
The header has no executable control flow. Its declarations connect `devlink.c` and `region.c` with the rest of the ixgbe driver.

## State and Persistence Behavior
No state is stored here. Implementations allocate `struct devlink`, register `struct devlink_port`, and create/destroy devlink regions stored in `struct ixgbe_adapter`.

## Dependencies and Integration Points
It relies on forward declarations from including headers for `struct device` and `struct ixgbe_adapter`. It is included by ixgbe probe/devlink code and region management code.

## Risks and Edge Cases
Because the header has no stubs, the Makefile must always include the corresponding devlink objects whenever callers are built. Public function signatures must remain aligned with devlink core API changes.

## Test Signals
Build/link ixgbe with devlink objects and exercise probe/remove to ensure allocation, port registration, and region lifecycle functions are all resolved and called in valid order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/region.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/region.c

## Purpose
`region.c` implements ixgbe devlink regions for E610 devices. It exposes NVM flash, shadow RAM, and device capability snapshots/read access through devlink regions.

## Important APIs, Types, and Functions
Region ops are `ixgbe_nvm_region_ops`, `ixgbe_sram_region_ops`, and `ixgbe_devcaps_region_ops`. `ixgbe_devlink_parse_region()` maps region ops to flat NVM versus shadow RAM access and sizes. Snapshot/read callbacks are `ixgbe_devlink_nvm_snapshot()`, `ixgbe_devlink_nvm_read()`, and `ixgbe_devlink_devcaps_snapshot()`. Public lifecycle functions are `ixgbe_devlink_init_regions()` and `ixgbe_devlink_destroy_regions()`.

## Control Flow
Region initialization is E610-only. It creates one-snapshot NVM and shadow RAM regions sized from `hw.flash.flash_size` and `hw.flash.sr_words * 2`, then creates a device-caps region with up to ten snapshots. NVM snapshots allocate a full buffer, read in 1 MiB blocks, acquire and release the NVM semaphore for each block to avoid holding it beyond the timeout, and return the buffer to devlink. Direct reads validate bounds, acquire the NVM semaphore once, read the requested range, and release. Device-caps snapshots allocate an ACI buffer and issue `ixgbe_aci_list_caps()`.

## State and Persistence Behavior
The file stores runtime devlink region handles in `adapter->nvm_region`, `adapter->sram_region`, and `adapter->devcaps_region`. It reads persistent flash and shadow RAM but does not write them. Snapshot buffers are dynamically allocated and freed by devlink through `kvfree`.

## Dependencies and Integration Points
It integrates with Linux devlink region APIs, ixgbe E610 flash metadata, NVM semaphore helpers, flat NVM readers, ACI capability listing, netlink extack reporting, and adapter teardown.

## Risks and Edge Cases
Large NVM snapshots can allocate significant memory. Semaphore acquisition failure returns `-EBUSY`; read failure returns `-EIO` and must release the semaphore before freeing. The number of 1 MiB blocks is stored in `u8`, so unexpectedly large flash sizes would be risky. Destroy only runs for E610 and checks non-NULL handles, but failed create paths leave individual region pointers NULL.

## Test Signals
Run `devlink region show/new/read/del` for NVM, shadow RAM, and device-caps on E610; test non-E610 no-op behavior; inject NVM semaphore and read failures; verify out-of-range reads return `-ERANGE`; and check remove after partial region creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe.h

## Purpose
`ixgbe.h` is the central private header for the ixgbe driver. It defines descriptor limits, buffer sizing, TX/RX flags, VF and SR-IOV state, ring and queue-vector structures, adapter-wide state, feature flags, helper macros, inline packet timestamp handling, and prototypes for the driver's cross-file implementation.

## Important APIs, Types, and Functions
Key structures include `struct ixgbe_adapter`, `struct ixgbe_ring`, `struct ixgbe_q_vector`, `struct ixgbe_tx_buffer`, `struct ixgbe_rx_buffer`, `struct vf_data_storage`, `struct ixgbe_ring_feature`, and `struct ixgbe_fdir_filter`. It defines feature bits in `adapter->flags` and `flags2`, ring state bits, queue limits, RSS/VMDQ/FDIR constants, XDP helpers, PTP fields, devlink region fields, and many exported driver prototypes. Inline helpers include descriptor accessors, buffer sizing, ring-state tests, `ixgbe_from_netdev()`, XDP queue selection, max RSS indices, `ixgbe_ptp_rx_hwtstamp()`, and `ixgbe_enabled_xdp_adapter()`.

## Control Flow
The header's inline control flow is focused on fast-path decisions: RX buffer size/page order selection based on ring state, descriptor availability calculation, XDP ring selection based on CPU/static key, MAC-type-based RSS limit selection, and RX hardware timestamp dispatch depending on descriptor status bits.

## State and Persistence Behavior
Most ixgbe runtime state is shaped here. `struct ixgbe_adapter` persists for the PCI function lifetime and tracks netdev, PCI, devlink, rings, queues, interrupts, DCB, SR-IOV, PTP, FDIR, XDP, IPsec, firmware flags, statistics, and hardware state. The header does not itself persist state, but its structures mirror hardware settings and hold software-owned counters and references.

## Dependencies and Integration Points
It includes kernel PCI/netdev/PTP/devlink/XDP headers and ixgbe type/common/DCB/E610/IPsec/FCoE headers. It is included by almost every ixgbe source file and forms the contract between probe, TX/RX, ethtool, devlink, PTP, SR-IOV, DCB, FCoE, IPsec, XSK, and MAC-specific modules.

## Risks and Edge Cases
This header has high blast radius. Layout changes to hot ring structures can affect cache alignment and fast path performance. Feature bit semantics must stay synchronized with implementation files. Inline timestamp handling mutates per-ring timestamp watchdog state and must match PTP register behavior. XDP queue selection depends on static key state and CPU indexes. Conditional FCoE/IPsec/debugfs/hwmon declarations must match Makefile objects and stubs.

## Test Signals
Full ixgbe build matrix across optional features, sparse/smatch for structure/inline misuse, RX/TX performance smoke tests, PTP timestamp tests, SR-IOV VF lifecycle, XDP/AF_XDP, DCB/FCoE/IPsec feature builds, and probe/remove with devlink region fields initialized and destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_82598.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_82598.c

## Purpose
`ixgbe_82598.c` provides MAC, PHY, EEPROM, link, flow-control, reset, VLAN/VMDq, I2C, analog register, and packet-buffer operations for the Intel 82598 generation of ixgbe hardware.

## Important APIs, Types, and Functions
It exports `ixgbe_82598_info`, whose operation tables bind 82598-specific functions into the generic driver. Important helpers include `ixgbe_get_invariants_82598()`, `ixgbe_init_phy_ops_82598()`, `ixgbe_start_hw_82598()`, `ixgbe_get_link_capabilities_82598()`, `ixgbe_get_media_type_82598()`, `ixgbe_fc_enable_82598()`, `ixgbe_start_mac_link_82598()`, `ixgbe_check_mac_link_82598()`, `ixgbe_setup_mac_link_82598()`, `ixgbe_reset_hw_82598()`, VMDq/VFTA helpers, analog register accessors, SFP I2C readers, LAN ID correction, and `ixgbe_set_rxpba_82598()`.

## Control Flow
The generic driver uses `ixgbe_82598_info` during probe to install operation tables. Reset stops the adapter, powers Atlas TX lanes back up if loopback powered them down, initializes/resets PHY unless disabled, issues a MAC software reset, optionally performs a second reset, stores/restores original AUTOC link settings, reads the permanent MAC, and clears RX address/multicast state. Link setup reads capabilities from AUTOC and configures KX/KX4 or copper PHY paths before restarting autoneg. Flow control validates watermarks and pause time, works around 1G RX pause reset issues, negotiates mode, and programs FCTRL/RMCS/FCRTL/FCRTH/FCTTV/FCRTV.

## State and Persistence Behavior
The file updates hardware registers and cached fields such as original AUTOC, permanent MAC address, PHY type, media type, and MAC invariant sizes. EEPROM/NVM content is read but not generally persisted here except through generic EEPROM write ops exposed in the operation table. VLAN and VMDq programming persists in hardware filter registers until reset or reconfiguration.

## Dependencies and Integration Points
It integrates with generic ixgbe MAC/PHY/EEPROM helpers, MDIO, SFP module identification, SW/FW semaphores, PCI config access, flow-control negotiation, VMDq/VFTA register layout, and device ID based media detection.

## Risks and Edge Cases
82598 has several hardware-specific workarounds: PCIe completion timeout adjustment, 1G RX pause disable, AT2 link-ready validation, Atlas lane power restoration, and possible double reset. SFP I2C reads require SW/FW semaphore ownership and polling. VLAN/VMDq helpers validate limited register ranges but rely on caller-provided VMDq values. Reset failure handling must preserve PHY status errors.

## Test Signals
Probe/reset 82598 variants across fiber, copper, backplane, and CX4 IDs; link setup for 1G and 10G; flow-control modes and invalid watermarks; SFP EEPROM/SFF-8472 reads; VLAN filter and VMDq programming; loopback followed by reset; and PCIe completion timeout configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_82598.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_82599.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_82599.c

## Purpose
`ixgbe_82599.c` provides 82599-generation ixgbe MAC, PHY, EEPROM, link, reset, Flow Director, SFP/QSFP, I2C, RX DMA, firmware-version, and operation table support. It is the hardware-specific layer for 82599 devices while sharing generic ixgbe helpers.

## Important APIs, Types, and Functions
It exports `ixgbe_82599_info`. Public Flow Director helpers include `ixgbe_reinit_fdir_tables_82599()`, `ixgbe_init_fdir_signature_82599()`, `ixgbe_init_fdir_perfect_82599()`, `ixgbe_fdir_add_signature_filter_82599()`, `ixgbe_fdir_set_input_mask_82599()`, `ixgbe_fdir_write_perfect_filter_82599()`, `ixgbe_fdir_erase_perfect_filter_82599()`, and `ixgbe_atr_compute_perfect_hash_82599()`. Hardware setup helpers include management detection, MAC link op initialization, SFP setup, protected AUTOC read/write, invariants, PHY init, link capability/media queries, D3 link stop, MAC/copper link setup, reset, analog access, firmware checks, EEPROM reads, pipeline reset, and shared QSFP I2C byte access.

## Control Flow
Probe installs operation tables through `ixgbe_82599_info`. PHY init handles QSFP shared I2C setup, identifies PHY/SFP, initializes MAC link ops, and switches copper media to copper link handlers. Link setup masks requested speeds against capabilities, rewrites AUTOC fields for KR/KX/KX4/SFI modes, and uses protected AUTOC writes when LESM firmware requires SW/FW locking. SmartSpeed retries full advertisement, then disables KR if needed and retries. Reset stops the adapter, clears pending TX, initializes PHY/SFP, chooses link or software reset based on link state and force flags, handles double reset, restores AUTOC/AUTOC2, initializes RX addresses, reserves a SAN MAC RAR if present, and reads WWN prefixes.

## State and Persistence Behavior
The file maintains cached original AUTOC/AUTOC2, PHY smart-speed and multispeed-fiber state, SFP setup state, SAN MAC RAR reservation, permanent MAC/SAN/WWN addresses, and operation pointers. It programs persistent runtime hardware state in AUTOC, AUTOC2, FDIR registers, RARs, RX control, I2C GPIO ownership bits, and EEPROM-derived firmware/module configuration. EEPROM is read through fastest available method but not written by this file.

## Dependencies and Integration Points
It integrates with generic ixgbe MAC/PHY/EEPROM helpers, mailbox ops, Flow Director ethtool/filter code, SFP module identification and EEPROM init sequences, SW/FW semaphores, management firmware detection, DCB/RSS/VMDq feature layers, and hardware register definitions from `ixgbe_type.h`.

## Risks and Edge Cases
AUTOC writes may need LESM semaphore ownership, and pipeline reset temporarily toggles LMS bits. Management firmware or WoL can constrain link mode restoration. Flow Director programming has strict mask validation, endian-specific register writes, command polling, and IPv4-only mask support in this implementation. QSFP shared I2C bus access uses GPIO handshaking with timeout. RX DMA enable works around a silicon erratum by disabling the security receive buffer around RX enable changes.

## Test Signals
Test 82599 probe/reset on fiber, copper, backplane, QSFP, and multispeed SFP devices; protected AUTOC paths with LESM enabled; SmartSpeed fallback; SFP setup sequence failure; Flow Director signature/perfect filter add/delete/mask validation; firmware version rejection on old SFI firmware; QSFP I2C timeout; RX DMA enable under traffic; and SAN MAC RAR reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_82599.c -->

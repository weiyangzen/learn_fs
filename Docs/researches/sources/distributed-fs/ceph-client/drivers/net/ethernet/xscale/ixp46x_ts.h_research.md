<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp46x_ts.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp46x_ts.h

Purpose: Defines the IXP46x time-sync register layout, bit masks, timestamp scaling constants, and the conditional API used by the Ethernet driver to discover the PTP hardware clock.

Important APIs/types/functions: `struct ixp46x_channel_ctl` maps per-channel timestamp control/event and TX/RX snapshot/source UUID registers. `struct ixp46x_ts_regs` maps global time-sync control, event, addend, accumulator, raw/system time, target time, auxiliary snapshots, and three timestamp channels. Constants include `DEFAULT_ADDEND`, `TICKS_NS_SHIFT`, global control/event masks (`TSCR_*`, `TSER_*`, `TTIPEND`), channel control masks (`MASTER_MODE`, `TIMESTAMP_ALL`), and snapshot event masks (`TX_SNAPSHOT_LOCKED`, `RX_SNAPSHOT_LOCKED`). `ixp46x_ptp_find()` is declared when `CONFIG_PTP_1588_CLOCK_IXP46X` is enabled and otherwise provided as an inline `-ENODEV` stub that clears the output registers/index.

Control flow: Consumers include this header and call `ixp46x_ptp_find()` to obtain the memory-mapped timestamp registers and PHC index. If PTP support is disabled, the stub makes timestamp support cleanly unavailable while keeping Ethernet builds working.

State and persistence behavior: No state is allocated by the header. It defines the ABI for persistent hardware register state used by `ptp_ixp46x.c` and `ixp4xx_eth.c`.

Dependencies and integration points: Integrates the IXP46x PTP clock provider with the IXP4xx Ethernet driver. It relies on Linux fixed-width integer types and error codes supplied by including C files and on Kconfig selecting or omitting `CONFIG_PTP_1588_CLOCK_IXP46X`.

Risks and test signals: Register layout changes are hardware ABI changes and would break both PHC operations and packet timestamping. `TICKS_NS_SHIFT` defines conversion between hardware ticks and nanoseconds; timestamp tests should verify read/write/adjust behavior against wall-clock expectations. PTP-disabled builds should confirm the stub returns `-ENODEV`, `regs=NULL`, and `phc_index=-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/ixp46x_ts.h -->

# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.h

## Purpose
Declares the public interface for the TI K3 AM65 CPTS time-sync driver and provides no-op or error stubs when CPTS support is disabled.

## Important APIs, Types, and Functions
Defines opaque `struct am65_cpts` and `struct am65_cpts_estf_cfg` with `ns_period` and `ns_start`. Enabled builds declare lifecycle, PHC, timestamp, time read, ESTF, and suspend/resume helpers: `am65_cpts_create`, `am65_cpts_release`, `am65_cpts_phc_index`, `am65_cpts_rx_timestamp`, `am65_cpts_tx_timestamp`, `am65_cpts_prep_tx_timestamp`, `am65_cpts_ns_gettime`, `am65_cpts_estf_enable`, `am65_cpts_estf_disable`, `am65_cpts_suspend`, and `am65_cpts_resume`.

## Control Flow
Compile-time selection through `CONFIG_TI_K3_AM65_CPTS` either binds callers to the implementation or uses inline stubs. Disabled builds return `ERR_PTR(-EOPNOTSUPP)` for create, `-1` for PHC index, zero/no-op behavior for timestamp and ESTF helpers, and no-op suspend/resume.

## State and Persistence
The header stores no state directly. It defines the ESTF timing contract used by QoS/TAPRIO to request a periodic CPTS output and exposes an opaque handle whose implementation persists PHC and event state in `am65-cpts.c`.

## Dependencies and Integration Points
Includes device and OF declarations and is included by the NUSS main driver and QoS module. It bridges optional CPTS support to netdev hwtstamp, RX/TX timestamping, and EST schedule timing without forcing those callers to know CPTS internals.

## Risks and Test Signals
Risks include type/signature drift between stubs and real implementation and callers assuming CPTS is present despite `ERR_PTR(-EOPNOTSUPP)`. Test signals are CPTS-enabled and disabled kernel builds, probe paths with missing `cpts` child nodes, hwtstamp requests returning clear errors when disabled, and TAPRIO behavior when ESTF helpers are stubs.

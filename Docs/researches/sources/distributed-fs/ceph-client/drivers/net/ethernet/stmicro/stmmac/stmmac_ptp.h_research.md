# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ptp.h

Purpose: register ABI and exported declarations for STMMAC PTP support.

Important APIs and definitions: defines PTP register base offsets for XGMAC, GMAC4, and GMAC3.x; IEEE 1588 register offsets for timestamp control, sub-second increment, system time, updates, addend, auxiliary control/timestamps, correction, and latency; timestamp control bits for enable/update/init/addend/protocol/event filtering; SSIR and auxiliary snapshot bits; ART selector constants; `enum aux_snapshot`; prototypes for GMAC1000 PTP helpers; and extern `ptp_clock_info` templates.

Control flow: core-specific code uses these constants for timestamp register access. `hwif.c` selects one ops template, and `stmmac_ptp_register()` registers it after capability adjustment.

State and persistence: no direct state. Definitions populate hardware registers and persistent `priv->ptp_clock_ops`.

Dependencies and integration: forward declares PTP and STMMAC types; consumed by PTP implementation, GMAC1000 timestamp code, and hardware abstraction.

Risks and test signals: hardware bit mismatch silently breaks timestamping. GMAC4-specific comments around snapshot selection imply careful cross-core use. Validate with timestamping, auxiliary snapshots, PPS/perout, and compile coverage across PTP-capable cores.

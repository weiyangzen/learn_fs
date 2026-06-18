<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.h

Purpose: common PHY helper declarations and inline gain/rate index helpers for mt76x02.

Important APIs/types/functions: inline `mt76x02_get_l_gain()`/`mt76x02_get_h_gain()`, and prototypes for rate-power offset/limit/max, TX power, RX path, TX DAC, bandwidth/band, VGA gain, and AGC initialization.

Control flow: declarative header; channel and calibration code include it to share helper contracts.

State and persistence: no local state. Helpers read calibration arrays and write hardware through implementations in `mt76x02_phy.c`.

Dependencies/integration: included by mt76x2 init/PHY and shared PHY code; depends on `struct mt76x02_dev` and rate-power struct from `mt76x02.h`.

Risks: inline gain indexing must match chain number; callers must initialize AGC gains before reading them. Test signals include compile coverage, channel switch after AGC init, single-chain and dual-chain gain reads, and TX power register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.h -->

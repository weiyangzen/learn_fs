<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.c

Purpose: common PHY helper routines for mt76x02. It programs RX/TX chain paths, bandwidth/band registers, rate-power registers, VGA/AGC gain adjustment, and AGC gain initialization.

Important APIs/types/functions: `mt76x02_phy_set_rxpath()`, `mt76x02_phy_set_txdac()`, `mt76x02_phy_set_txpower()`, `mt76x02_phy_set_bw()`, `mt76x02_phy_set_band()`, `mt76x02_phy_adjust_vga_gain()`, `mt76x02_init_agc_gain()`, and rate-power min/max helpers.

Control flow: channel setup code derives rate power and calls these helpers to write ALC/TX power tables, band flags, bandwidth/control-channel fields, and antenna paths. Calibration periodically reads false CCA and adjusts AGC gain offset up/down within a low-gain-dependent limit.

State and persistence: writes BBP/TX power/band registers and updates `dev->cal.false_cca`, AGC gain arrays, low-gain flags, and gain-init marker.

Dependencies/integration: mt76x2 PCI/USB PHY paths, EEPROM-derived power tables, DFS AGC adjustment, EDCCA learning, and register definitions.

Risks: chainmask interpretation, signed power table packing, bandwidth/control channel mismatch, and unstable AGC adjustment from noisy false-CCA counters. Test signals include 1x1/2x2 antenna modes, 20/40/80 MHz channels, TX power limit changes, false-CCA stress, and channel switch calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.c -->

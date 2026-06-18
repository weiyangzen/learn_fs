# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.h

## Purpose

`phy_g.h` is the private register and state contract for the b43 G-PHY implementation. It defines CCK and extended G-PHY register offsets, G-PHY table encodings, attenuation value types, TX-control bit meanings, and the `struct b43_phy_g` state block that `phy_g.c` stores under `dev->phy.g`.

The header does not implement the PHY algorithms, but it exposes the few G-PHY helpers needed by other b43 PHY code and declares `b43_phyops_g` for common PHY dispatch.

## Important APIs, Types, and Macros

- `B43_PHY_VERSION_CCK`, `B43_PHY_CCKBBANDCFG`, `B43_PHY_PGACTL`, `B43_PHY_ITSSI`, `B43_PHY_LO_LEAKAGE`, `B43_PHY_ENERGY`, `B43_PHY_DACCTL`, and `B43_PHY_RCCALOVER` name CCK/B-PHY registers used during G-PHY initialization, power measurement, LO leakage calibration, and attenuation programming.
- `B43_PHY_CLASSCTL`, `B43_PHY_GTABCTL`, `B43_PHY_GTABDATA`, `B43_PHY_LO_MASK`, `B43_PHY_LO_CTL`, `B43_PHY_RFOVER`, `B43_PHY_RFOVERVAL`, `B43_PHY_ANALOGOVER`, and `B43_PHY_ANALOGOVERVAL` name extended G-PHY registers used for classification, table access, LO control, RF override, and analog override.
- `B43_GTAB()`, `B43_GTAB_NRSSI`, `B43_GTAB_TRFEMW`, and `B43_GTAB_ORIGTR` encode G-PHY table numbers and offsets.
- `b43_gtab_read()` and `b43_gtab_write()` are external G-PHY table access helpers.
- `has_tx_magnification(phy)` and `has_loopback_gain(phy)` capture hardware capability predicates used by radio and gain setup.
- `struct b43_rfatt`, `struct b43_rfatt_list`, `struct b43_bbatt`, and `struct b43_bbatt_list` model radio and baseband attenuation choices and allowed ranges.
- `b43_compare_rfatt()` and `b43_compare_bbatt()` provide simple equality helpers for attenuation values.
- `B43_TXCTL_PA3DB`, `B43_TXCTL_PA2DB`, and `B43_TXCTL_TXMIX` are TX-control bits passed through the G-PHY TX-power path.
- `struct b43_phy_g` is the per-device G-PHY state object.
- `b43_gphy_set_baseband_attenuation()`, `b43_gphy_channel_switch()`, and `b43_generate_dyn_tssi2dbm_tab()` are callable helpers implemented in `phy_g.c`.
- `extern const struct b43_phy_operations b43_phyops_g` exports the operation table.

## Control Flow and Integration

`phy_common.c` selects `b43_phyops_g` for detected G-PHY hardware. The operation table calls into `phy_g.c`, which uses this header's register constants and `struct b43_phy_g` layout. Common code and neighboring PHY modules can also call the three declared helper functions for baseband attenuation, channel switching, and dynamic TSSI table generation.

The table macros are used with the generic b43 OFDM/G-PHY table helpers. The attenuation types are used by both G-PHY power control and LO calibration code. The capability macros are intentionally header-level so initialization and support code can make consistent radio-revision decisions.

## State and Persistence

`struct b43_phy_g` is volatile per-device state. It persists across callbacks after allocation and until the PHY is freed. Important fields include:

- ACI/interference flags: `aci_enable`, `aci_wlan_automatic`, `aci_hw_rssi`, and `interfmode`.
- RF kill state: `radio_on` and `radio_off_context` with saved RF override registers.
- TX-power state: `tssi2dbm`, `dyn_tssi_tbl`, target/current/average TSSI, current `bbatt`, `rfatt`, `tx_control`, and pending attenuation deltas.
- LO and loopback state: `lo_control`, `max_lb_gain`, `trsw_rx_gain`, `lna_lod_gain`, `lna_gain`, and `pga_gain`.
- Interference mitigation register stack: `interfstack[B43_INTERFSTACK_SIZE]`, currently a packed raw array.
- NRSSI calibration: `nrssi`, `nrssislope`, and `nrssi_lt`.
- Radio/init calibration sentinels: `lofcal` and `initval`.
- OFDM table access cache: `ofdmtab_addr` and `ofdmtab_addr_direction`.

The header comments identify several maturity risks: `interfstack` should be a data structure, `initval` needs a better name, and the table address cache must track last direction to avoid stale hardware address reuse.

## Dependencies

The header includes `phy_a.h` because OFDM PHY registers are shared with A-PHY definitions and needed for G-PHY register encodings. It assumes b43 core types such as `struct b43_wldev`, `struct b43_phy_operations`, `u8`, `u16`, `s8`, `s16`, `s32`, and `bool` are available through kernel and b43 headers. The forward declaration of `struct b43_txpower_lo_control` links this header to `lo.h` without requiring the full LO definition.

## Risks and Edge Cases

- The register constants are raw hardware ABI. A wrong value can silently corrupt unrelated PHY/radio state.
- `B43_INTERFSTACK_SIZE` must remain large enough for every save in interference mitigation; the packed format stores only 12 offset bits and 4 register-id bits.
- `has_tx_magnification()` and `has_loopback_gain()` encode subtle revision/radio predicates. Changes should be validated against all affected radio revisions.
- The dynamic TSSI table pointer can either be static or allocated. Callers must respect `dyn_tssi_tbl` before freeing.
- Header state fields are heavily coupled to `phy_g.c`; changing layout or initialization assumptions can break calibration restore and periodic work.

## Test Signals

Compile coverage should include `CONFIG_B43_PHY_G` and LO support. Runtime signals include successful allocation/free without leaks, no NULL `lo_control` or `tssi2dbm` use after `prepare_structs`, valid attenuation range generation, successful channel changes through `b43_gphy_channel_switch`, and no restore warnings from interference stack users. Static analysis should check that every dynamic TSSI table allocation is paired with the `dyn_tssi_tbl` guarded free.

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c lines 1-4811

## Scope

This chunk covers the opening of the Broadcom `brcmsmac` N-PHY implementation. It contains the module/license header, include dependencies, local register-access macros, calibration/control constants, local helper data types, gain/filter tables, and the first large set of static channel tuning tables. No executable function body is present in lines 1-4811; the chunk is a static configuration and data-definition layer consumed by later N-PHY initialization, channel selection, calibration, and radio programming code in the same file.

The source file continues well beyond this chunk. In particular, the table `chan_info_nphyrev6_2056v11[]` begins at line 4675 and is still open at line 4811, so later chunk(s) must complete that table before whole-file conclusions about all radio 2056v11 channel entries are final.

## Purpose

The visible code establishes the constants and lookup tables needed to translate an 802.11 channel/frequency and radio/PHY revision into concrete RF synthesizer, RX/TX front-end, and PHY bandwidth register values. The data is revision-specific because N-PHY devices use several radio blocks (`2055`, `2056`, later `2057`) with different register naming and tuning values.

The table rows are hardware programming payloads. Each row is keyed by channel number and frequency and then stores the values later routines write into radio registers and N-PHY registers when switching channel, calibrating RX/TX, setting bandwidth, or applying workarounds.

## Dependencies

The chunk includes Linux and driver-local headers:

- Linux helpers: `linux/kernel.h`, `linux/delay.h`, and `linux/cordic.h`.
- Broadcom bus/chip headers: `brcm_hw_ids.h`, `aiutils.h`, `chipcommon.h`, `pmu.h`, and `soc.h`.
- MAC/PHY integration headers: `d11.h`, `phy_shim.h`, `phy_int.h`, `phy_hal.h`, `phy_radio.h`, `phyreg_n.h`, and `phytbl_n.h`.

The macro and table definitions depend heavily on symbols defined elsewhere:

- `read_radio_reg()`, `write_radio_reg()`, and `read_phy_reg()` are used by macros but implemented outside this chunk.
- Register token names such as `radio_type##_##jspace##_##reg_name` and `radio_type##_##SYN##_##reg_name` come from radio register headers.
- PHY revision helpers such as `NREV_GE()` and fields under `pi->pubpi.phy_rev` come from the PHY core structures.
- `struct brcms_phy`, `struct brcms_phy_pub`, and `struct nphy_txgains` are referenced or embedded but defined outside this chunk.

## Important APIs, Types, and Data

### Register Access Macros

Lines 25-60 define token-pasting helpers for multi-core radio register addressing:

- `READ_RADIO_REG2()` and `WRITE_RADIO_REG2()` build register addresses using a radio type, register-space name, core selector, and register name. They OR the selected core namespace into a common register token.
- `WRITE_RADIO_SYN()` writes synthesizer-space registers.
- `READ_RADIO_REG3()` / `WRITE_RADIO_REG3()` and `READ_RADIO_REG4()` / `WRITE_RADIO_REG4()` support alternate radio register naming layouts where the core number appears in a different token position.

These are not public APIs, but later code likely uses them to hide radio-family register naming differences while programming core 0/core 1 paths.

### Calibration and Control Constants

Lines 62-168 define N-PHY constants for:

- Adjacent-channel interference detection windows and channel skip/delta thresholds.
- Noise and glitch thresholds for associated and unassociated states.
- RSSI calibration limits, sign extension, and violation checks.
- IQ calibration gain count, PAPD table sizes, and digital filter coefficient count.
- SROM temperature offset interpretation and maximum calibration temperature delta.
- Noise variance table lengths for 20 MHz and 40 MHz modes.
- RX/TX calibration tone frequency and amplitude constants.
- TX filter mode identifiers for OFDM20, OFDM40, CCK, and default filters.
- 5357 chip-control bits for external PA and antenna mux behavior.

These constants are part of the persistent hardware policy for later runtime decisions. Changing them changes calibration acceptance, noise mitigation, and RF programming behavior.

### Local Structs

The chunk defines several local table/restore-state shapes:

- `struct nphy_iqcal_params`: TX low-pass filter, TX gain mixer, PGA, PAD, IPA, calibration gain, and five correction values for IQ calibration.
- `struct nphy_txiqcal_ladder`: compact TX IQ calibration ladder row with percentage and envelope gain.
- `struct nphy_ipa_txcalgains`: wraps `struct nphy_txgains` with a flag/index pair for table-indexed IPA TX calibration.
- `struct nphy_papd_restore_state`: per-core and shared state snapshot for PAPD restoration, including feedback mixer, VGA, internal PA, AFE control/override, power-up, attenuation, and multiplier state.
- `struct nphy_ipa_txrxgain`: RX calibration gain tuple with HPVGA, LPF BIQ stages, LNA2/LNA1, and TX power index.
- `struct chan_info_nphy_2055`: channel/frequency row for radio 2055, including PLL values, local-generator tuning, per-core RX/TX values, and six PHY bandwidth values.
- `struct chan_info_nphy_radio205x`: channel/frequency row for radio 2056-class programming, including synthesizer PLL fields, reserved synthesizer addresses, logen fields, per-core RX/TX tune/boost values, and six PHY bandwidth values.
- `struct chan_info_nphy_radio2057` and `struct chan_info_nphy_radio2057_rev5`: alternate row layouts for later 2057 tables, defined here but not populated in this chunk.
- `struct nphy_sfo_cfg`: a smaller PHY bandwidth-only row.

### Static Tables Present in This Chunk

The chunk includes several static tables:

- `nphy_ipa_rxcal_gaintbl_5GHz[]`, `nphy_ipa_rxcal_gaintbl_2GHz[]`, `nphy_ipa_rxcal_gaintbl_5GHz_rev7[]`, and `nphy_ipa_rxcal_gaintbl_2GHz_rev7[]`: IPA RX calibration gain ladders for band and revision combinations.
- `NPHY_IPA_REV4_txdigi_filtcoeffs[][15]`: seven sets of TX digital filter coefficients for IPA rev4 paths.
- `chan_info_nphy_2055[]`: complete channel tuning table for radio 2055, covering 5 GHz channels from 184 through 228 and 32 through 182, plus 2.4 GHz channels 1 through 14.
- `chan_info_nphyrev3_2056[]`: complete radio 2056 table for N-PHY rev3.
- `chan_info_nphyrev4_2056_A1[]`: complete radio 2056 A1 table for N-PHY rev4.
- `chan_info_nphyrev5_2056v5[]`: complete radio 2056v5 table for N-PHY rev5.
- `chan_info_nphyrev6_2056v6[]`: complete radio 2056v6 table for N-PHY rev6.
- `chan_info_nphyrev5n6_2056v7[]`: complete radio 2056v7 table shared by rev5/rev6 paths.
- `chan_info_nphyrev6_2056v8[]`: complete radio 2056v8 table for rev6.
- `chan_info_nphyrev6_2056v11[]`: begins in this chunk but is incomplete at line 4811.

The `chan_info_*` tables are mostly dense numeric literals. The semantic contract is carried by the struct field order, so row/field alignment is critical.

## Control Flow

There is no direct executable control flow in lines 1-4811. The only conditional logic is in macro expansion:

- Core selection in `READ_RADIO_REG2()`/`WRITE_RADIO_REG2()` chooses core 0 or core 1 register namespaces.
- The RSSI violation macros compare calibrated RSSI values against upper/lower tolerances.
- `NPHY_IS_SROM_REINTERPRET` expands to a PHY revision check.

The runtime control flow using this chunk is expected to happen later in the file:

1. A channel set or initialization routine identifies radio type/revision and channel.
2. It selects the matching `chan_info_*` table.
3. It searches for the matching `chan`/`freq` row.
4. It writes synthesizer, RX/TX, and PHY bandwidth values from that row through radio/PHY register helpers.
5. Calibration routines select gain/filter tables based on band, revision, IPA presence, and calibration mode.

## State and Persistence Behavior

The chunk itself defines no mutable global state. Most objects are `static const`, so they are read-only kernel text/data inputs after compilation.

Persistence is hardware-facing rather than file-backed:

- Register macros write values into radio/PHY hardware state through driver helpers.
- The table values represent stable default hardware programming for channel changes and calibration.
- `struct nphy_papd_restore_state` is a transient in-memory snapshot type used later to restore PAPD-related register state after calibration or measurement changes.

Any future edit to the numeric tables effectively changes persistent device behavior across boots because these constants are compiled into the driver.

## Integration Points

This chunk integrates with:

- The Linux wireless driver build via `pr_fmt()` and kernel headers.
- Broadcom chip/bus helpers for chip IDs, PMU, chipcommon, and AI backplane access.
- The brcmsmac PHY abstraction through `phy_int.h`, `phy_hal.h`, `phy_radio.h`, `phyreg_n.h`, and `phytbl_n.h`.
- Later N-PHY routines in this same file that likely implement attach/init, channel switching, radio initialization, calibration, TX power control, RSSI calibration, PAPD, and workarounds.
- Register definition headers that must match the token-pasting macro naming schemes.

The line-anchored table starts show the intended revision split: radio 2055 data starts at line 438, radio 2056 rev3 at 937, rev4 A1 at 1560, rev5/v5 at 2183, rev6/v6 at 2806, rev5/6 v7 at 3429, rev6/v8 at 4052, and rev6/v11 at 4675.

## Risks and Edge Cases

- Numeric table field order is fragile. A missing value, extra value, or wrong field alignment will silently program the wrong hardware register.
- The register macros rely on token pasting against names defined in headers. Register renames or new radio layouts can fail at compile time or, worse, select the wrong token pattern if reused incorrectly.
- The `u16` filter coefficient table stores negative literals in unsigned elements. This likely relies on two's-complement wraparound for hardware coefficient encoding; readers must not "fix" these to signed types without checking the downstream table writer.
- Channel tables duplicate many rows across revisions with small differences. Manual edits are high risk because a one-nibble change can affect a narrow channel/revision only.
- The chunk boundary cuts `chan_info_nphyrev6_2056v11[]` mid-table. Whole-file reconciliation must verify the final table closes correctly in the next chunk and that consumers never see a partially documented revision map.
- The constants include regulatory-adjacent and RF-behavior-affecting values such as TX power calibration, external PA, noise thresholds, and channel tuning. Behavioral validation needs actual hardware or a trusted golden register trace.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Kernel build catches struct initializer arity/type errors, token-pasting register name mismatches, and missing external symbols.
- Static checks can verify each complete `chan_info_*` array has expected channel coverage, especially 2.4 GHz channels 1-14 and the 5 GHz channel list used by this driver.
- Channel-switch tests on supported Broadcom N-PHY hardware should compare programmed radio/PHY registers against known-good traces for each radio revision.
- Calibration smoke tests should exercise IPA RX gain tables, TX digital filter coefficient loading, RSSI calibration limits, and PAPD restore behavior.
- Regression tests should specifically cover radio 2055, 2056 rev3/rev4/rev5/rev6/v7/v8/v11 paths because this chunk encodes distinct table families for them.

## Cross-Chunk Notes

Later chunks need to identify the functions that consume these tables and constants. In particular, look for channel lookup and radio-programming routines that reference `chan_info_nphy_2055`, `chan_info_nphyrev3_2056`, `chan_info_nphyrev4_2056_A1`, `chan_info_nphyrev5_2056v5`, `chan_info_nphyrev6_2056v6`, `chan_info_nphyrev5n6_2056v7`, `chan_info_nphyrev6_2056v8`, and `chan_info_nphyrev6_2056v11`. The final per-file synthesis should connect those consumers to `wlc_phy_chanspec_set_nphy()` and radio init/calibration paths if confirmed in later lines.

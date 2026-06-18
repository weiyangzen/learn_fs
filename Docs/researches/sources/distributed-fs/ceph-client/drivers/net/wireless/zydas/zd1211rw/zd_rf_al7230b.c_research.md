# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al7230b.c

## Purpose
Implements RF programming for the Airoha AL7230B transceiver. It supports both original ZD1211 and ZD1211B register sequences, including new/old PHY layout differences and a ZD1211B-specific 6M band-edge patch.

## Important APIs, Types, And Functions
Exports `zd_rf_init_al7230b()`. Internal functions include `zd1211_al7230b_init_hw()`, `zd1211b_al7230b_init_hw()`, `zd1211_al7230b_set_channel()`, `zd1211b_al7230b_set_channel()`, radio on/off helpers, `zd1211b_al7230b_finalize()`, and `zd1211b_al7230b_patch_6m()`. Tables `chan_rv`, `std_rv`, `rv_init1`, `rv_init2`, and `ioreqs_sw` encode common RF and BBP programming.

## Control Flow
Initialization writes AL7230B-specific CR values, RF standard words, channel-1 values, PLL cycles, and final CR203/CR240 state. ZD1211B setup branches on `chip->new_phy_layout` for several CR values. Channel switching powers PLL down, rewrites standard RF words and channel words, applies switch registers, powers PLL back on, and finalizes. Radio on/off uses CR11 plus CR251 generation-specific PLL values.

## State And Persistence
No private heap state. The selected callback set persists in `struct zd_rf`; chip fields `new_phy_layout` and generation determine programming. Non-B ZD1211 enables CCK gain patching, while B uses a custom `patch_6m_band_edge`.

## Dependencies And Integration Points
Uses common RF/chip locked register helpers and is selected by `AL7230B_RF` from EEPROM. It relies on chip-level channel calibration and optional 6M patch invocation.

## Risks
Many values differ subtly from AL2230 despite comments noting similarity. Channel 11 band-edge logic is explicitly flagged as regulatory-domain sensitive. New/old PHY detection changes RF performance. Finalization must reapply CR203 after a split write marker.

## Test Signals
Probe AL7230B on ZD1211 and ZD1211B with old/new PHY layouts, switch all 2.4 GHz channels, validate channel 1/11 edge behavior, run AP beacon/TX tests after channel changes, and confirm radio power toggles leave PLL state usable.

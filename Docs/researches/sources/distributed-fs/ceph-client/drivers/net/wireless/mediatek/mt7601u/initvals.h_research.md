# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals.h

## Purpose
Holds static BBP and MAC register initialization tables for MT7601U hardware startup.

## Important APIs, Types, And Functions
Defines arrays `bbp_common_vals`, `bbp_chip_vals`, `mac_common_vals`, and `mac_chip_vals`, each containing `struct mt76_reg_pair` entries consumed by initialization code. The values configure BBP AGC/sync/RX/CCK controls, GLRT indexed registers, MAC basic rates, filters, backoff/timeout/protection, PBF/FCE, TX power attenuation, and beacon offsets.

## Control Flow
No executable flow. `init.c` writes these tables through `mt7601u_write_reg_pairs()` during hardware initialization.

## State And Persistence
The arrays are static const data. Their values persist in hardware registers after init until reset or later runtime configuration changes.

## Dependencies And Integration Points
Depends on MT7601U register definitions and `struct mt76_reg_pair`. Used by `mt7601u_init_bbp()` and `mt7601u_write_mac_initvals()`.

## Risks
Magic register values encode vendor hardware knowledge. A wrong value can break RX sensitivity, TX protection, DMA buffering, or beacon memory layout. Some later runtime code assumes these defaults before applying channel or association changes.

## Test Signals
Successful BBP/MAC initialization, association stability, expected RX filter/protection defaults, sane aggregation behavior, and no regressions when comparing register dumps with known-good vendor values.

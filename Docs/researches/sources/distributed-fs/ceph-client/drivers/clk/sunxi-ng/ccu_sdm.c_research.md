# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_sdm.c

## Purpose
`ccu_sdm.c` supports sigma-delta modulation helper paths for exact audio PLL rates where the hardware pattern is table-driven rather than algorithmically derived.

## Important APIs, Types, And Functions
Important APIs are `ccu_sdm_helper_is_enabled()`, `enable()`, `disable()`, `has_rate()`, `read_rate()`, and `get_factors()`, exported in the `SUNXI_CCU` namespace.

## Control Flow
Enable writes the matching pattern to the tuning register, sets the tuning enable bit, then sets the PLL SDM enable bit if present. Disable clears both enables. Rate reads match current pattern plus M/N factors against the table because generic effective-rate calculation is not known.

## State And Persistence
State is hardware SDM enable bits and tuning pattern registers. The supported rate table is static descriptor data.

## Dependencies And Integration Points
It depends on CCF debug names, MMIO, spinlocks, and `ccu_common`. It integrates with `ccu_nm` audio PLL descriptors.

## Risks
The code intentionally supports only table-known rates, mainly 22.5792 MHz and 24.576 MHz audio-family rates. Unknown patterns read as 0, so changing vendor pattern values needs hardware validation.

## Test Signals
Test with audio playback/capture at 44.1 kHz and 48 kHz families, clk-summary rate readback, and transitions between SDM and non-SDM rates.

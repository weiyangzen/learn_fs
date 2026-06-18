# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.c

Purpose: shared utility implementation, currently focused on dB/linear power conversion and bounded text truncation.

Important APIs/functions: `rtw89_linear_to_db_quarter()` binary-searches a large lookup table and returns the closest quarter-dBm value. `rtw89_linear_to_db()` converts to whole dBm. `rtw89_db_quarter_to_linear()` clamps a quarter-dBm input and maps it to micro-scaled linear power. `rtw89_db_to_linear()` accepts whole dBm. `rtw89_might_trailing_ellipsis()` replaces the end of a filled string buffer with `...`.

Control flow: dB conversion uses `RTW89_MIN_DBM`, `RTW89_MAX_DBM`, and a table offset so negative quarter-dBm values can index the inverse table. Out-of-range linear values clamp to min/max; between entries choose the nearest table value.

State and persistence: static immutable lookup table only; no mutable state.

Dependencies/integration: exported symbols are used by SAR/TAS rolling average power logic and potentially diagnostics. Ellipsis helper supports fixed-size debug/report buffers.

Risks: the table encodes numerical behavior; changing entries affects TAS thresholds and RF power decisions. Floating-looking macro expressions are folded into integer constants but should be handled carefully. Binary search assumes a sorted table.

Test signals: unit-style conversion checks around min/max/zero-ish values, monotonicity tests, round-trip dB-to-linear-to-dB tolerances, and debug buffer truncation cases.

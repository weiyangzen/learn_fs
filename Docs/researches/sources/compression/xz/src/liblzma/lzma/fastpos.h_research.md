# sources/compression/xz/src/liblzma/lzma/fastpos.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos.h -->
## sources/compression/xz/src/liblzma/lzma/fastpos.h

### Purpose
`fastpos.h` provides fast conversion from LZMA match distances to six-bit distance-slot values, a compact two-bit-style bit-scan encoding used in LZMA distance coding and dictionary-size property coding.

### Important APIs, Types, And Functions
In small builds, `get_dist_slot()` and `get_dist_slot_2()` use `bsr32()`. In normal builds, the hidden `lzma_fastpos` table, `FASTPOS_BITS`, `fastpos_shift()`, `fastpos_limit()`, `fastpos_result()`, `get_dist_slot()`, and optionally `get_dist_slot_2()` provide table-based lookup.

### Control Flow
Small distances are table lookups. Larger distances are shifted down by calibrated amounts before lookup and then adjusted by twice the shift. `get_dist_slot_2()` assumes the distance is at least `FULL_DISTANCES` and uses a different base shift to speed distance coding after fully modeled distances.

### State, Persistence, And Dependencies
There is no mutable state. Normal builds depend on `fastpos_table.c` providing `lzma_fastpos`; small builds depend on `bsr32()`. `FULL_DISTANCES_BITS` is supplied by `lzma_common.h` when the specialized helper is needed.

### Integration Points
LZMA encoders use this for match distance slot coding. LZMA2 property encoding also uses `get_dist_slot()` to encode dictionary size.

### Risks
Slot mapping must exactly match LZMA format rules. Build configuration changes can switch between BSR and table behavior, so both paths must be equivalent. `get_dist_slot_2()` requires its precondition.

### Test Signals
Tests should compare both paths over representative distances, all boundaries shown by the table, dictionary-size property values, and full-distance thresholds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos.h -->

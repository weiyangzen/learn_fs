# sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c -->
## sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c

### Purpose
`fastpos_tablegen.c` generates the `lzma_fastpos[]` lookup table used by `fastpos_table.c`.

### Important APIs, Types, And Functions
The standalone `main()` includes `fastpos.h`, fills a local `fastpos[1 << FASTPOS_BITS]`, and prints a C source file containing the table.

### Control Flow
The generator seeds slots 0 and 1, then iterates distance-slot values from 2 to `2 * FASTPOS_BITS - 1`. For each slot, it repeats that slot value `1 << ((slot_fast >> 1) - 1)` times, matching the LZMA distance-slot range geometry. It prints SPDX/header text and formats 16 entries per line.

### State, Persistence, And Dependencies
State is local to the generator. It depends on `FASTPOS_BITS` from `fastpos.h` and standard C I/O headers.

### Integration Points
This file is distributed as a maintenance tool and not normally compiled into liblzma. Its output is checked into `fastpos_table.c`.

### Risks
Changing `FASTPOS_BITS` without regenerating the table breaks lookup bounds or semantics. The generator prints source to stdout, so build scripts must redirect output intentionally.

### Test Signals
Run the generator, diff against `fastpos_table.c`, and compare selected generated slots against `get_dist_slot()` expectations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c -->

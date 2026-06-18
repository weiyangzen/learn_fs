# sources/distributed-fs/moosefs/mfschunkserver/chartsdefs.h

## Purpose
`chartsdefs.h` defines the chunkserver chart schema: the persisted filename, numeric chart indexes, stat ids, aggregation modes, scaling rules, calculated metrics, and exported multi-series chart definitions. It is shared by the daemon and stats dump tool.

## Important Definitions
`CHARTS_FILENAME` is `csstats.mfs`. `CHARTS_*` constants assign indexes `0..47` for CPU, master traffic, replication traffic, client traffic, HDD read/write bytes and operations, high-level operations, read/write time, replication count, chunk operation counts, load, memory, movement, space, chunk counts, chunk layout categories, disk state counts, and usage difference. `CHARTS` is `48`.

`STRID(a,b,c,d)` packs four characters into a 32-bit stat id. `STATDEFS` maps each raw chart name to stat id, aggregation mode (`CHARTS_MODE_ADD` or `CHARTS_MODE_MAX`), percent flag, scale, multiplier, and divisor. `CALCDEFS` defines calculated series for virtual-minus-RSS memory and free space (`TSPACE - USPACE`) clamped at zero. `ESTATDEFS` defines exported aggregate charts such as `cpu`, `bwin`, `bwout`, `hddread`, `hddwrite`, `hddopsr`, `hddopsw`, `mem`, `move`, `space`, `chunks`, and `hddcnt`.

## Control Flow and Integration
This header has no executable flow, but its macros instantiate `statdef`, `estatdef`, and calculation arrays in `chartsdata.c`; `Makefile.am` also includes it in the stats dump utility. The index constants are used by `chartsdata_refresh` to fill the data array.

## State and Persistence
The schema defines the meaning of persisted `csstats.mfs` samples. Any reordering or id/name change affects compatibility with existing chart history and tools. Adding a metric requires increasing `CHARTS`, assigning a new index, extending `STATDEFS`, and updating producers.

## Dependencies
The macro bodies use chart subsystem constants and macros such as `CHARTS_MODE_ADD`, `CHARTS_SCALE_MICRO`, `CHARTS_CALCDEF`, `CHARTS_MAX`, `CHARTS_SUB`, `CHARTS_DIRECT`, and `CHARTS_DEFS_END`, so includers must include or otherwise know the common chart definitions.

## Risks
The largest risk is positional drift. `CHARTS_*` indexes, `CHARTS` count, `STATDEFS`, and `chartsdata_refresh` must evolve together. Scale multipliers/divisors encode units and rates; a wrong divisor can silently produce misleading operational dashboards. The `STRID` macro casts characters to `uint8_t`, so it relies on fixed-width types being visible in includers.

## Test Signals
Signals include successful compilation of `chartsdata.c` and `mfscsstatsdump`, chart dump output with all expected names, persisted chart files readable after upgrades, and tests that compare the number of raw definitions against `CHARTS`. Adding metrics should include a compatibility check for old `csstats.mfs` files.

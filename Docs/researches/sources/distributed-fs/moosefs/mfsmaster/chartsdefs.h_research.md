# sources/distributed-fs/moosefs/mfsmaster/chartsdefs.h

`chartsdefs.h` defines the mfsmaster chart schema: stable chart indexes, persistent filename, raw statistic descriptors, calculated descriptors, and extended multi-series descriptors shared by the producer and stats dump tooling.

It defines `CHARTS_FILENAME` as `stats.mfs`, chart index constants from `CHARTS_UCPU` through `CHARTS_MOUNTS_BYTES_SENT`, total `CHARTS` as 70, `STRID` for four-byte stat identifiers, and the macros `STATDEFS`, `CALCDEFS`, and `ESTATDEFS`.

`chartsdata.c` expands these macros into arrays passed to `charts_init`; `mfsstatsdump` includes the same file to interpret persisted chart data. Calculated definitions derive virtual memory overhead, free space, active servers, and disconnected non-marked servers. Extended definitions group related raw series such as CPU, memory, space, chunk operation status, objects, chunk health, and chunkserver states.

This header is the schema contract for `stats.mfs`. Renumbering indexes or changing stat IDs can affect compatibility with existing stats files and tools. Dependencies are the common chart-engine macros and constants.

Risks are index drift between producer assignments and definitions, incomplete updates when adding metrics, and compatibility breaks for old stats files. Test signals include chart initialization with these definitions, dumping known `stats.mfs` files, verifying names and stat IDs, and checking that produced indexes below `CHARTS` have intended definitions.

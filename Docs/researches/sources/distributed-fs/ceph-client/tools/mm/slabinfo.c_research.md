# sources/distributed-fs/ceph-client/tools/mm/slabinfo.c

Purpose: Reports and optionally manipulates SLUB slab cache state exposed through `/sys/kernel/slab` or `/sys/slab`, with detailed totals, sorting, NUMA, activity, debug, validation, and shrink modes.

Important APIs and types: `struct slabinfo` mirrors many slab sysfs attributes, while `struct aliasinfo` maps symlink aliases to target slabs. Key routines include `read_slab_dir`, `link_slabs`, `rename_slabs`, `slabcache`, `report`, `totals`, `xtotals`, `slab_numa`, `show_tracking`, `slab_stats`, `slab_debug`, `slab_validate`, `slab_shrink`, and `sort_slabs`.

Control flow: `main` parses display/action/sort/debug options and an optional regex, reads all matching slab directories and aliases, then selects alias display, extended totals, simple totals, or per-slab output/action. Reading gathers sysfs attributes including object counts, NUMA lists, debug flags, and allocator counters. Some modes write to attributes such as `validate`, `shrink`, `sanity_checks`, `red_zone`, `poison`, `store_user`, and `trace`.

State and persistence behavior: Reporting is in-memory and stdout-only, but validation, shrinking, and debug toggles persist by writing kernel sysfs controls. Current working directory is changed into the slab sysfs root.

Dependencies and integration points: Consumes SLUB sysfs/debugfs layouts and optional `/sys/kernel/debug/slab/*` trace files. `slabinfo-gnuplot.sh` expects `-X` extended totals text.

Risks: Global fixed arrays cap slabs, aliases, and NUMA nodes. Sysfs attributes vary by kernel configuration. Debug toggles require empty slabs and privileges. The code has historical style and limited cleanup because process exit reclaims memory.

Test signals: Exercise default list, regex filtering, aliases, totals/extended totals, NUMA, activity, top-N, debug toggle failure on nonempty slabs, validate/shrink on test systems, and gnuplot preprocessing compatibility.

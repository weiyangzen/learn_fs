# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap_flags.sh

Purpose: Generates a flag-indexed C table for `MAP_*` mmap flags across generic and architecture-specific headers.

Important APIs/types/functions: It emits `static const char *mmap_flags[]` plus compatibility `#ifndef MAP_*` definitions for found flags. It accepts either host architecture or explicit linux/generic/arch header directories.

Control flow: The script derives host arch when needed, parses architecture `mman.h`, Linux `mman.h`, `mman-common.h`, and generic `mman.h` depending on include relationships, excludes `MAP_UNINITIALIZED`, `MAP_TYPE`, and `MAP_SHARED_VALIDATE`, and indexes each flag as `ilog2(value) + 1`.

State and persistence: Output goes to stdout. It has no runtime state.

Dependencies and integration points: Output is included by `mmap.c`; `ilog2` indexing relies on `<linux/log2.h>` in the C consumer.

Risks: Non-power-of-two masks are unsuitable for this table and are filtered only for known cases. Duplicate generic/arch definitions may produce repeated slots.

Test signals: Regenerate on x86 and at least one non-x86 architecture header set, then compile and trace `mmap` flag combinations.

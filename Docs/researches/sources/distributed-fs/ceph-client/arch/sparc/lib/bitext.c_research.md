# sources/distributed-fs/ceph-client/arch/sparc/lib/bitext.c

Purpose: Simple bitmap allocator utilities for SPARC bit-map structures.

Important APIs/functions: Defines `bit_map_string_get`, `bit_map_clear`, and `bit_map_init`.

Control flow: `bit_map_string_get` scans a bitmap for a contiguous zero run of requested length aligned to the requested boundary, marks it allocated, and returns offset or `-1`. `bit_map_clear` clears a range. `bit_map_init` initializes metadata and clears the backing bitmap.

State and persistence: Mutates the caller-provided `struct bit_map` backing bitmap and metadata counters.

Dependencies/integration: Includes `linux/string.h`, `linux/bitmap.h`, and `asm/bitext.h`.

Risks/test signals: Off-by-one range scans and alignment handling are primary risks. Test allocation/free cycles, full maps, exact-size allocations, alignment > 1, and fragmentation behavior.

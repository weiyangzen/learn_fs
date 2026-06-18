# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.c

Purpose: core libfdt validation, low-level structure traversal, offset access, string-table search, and blob relocation.

Important APIs/functions: `fdt_ro_probe_()` performs minimal read-only sanity checks, including 8-byte alignment, magic, version, and `totalsize`. `fdt_header_size_()` and `fdt_header_size()` resolve versioned header length. `fdt_check_header()` performs stronger header and block-bound checks. `fdt_offset_ptr()` bounds-checks structure-block ranges. `fdt_next_tag()` parses FDT tags and computes aligned next offsets. `fdt_check_node_offset_()` and `fdt_check_prop_offset_()` validate structural offsets. `fdt_next_node()`, `fdt_first_subnode()`, and `fdt_next_subnode()` implement depth-aware traversal. `fdt_find_string_len_()` scans string tables. `fdt_move()` relocates blobs with overlap-safe `memmove`.

Control flow/state: stateless over caller-provided blobs. Behavior is heavily gated by `can_assume()` masks; enabling assumptions skips validation paths.

Dependencies/integration: central dependency for read-only, read-write, overlay, and sequential-write modules. Uses raw structures from `fdt.h`, exported macros from `libfdt.h`, and assumptions/helpers from `libfdt_internal.h`.

Risks: assumption masks trade safety for size/performance and can turn malformed input into undefined behavior. Offset arithmetic and FDT version handling are critical security surfaces. `fdt_next_tag()` returns `FDT_END` both for true end and some malformed cases while encoding details in `nextoffset`.

Test signals: unaligned input, bad magic/version, truncated sections, malformed tags, old-version property alignment, traversal depth edge cases, subnode iteration, string-table searches, and overlapping `fdt_move()`.

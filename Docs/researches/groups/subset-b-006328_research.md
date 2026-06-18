# subset-b-006328 research

Grouped research for the DTC/libfdt files listed in work item `subset-b-006328`. Each section is source-path aligned for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fdtoverlay.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/fdtoverlay.c

Purpose: command-line utility that applies one or more compiled device-tree overlays (`.dtbo`) to a base DTB and writes a packed output DTB. It is a thin orchestration layer over libfdt overlay APIs.

Important APIs/functions: `main()` parses `-i`, `-o`, `-v` via `util_getopt_long`; `do_fdtoverlay()` reads the base and overlay blobs with `utilfdt_read`, validates read lengths against `fdt_totalsize`, applies overlays sequentially, packs with `fdt_pack`, and writes with `utilfdt_write`; `apply_one()` expands a working buffer in 64 KiB increments, copies the overlay because `fdt_overlay_apply()` invalidates inputs on failure, checks whether the base has `/__symbols__`, and retries only on `-FDT_ERR_NOSPACE`.

Control flow/state: the current base blob pointer is replaced after each successful overlay. `buf_len` persists as the mutable capacity across overlays. On success ownership of the old base is freed; on failure temporary base/overlay copies are freed and the original call unwinds.

Dependencies/integration: depends on `libfdt.h` for `fdt_open_into`, `fdt_overlay_apply`, `fdt_path_offset`, `fdt_pack`, `fdt_strerror`; on `util.h` for I/O, allocation, and common usage handling. It is an end-user wrapper around `libfdt/fdt_overlay.c`.

Risks: failure paths must assume both base and overlay may be corrupted, hence the copy discipline is important. Missing base symbols produce confusing overlay fixup failures, so the explicit `-@` diagnostic is important. `verbose` is global but only affects CLI printing here.

Test signals: exercise applying overlays with phandle and path targets, insufficient output space retry, missing `/__symbols__` diagnostics, incomplete blob read rejection, multi-overlay sequencing, and output repacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fdtoverlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fdtput.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/fdtput.c

Purpose: command-line utility for editing a DTB in place on disk by setting a property value or creating nodes.

Important APIs/functions/types: `enum oper_type` distinguishes property writes from node creation. `struct display_info` carries operation, type, element size, verbosity, and auto-path creation. `encode_value()` converts CLI strings into a raw property payload using util-decoded type/size, defaulting to 32-bit cells. `store_key_value()` resolves a node path then calls `fdt_setprop`. `create_paths()` walks path components and creates missing subnodes. `create_node()` splits parent/name and calls `fdt_add_subnode`. `do_fdtput()` reads the blob, dispatches the operation, and writes it back.

Control flow/state: `main()` validates arguments and flags, then `do_fdtput()` mutates the loaded blob and persists it only if all requested changes succeed. Auto-path mode can create intermediate nodes before writing the property or create full paths directly for node creation.

Dependencies/integration: uses libfdt read/write mutators and DTC util helpers for blob I/O and type parsing. It assumes the input blob has sufficient writable slack; unlike `fdtoverlay`, it does not grow via `fdt_open_into`.

Risks: `encode_value()` uses `int *` stores into a char buffer for 32-bit values, so alignment assumptions follow local platform behavior. Only one-byte and four-byte integer paths are fully stored despite accepting size metadata; two-byte values are effectively truncated through the byte path. `create_node()` temporarily writes NUL into the node path string.

Test signals: property writes for string/int/hex types, empty values, `-p` auto path creation, `-c` node creation, insufficient DTB space, missing parent diagnostics, and malformed type strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fdtput.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/flattree.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/flattree.c

Purpose: converts DTC's in-memory `dt_info`/`node` tree to flattened device-tree binary or assembly output, and parses DTB input back into the live tree representation.

Important APIs/functions: version metadata in `version_table` controls FDT versions 1, 2, 3, 16, and 17. `struct emitter` abstracts binary vs assembly emission. `flatten_tree()` emits node tags, names, properties, synthetic legacy `name` properties, string-table entries, alignment, and children. `flatten_reserve_list()` serializes reserve entries plus requested expansion slots. `make_fdt_header()` lays out header offsets and size fields. Public emitters are `dt_to_blob()` and `dt_to_asm()`. Read-side helpers `struct inbuf`, `flat_read_*`, `flat_read_property()`, `flat_read_mem_reserve()`, and `unflatten_tree()` feed public `dt_from_blob()`.

Control flow/state: output is staged in `struct data` buffers for reserve map, structure block, strings, and final blob. Global DTC options `reservenum`, `minsize`, `padsize`, `alignsize`, and `quiet` affect layout and diagnostics. Input parsing reads the full `totalsize`, validates section offsets, chooses legacy flags by version, then recursively rebuilds nodes.

Dependencies/integration: depends on `dtc.h` tree/data APIs, `srcpos`, `fdt.h` structs/constants, endian helpers, and source-file open helpers. It is the main bridge between DTC parsing and libfdt-compatible DTB bytes.

Risks: string-table insertion is O(n). Old-version alignment and full-path semantics are subtle. `dt_from_blob()` validates bounds manually but exits via `die()` rather than returning errors. Malformed ordering of properties after subnodes is tolerated with a warning during unflattening.

Test signals: round trips for all supported FDT versions, reserve maps, legacy full-path/name-property blobs, NOP tags, padding/alignment/minsize options, assembly labels, malformed offset bounds, and plugin marker detection through `__fixups__`/`__local_fixups__`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/flattree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fstree.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/fstree.c

Purpose: imports a filesystem directory tree as a DTC live device tree, with directories becoming nodes and regular files becoming properties.

Important APIs/functions: `read_fstree()` recursively opens a directory, skips `.` and `..`, stats entries, reads regular files with `data_copy_file()` into `build_property()`, descends into subdirectories, names child nodes with their directory entry names, and appends properties/children. `dt_from_fs()` names the root node `""`, computes boot CPU ID with `guess_boot_cpuid()`, and returns `build_dt_info(DTSF_V1, NULL, tree, ...)`.

Control flow/state: no persistent state beyond the constructed `struct node` graph. Processing order follows directory iteration order, so deterministic output depends on later sorting if callers require it.

Dependencies/integration: uses POSIX `opendir`, `readdir`, `stat`, `fopen`, and DTC tree/data helpers from `dtc.h`. It integrates with the same `dt_info` pipeline used by DTS and DTB inputs.

Risks: unreadable regular files are warned and skipped, while `opendir`/`stat` failures are fatal. Non-regular non-directory entries are ignored. Property names come directly from filenames, so invalid device-tree property names are not filtered here.

Test signals: directory-to-node recursion, file contents preserved as property bytes, unreadable file warning behavior, symlink/device entry handling, root naming, and downstream sort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fstree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.c

Purpose: core libfdt validation, low-level structure traversal, offset access, string-table search, and blob relocation.

Important APIs/functions: `fdt_ro_probe_()` performs minimal read-only sanity checks, including 8-byte alignment, magic, version, and `totalsize`. `fdt_header_size_()` and `fdt_header_size()` resolve versioned header length. `fdt_check_header()` performs stronger header and block-bound checks. `fdt_offset_ptr()` bounds-checks structure-block ranges. `fdt_next_tag()` parses FDT tags and computes aligned next offsets. `fdt_check_node_offset_()` and `fdt_check_prop_offset_()` validate structural offsets. `fdt_next_node()`, `fdt_first_subnode()`, and `fdt_next_subnode()` implement depth-aware traversal. `fdt_find_string_len_()` scans string tables. `fdt_move()` relocates blobs with overlap-safe `memmove`.

Control flow/state: stateless over caller-provided blobs. Behavior is heavily gated by `can_assume()` masks; enabling assumptions skips validation paths.

Dependencies/integration: central dependency for read-only, read-write, overlay, and sequential-write modules. Uses raw structures from `fdt.h`, exported macros from `libfdt.h`, and assumptions/helpers from `libfdt_internal.h`.

Risks: assumption masks trade safety for size/performance and can turn malformed input into undefined behavior. Offset arithmetic and FDT version handling are critical security surfaces. `fdt_next_tag()` returns `FDT_END` both for true end and some malformed cases while encoding details in `nextoffset`.

Test signals: unaligned input, bad magic/version, truncated sections, malformed tags, old-version property alignment, traversal depth edge cases, subnode iteration, string-table searches, and overlapping `fdt_move()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.h

Purpose: public raw FDT wire-format definitions: header, reserve entries, structure-block records, tag constants, magic, and versioned header sizes.

Important APIs/types/macros: `struct fdt_header` models all versioned header fields through version 17. `struct fdt_reserve_entry` stores 64-bit address/size pairs. `struct fdt_node_header` and `struct fdt_property` model variable-length structure-block entries. Constants include `FDT_MAGIC`, `FDT_TAGSIZE`, tags `FDT_BEGIN_NODE`, `FDT_END_NODE`, `FDT_PROP`, `FDT_NOP`, `FDT_END`, and header sizes `FDT_V1_SIZE` through `FDT_V17_SIZE`.

Control flow/state: no executable logic. The layout types are included by both C and, guarded by `__ASSEMBLER__`, assembly contexts.

Dependencies/integration: requires endian-qualified integer types from `libfdt_env.h` before inclusion through `libfdt.h`. Consumed by all libfdt C modules and DTC flatten/unflatten code.

Risks: these structs define on-disk/on-wire ABI. Field ordering, flexible arrays, and sizes must remain stable. Consumers must always convert `fdt32_t`/`fdt64_t` to CPU endian before arithmetic.

Test signals: compile-time layout expectations, header-size compatibility for all supported versions, tag parsing interoperability, and DTB round-trip tests across endian hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_addresses.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_addresses.c

Purpose: helpers for reading address/size cell counts and appending encoded address ranges to properties.

Important APIs/functions: private `fdt_cells()` reads a named cell-count property, validates exact `fdt32_t` length, converts endian, and enforces `FDT_MAX_NCELLS`. `fdt_address_cells()` returns `#address-cells`, rejects zero, and defaults missing values to 2. `fdt_size_cells()` returns `#size-cells` and defaults missing values to 1. `fdt_appendprop_addrrange()` encodes an address and size as one- or two-cell values according to the parent and appends via `fdt_appendprop()`.

Control flow/state: stateless. The range helper builds a stack buffer of up to two 64-bit values and appends the encoded prefix length determined by cell counts.

Dependencies/integration: relies on read-only `fdt_getprop`, write-side `fdt_appendprop`, endian store helpers `fdt32_st`/`fdt64_st`, and error codes from `libfdt.h`.

Risks: intentionally only supports address and size cell counts of 1 or 2 in `fdt_appendprop_addrrange()`, despite `FDT_MAX_NCELLS` allowing up to 4. It validates 32-bit address overflow including range end overflow for one-cell addresses.

Test signals: missing/default cell counts, malformed property lengths, zero address cells, counts above max, one-cell overflow cases, two-cell encoding, and append failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_addresses.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_empty_tree.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_empty_tree.c

Purpose: convenience constructor for an empty but fully open read-write FDT containing only the root node.

Important APIs/functions: `fdt_create_empty_tree()` chains `fdt_create()`, `fdt_finish_reservemap()`, `fdt_begin_node("")`, `fdt_end_node()`, `fdt_finish()`, and finally `fdt_open_into(buf, buf, bufsize)` to convert the compact sequential-write result into a version-17 mutable blob with remaining buffer space.

Control flow/state: strict sequential-write state transitions: create, reserve-map completion, structure emission, finalization, then read-write reopening. Any error aborts and returns the libfdt negative error code.

Dependencies/integration: depends on `fdt_sw.c` creation APIs and `fdt_rw.c` `fdt_open_into`. Used by callers needing a blank tree before adding nodes/properties.

Risks: in-place `fdt_open_into` must preserve the just-created blob while expanding totalsize to the caller buffer. The function assumes the caller supplied enough aligned memory and handles no allocation itself.

Test signals: tiny buffer `-FDT_ERR_NOSPACE`, valid root-only tree layout, ability to add properties after creation, and preservation of total buffer size for later mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_empty_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_overlay.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_overlay.c

Purpose: implements device-tree overlay application: target resolution, phandle rebasing, external fixup resolution, conflict prevention, overlay merge, and symbol update.

Important APIs/functions: public `fdt_overlay_target_offset()` resolves fragment targets by `target` phandle or `target-path`. Public `fdt_overlay_apply()` performs the full pipeline. Private helpers adjust overlay phandles (`overlay_adjust_local_phandles`), rewrite local references from `/__local_fixups__`, resolve `/__fixups__` through base `/__symbols__`, prevent overwriting base phandles, recursively merge `__overlay__` content, and update base `__symbols__` paths for subsequent overlays.

Control flow/state: `fdt_overlay_apply()` first probes both blobs, finds base max phandle as `delta`, mutates the overlay in place, mutates the base during merge/symbol update, and invalidates the overlay magic on both success and error; on error it also invalidates base magic because partial mutation may have occurred.

Dependencies/integration: uses almost every libfdt traversal and mutation primitive: `fdt_for_each_subnode`, property iterators, `fdt_getprop*`, `fdt_setprop*`, `fdt_add_subnode`, `fdt_path_offset`, phandle helpers, and unaligned `fdt32_ld/st`.

Risks: overlay application is intentionally non-atomic. Malformed fixup strings, invalid offsets, missing symbols, phandle overflow, and insufficient base slack can corrupt working copies. `fdto` must be disposable after calling.

Test signals: phandle and target-path fragments, local fixups, external fixups via symbols, missing symbols, phandle collisions, symbol propagation, nested overlay nodes, root-target paths, malformed fixup properties, and error-time magic invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_ro.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_ro.c

Purpose: read-only libfdt API implementation for string lookup, node/property navigation, phandles, paths, aliases, symbols, compatible/string-list helpers, and reserve-map access.

Important APIs/functions: `fdt_get_string`/`fdt_string`; phandle helpers `fdt_find_max_phandle`, `fdt_generate_phandle`, `fdt_get_phandle`, `fdt_node_offset_by_phandle`; reserve helpers `fdt_get_mem_rsv`, `fdt_num_mem_rsv`; path and node functions `fdt_subnode_offset*`, `fdt_path_offset*`, `fdt_get_name`, `fdt_get_path`, `fdt_parent_offset`; property functions `fdt_first_property_offset`, `fdt_get_property*`, `fdt_getprop*`; alias/symbol helpers; string-list and compatible search APIs.

Control flow/state: stateless traversal over the structure block using `fdt_next_node` and property iterators. Many APIs return pointers into the original blob and communicate errors through negative return values or `lenp`.

Dependencies/integration: built on `fdt.c` probing and tag traversal plus raw endian helpers. It is the read side consumed by overlay, read-write mutation, CLI tools, and external users.

Risks: old FDT versions before 16 require special property realignment and limit some property-structure APIs. Path lookup supports aliases only for non-absolute first components. Several scans are O(tree size) and comments call out suboptimal repeated property scans.

Test signals: string bounds/truncation, alias paths, omitted unit addresses, old-version realignment, parent/path reconstruction, malformed string lists, compatible matching, reserve terminators, and invalid phandle values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_ro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_rw.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_rw.c

Purpose: read-write libfdt API for mutating complete, version-17-compatible DTBs in caller-provided buffers.

Important APIs/functions: `fdt_rw_probe_()` verifies read-write suitability and block order. Splice helpers move bytes in memory and update offsets/sizes for reserve, structure, and string blocks. Public APIs add/delete reserve entries, set node names, set/append/delete properties, add/delete subnodes, open/repack blobs, and normalize layout with `fdt_open_into()`/`fdt_pack()`. `fdt_find_add_string_()` deduplicates or appends property names with rollback support.

Control flow/state: all mutation is in-place and may shift structure offsets, invalidating cached offsets after insertion/deletion. `fdt_open_into()` can convert supported older layout/version into ordered version 17 and expand totalsize to the target buffer. `fdt_pack()` compacts data and shrinks totalsize to actual used bytes.

Dependencies/integration: depends on read-only lookup APIs, `fdt_next_tag`, internal reserve/offset helpers, and assumption masks. CLI tools and overlay application use these mutators.

Risks: caller must provide enough slack or handle `-FDT_ERR_NOSPACE`. Misordered blocks require `fdt_open_into()` before other writes. Rollback of newly added strings can be disabled by `ASSUME_NO_ROLLBACK`, leaving harmless but persistent string-table growth after failed mutations.

Test signals: property resize grow/shrink, append, delete, subnode insertion ordering after properties, node deletion, reserve-map splicing, opening misordered/old blobs, overlapping output buffers, packing, and offset invalidation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_strerror.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_strerror.c

Purpose: maps libfdt integer return codes to stable human-readable strings.

Important APIs/functions/types: `struct fdt_errtabent` stores a string pointer. `FDT_ERRTABENT()` initializes designated entries for every known `FDT_ERR_*` value through `FDT_ERR_ALIGNMENT`. `fdt_strerror()` returns special messages for positive offsets/lengths and zero, table strings for known negative errors, and `<unknown error>` otherwise.

Control flow/state: static immutable table indexed by positive error number after negating the passed error value.

Dependencies/integration: depends on error-code definitions in `libfdt.h`. Used by CLI tools and callers that surface libfdt failures.

Risks: table must stay synchronized with `FDT_ERR_MAX`; missing entries silently report unknown for new errors. Positive libfdt returns are not errors and are deliberately described as valid offsets/lengths.

Test signals: all known negative errors, zero, positive offsets, out-of-range negative codes, and any future error-code additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_strerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_sw.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_sw.c

Purpose: sequential-write API for constructing a new DTB from scratch in a caller-supplied buffer.

Important APIs/functions: probes enforce write states: initial reserve-map state, structure-emission state, and completed state. `fdt_create_with_flags()` initializes an unfinished blob using `FDT_SW_MAGIC` and stores creation flags in `last_comp_version`; `fdt_resize()` safely moves an unfinished blob; `fdt_add_reservemap_entry()` and `fdt_finish_reservemap()` write reserve entries. `fdt_begin_node`, `fdt_end_node`, `fdt_property_placeholder`, `fdt_property`, and string helpers build the structure and reverse-growing strings block. `fdt_finish()` writes `FDT_END`, relocates strings after structure, fixes property name offsets, and restores final magic/version fields.

Control flow/state: state is encoded in header fields. During construction the strings block grows backward from the end of the buffer while the structure block grows forward; `fdt_finish()` compacts them into normal order.

Dependencies/integration: uses `fdt_next_tag`, raw offset helpers, endian macros, and flags from `libfdt.h`. `fdt_empty_tree.c` is a simple consumer.

Risks: calls in the wrong state return `-FDT_ERR_BADSTATE`. Name dedup can be disabled for speed/size tradeoffs. Failed property allocation rolls back newly added strings only if needed and possible.

Test signals: state-machine misuse, buffer exhaustion with forward/backward growth collision, no-name-dedup flag behavior, resize overlap cases, property placeholder writes, finish-time nameoff correction, and final tree validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_wip.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_wip.c

Purpose: work-in-place helpers that modify existing structure bytes without resizing the blob, primarily replacing property values or NOP-ing properties/nodes.

Important APIs/functions: `fdt_setprop_inplace_namelen_partial()` writes a byte range inside an existing property after bounds checking. `fdt_setprop_inplace()` replaces an entire property only when the length is identical. `fdt_nop_region_()` fills a byte range with `FDT_NOP` tags. `fdt_nop_property()` finds a property and NOPs its record. `fdt_node_end_offset_()` computes a subtree end offset via depth traversal. `fdt_nop_node()` NOPs an entire node subtree.

Control flow/state: no block sizes or offsets are changed. NOP operations preserve byte layout while making tags ignored by traversal. In-place set APIs return `-FDT_ERR_NOSPACE` for length mismatches because resizing is outside this module.

Dependencies/integration: uses read-only property lookup, writable pointer helpers, `fdt_next_node`, and endian tag writes. Overlay code uses partial in-place writes for phandle fixups where property sizes are fixed.

Risks: `fdt_nop_property()` uses property value length plus header size without tag alignment padding, so behavior relies on existing layout and traversal tolerance. These APIs are unsuitable for size-changing updates.

Test signals: exact-length replacements, partial unaligned phandle writes, out-of-bounds partial writes, node/property NOP traversal skip behavior, and subtree end calculation on malformed trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_wip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt.h

Purpose: primary public libfdt API header, documenting supported versions, error codes, traversal/read/write/overlay APIs, inline endian helpers, and convenience macros.

Important APIs/types/macros: version constants, `FDT_ERR_*` values, `FDT_MAX_PHANDLE`, unaligned load/store helpers `fdt16_ld`, `fdt32_ld/st`, `fdt64_ld/st`, iteration macros `fdt_for_each_subnode` and `fdt_for_each_property_offset`, header field getters/setters, read-only functions, sequential-write constructors, read-write mutators, typed property helpers, overlay APIs, and `fdt_strerror`.

Control flow/state: no standalone runtime state, but the API contract documents important state effects: sequential-write state transitions, read-write offset invalidation after inserts/deletes, and overlay non-atomic mutation.

Dependencies/integration: includes `libfdt_env.h` and `fdt.h`, exposes C ABI with `extern "C"`, and hides selected APIs from SWIG bindings. It is the single include used by DTC utilities and external consumers.

Risks: inline helpers are ABI/API surface; changing signatures or macro semantics affects all consumers. Documentation repeatedly warns that mutators can invalidate offsets and that overlay apply can damage inputs on failure.

Test signals: public-header compile coverage in C/C++, SWIG exclusions, typed helper endian output, macro iteration correctness, error-code/string synchronization, and behavior promised in comments for each API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_env.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_env.h

Purpose: environment abstraction for libfdt integer types, standard includes, optional sparse annotations, and endian conversion primitives.

Important APIs/types/macros: includes `stdbool.h`, `stddef.h`, `stdint.h`, `stdlib.h`, `string.h`, and `limits.h`. Defines `FDT_FORCE` and `FDT_BITWISE` for sparse `__CHECKER__` builds. Typedefs `fdt16_t`, `fdt32_t`, and `fdt64_t` as bitwise-qualified fixed-width integer types. Provides inline `fdt16_to_cpu`, `cpu_to_fdt16`, `fdt32_to_cpu`, `cpu_to_fdt32`, `fdt64_to_cpu`, and `cpu_to_fdt64` using byte extraction.

Control flow/state: no persistent state. Conversion macros operate by reading bytes of the native integer representation, producing big-endian FDT values and vice versa.

Dependencies/integration: included by `libfdt.h` before `fdt.h` and directly by libfdt C files. It is the portability layer for endian and type behavior.

Risks: byte extraction assumes object representation access through `uint8_t *`, which is standard-friendly for byte inspection. Sparse annotations are no-ops outside checker builds, so type misuse is only caught in specialized analysis.

Test signals: endian conversions on little- and big-endian hosts, sparse builds, fixed-width type availability, and inclusion ordering before raw FDT structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_internal.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_internal.h

Purpose: private libfdt helpers, alignment macros, unchecked pointer arithmetic, reserve-map accessors, internal endian loads, sequential-write magic, and compile-time validation-assumption controls.

Important APIs/macros: `FDT_ALIGN`, `FDT_TAGALIGN`, `FDT_RO_PROBE`, declarations for internal validators/string search/node end offset, raw `fdt_offset_ptr_` and writable variants, reserve-map pointer helpers, internal `fdt32_ld_`/`fdt64_ld_`, `FDT_SW_MAGIC`, `FDT_ASSUME_MASK`, assumption enum values, `can_assume_()`, and `can_assume(NAME)`.

Control flow/state: assumption bits are compile-time constants controlling whether validation and rollback branches are included or skipped. Helpers themselves are stateless but expose unchecked memory access intended only after probes or when assumptions allow it.

Dependencies/integration: included by every libfdt implementation file, tying modules to shared validation policy and internal memory layout.

Risks: `ASSUME_PERFECT` or related masks deliberately remove safety checks and can make malformed DTBs crash or corrupt memory. The unchecked pointer helpers must not leak as public API. Assumption combinations must be understood by embedders trying to minimize code size.

Test signals: builds with default assumptions and each optimized mask, malformed input behavior under safe defaults, code-size/performance configurations, and sanitizer/fuzzer coverage around unchecked helper call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/livetree.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/livetree.c

Purpose: core DTC in-memory device-tree construction, merging, lookup, sorting, phandle allocation, and generation/consumption of overlay metadata nodes.

Important APIs/functions: builders for labels, properties, nodes, reserve entries, and `dt_info`; merge/delete helpers; append helpers for unique strings/u32s; accessors by property, label, marker, path, phandle, and reference; `get_node_phandle()` allocates phandles and adds legacy/ePAPR properties according to global format; `sort_tree()` canonicalizes order. Overlay metadata functions generate `__symbols__`, `__fixups__`, `__local_fixups__`, reconstruct labels/fixup markers, and update local phandle markers.

Control flow/state: tree nodes/properties are linked lists with soft-delete flags and label delete flags. Merging overlays new content onto old nodes, replacing property values on name collision and recursively merging child collisions. Phandle allocation uses a static local counter and consults existing tree phandles.

Dependencies/integration: depends on `dtc.h` data/marker/tree types, global options (`phandle_format`, `generate_fixups`, `quiet`), and `srcpos`. It feeds serializers in `flattree.c` and receives parsed DTS/DTB/FS trees.

Risks: soft-deleted elements remain in lists and must be filtered by iteration macros. Static phandle counter is process-global. Fixup string parsing temporarily mutates property data. Existing malformed metadata produces warnings and partial recovery.

Test signals: duplicate label resurrection, property/node delete overlays, merge collision behavior, path/label/phandle references, sorting determinism, phandle formats, symbol/fixup/local-fixup generation, and malformed metadata warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/livetree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/of_unittest_expect -->
# sources/distributed-fs/ceph-client/scripts/dtc/of_unittest_expect

Purpose: Perl log post-processor for Linux devicetree unittest console output. It highlights expected messages, suppresses optional expected output, and reports missing/unexpected unittest expectation markers.

Important APIs/functions/state: `compare()` matches expected text against log lines with literal segments plus special tokens `<<int>>`, `<<hex>>`, and `<<all>>`. `usage()` prints CLI help. `Getopt::Long` parses display options. The main `LINE` loop strips optional timestamps, recognizes `EXPECT \`, `EXPECT /`, `EXPECT_NOT \`, and `EXPECT_NOT /` markers with the `### dt-test ###` prefix, tracks stacks/queues for begin/end matching, prefixes output lines, and prints statistics.

Control flow/state: expectation begin lines push patterns onto stacks. Matching normal lines move entries into found queues. End markers validate nesting and whether the expected or forbidden message occurred. Global counters track found/missing expectations, unittest failures, and internal errors.

Dependencies/integration: Perl script using `Getopt::Long` and `Text::Wrap` plus console output conventions from `drivers/of/unittest.c`. It is not linked with DTC/libfdt C code but belongs to the same devicetree tooling area.

Risks: there appear to be variable-name mistakes in some branches (`@begin` instead of `@exp_begin_stack`/`@expnot_begin_stack`), which can affect matching. Regex handling is intentionally simple and case-sensitive. Hex matching only accepts lowercase `a-f`.

Test signals: logs with nested EXPECT/EXPECT_NOT regions, missing begin/end markers, timestamp stripping, hidden expected lines, line-number mode, fail-line detection, stats toggling, and special-token comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/of_unittest_expect -->

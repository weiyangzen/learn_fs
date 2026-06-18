# Group Research: group_1577_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_isave_c_sources_os__0afc4b1b5fde

Scope confirmed in `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.c

Purpose: implements Ghostscript interpreter VM save/restore/forgetsave management. It treats `save` as a transactional boundary over ref-memory chunks, change chains, local/global VM spaces, names, streams, font caches, and allocator state.

Core mechanisms:
- `alloc_save_state` creates visible save IDs, optionally saves global VM for the outermost local save, captures current allocator chunks, creates inner chunks for unallocated regions, resets free lists, and marks the interpreter as in-save.
- `alloc_save_change_in` records old slot contents in an `alloc_change_t` chain when an old ref slot is modified during a save level, preserving enough location metadata for static refs, dynamic refs, and refs embedded in structs.
- `alloc_restore_step_in` finalizes objects that will be freed, restores auxiliary resources, replays saved ref contents, frees chunks allocated after the save, restores allocator state, and resets or recomputes `l_new` markings.
- `alloc_forget_save_in` commits a save by merging current chunks/free lists/change chains into the next outer save, or clears bookkeeping when committing the outermost save.
- `alloc_restore_all` unwinds all save levels, finalizes memory spaces, releases non-memory resources through a fake save, and frees local/global/system memory.

Important details:
- `l_new` is a slot-level marker used to decide whether a slot modification needs undo logging. `save_set_new` scans change chains and newly allocated ref objects to set or clear this bit.
- To avoid repeated expensive scans at deep save levels, the code creates invisible internal saves after scanning more than `max_repeated_scan`.
- `alloc_is_since_save` and name variants detect whether a pointer/name would become dangling after restore by checking chunks allocated since the target save.
- GC support for `alloc_change_t` relocates both the saved content and the referenced slot address, including the embedded-struct offset case.

Dependencies: `gs_ref_memory_t`, chunk allocator internals, ref packing, name table restoration, stream lists, font cache restore hooks, VM-space checks, and Ghostscript GC structure descriptors.

Research notes:
- This is interpreter memory-transaction code, not filesystem logic, but it is central to safe PostScript execution in the vendored Plan 9 Ghostscript tree.
- Comments explicitly describe save as "start transaction", restore as abort, and forgetsave as commit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.h

Purpose: declares the interpreter save/restore API used by PostScript VM operators and memory-management code.

Key contract:
- Save objects are represented externally by numeric save IDs rather than direct `alloc_save_t` refs, because PostScript save objects are simple objects and because direct composite save references would complicate invalidation after restore.
- `alloc_save_state` returns a nonzero save ID and stores caller client data.
- `alloc_find_save`, `alloc_save_current_id`, and `alloc_save_current` map IDs back to active save records.
- `alloc_restore_step_in` restores one externally visible save step, while `alloc_forget_save_in` commits a save without pointer recency checks.
- `alloc_is_since_save` and name helpers support restore safety checks.

The internal section documents the `new_mask`/`test_mask` optimization: while in a save, new allocations get `l_new`, and old-slot stores are undo-logged only when `l_new` is absent.

Dependencies: requires interpreter memory definitions and `idosave.h`; exposes `font_restore` as the cache cleanup hook used by `isave.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isave.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.c

Purpose: implements the main Ghostscript PostScript/PDF token scanner. It reads tokens from streams or strings, builds refs, supports resumable scanning across stream refills/callouts, and handles Level 2 syntax extensions.

Main behavior:
- Dynamic string/name accumulation starts in an inline buffer and grows into VM strings as needed.
- `scan_token` skips whitespace, scans delimiters, names, literal names, immediate `//name` lookups, procedures delimited by `{}` with operand-stack accumulation, strings, hex strings, ASCII85 strings, comments, DSC comments, numbers, and binary tokens.
- `scan_string_token_options` scans from a string and advances the source string past the token.
- `scan_handle_refill` handles `scan_Refill` by processing stream buffers or pushing scanner continuation state to the execution stack for interrupts/callouts.
- Comment hooks can call external DSC/general comment processors or return comment tokens when scanner options request it.

State and continuation:
- `scanner_state` stores procedure stack depth, options, scan type, dynamic buffer, and scanner-specific substate.
- Suspended scans preserve partial comment/name/string/binary state and resume through labeled continuation paths.
- GC descriptors enumerate dynamic scanner strings and binary object-sequence arrays.

Important compatibility paths:
- Level 2 enables `<<`, `>>`, binary objects, ASCII85 strings, and broader string escape handling.
- PDF options alter name and invalid-number handling.
- The scanner can run in `SCAN_CHECK_ONLY` mode for syntax checking without producing full values.

Dependencies: stream/filter code, operand/dictionary stacks, name table, packed arrays, number scanner, binary token scanner, string decoders, VM-space store checks, and interpreter continuation machinery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.h

Purpose: defines scanner state, dynamic accumulation buffers, binary scanning substate, scanner options, special return codes, and public scanner entry points.

Key structures:
- `dynamic_area` tracks base/next/limit pointers, dynamic-vs-buffer ownership, the local comment-sized buffer, and allocator.
- `scan_binary_state` stores number format, continuation function, object array, current index, string/object bounds, top-level size, and sequence byte size.
- `scanner_state` stores procedure-building stack depths, options, current scan mode, dynamic area, and unioned substate for binary, names, and string filters.

Options include string-source scanning, syntax-check-only mode, comment/DSC processing, PDF scan rules, and Adobe-compatible invalid-number behavior. Return codes distinguish ordinary tokens from binary object sequences, EOF, refills, comments, and DSC comments.

The header exposes `st_scanner_state` so saved scanner states can be allocated and traced by the Ghostscript GC.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.c

Purpose: implements Ghostscript Level 2 binary token scanning and binary object sequence writing support.

Scanner responsibilities:
- Recognizes binary token byte values 128-159 for numbers, booleans, short strings, system/user names, numeric arrays, and binary object sequences.
- Decodes fixed, integer, and floating formats with explicit endian/native/IEEE variants.
- Supports refill-safe continuation for binary strings, numeric arrays, and binary object sequences.
- Parses binary object sequences into preallocated ref arrays, then reads trailing string/name data and fixes up names, evaluated names, arrays, and Ghostscript's dictionary extension.

Binary object sequence handling:
- Preallocates worst-case object refs from the declared byte length.
- Allocates/reallocates one trailing string area once the smallest string offset is known.
- Supports strings, names from raw bytes or system/user name tables, executable/evaluated names, arrays, marks, nulls, numbers, booleans, and dictionary objects.
- Dictionary support is an extension: even sizes encode key/value pairs; size 1 encodes an indirect dictionary reference.

Writing support:
- `encode_binary_token` serializes refs into 8-byte binary sequence object records for nulls, marks, integers, reals, booleans, arrays, dictionaries, strings, and names.
- It tracks separate ref and character offsets and adapts real encoding to the configured binary object format.

Dependencies: `btoken.h`, binary-number decoding from `ibnum.h`, dictionary/name lookup, VM-space store checks, dynamic scanner state from `iscan.h`, and stream buffer APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.h

Purpose: declares the internal binary-token scanner entry point `scan_binary_token`.

The main scanner calls this only when binary tokens are enabled by the binary object format and Level 2 support. The header exists because builds may provide either the real Level 2 implementation or a dummy Level 1 implementation.

Return contract: 0 for a normal binary token, `scan_BOS` for a binary object sequence, `scan_Refill` when more input is required, or a negative Ghostscript error code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.c

Purpose: implements the performance-sensitive number scanner used by `iscan.c`.

Supported syntax and behavior:
- Decimal integers, reals with fractional and exponent parts, signed numbers, radix numbers using `radix#digits`, and overflow promotion from int to long to double accumulation.
- Returns 0 when the whole input range is consumed as a number, or 1 with `*psp` pointing after the numeric prefix when trailing non-number data exists.
- Produces integer refs when possible and real refs when decimal/exponent/overflow requires it.
- Checks integer/unsigned/radix overflow and real range against `MAX_FLOAT`.

Optimization details:
- Fast path accumulates up to four leading decimal digits without a loop.
- Powers of ten up to 1e6 are table-driven for real scaling.
- Power-of-two radix parsing uses shifts instead of multiplication.

Compatibility detail: `PDFScanInvNum` allows Adobe-compatible handling of bogus `-` characters after a decimal point by swallowing the rest of the fractional digits rather than treating them as a scanner error.

Research notes: The file comments acknowledge the "spaghetti" control flow as a deliberate scanner hot-path optimization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.h

Purpose: declares `scan_number`, the numeric-token parser used by the main scanner.

Contract: the function scans a byte range with a supplied sign into a `ref`, returns 0 for full consumption, returns 1 for a valid numeric prefix plus trailing data, and leaves `l_new` marking to the caller. The final boolean parameter enables PDF invalid-number compatibility behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscannum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isdata.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isdata.h

Purpose: defines shared data structures for expandable stacks of Ghostscript refs.

Key design:
- Stack blocks include guard elements at top and bottom for low-overhead overflow/underflow detection.
- GC safety requires unused block areas to contain legitimate refs, so allocation, block transitions, and GC cleanup explicitly null unused slots.
- `ref_stack_t` stores mutable stack pointers, current block ref, extension sizes, max-stack parameter, margin/body sizing, initialization parameters, and allocator.

The header defines `s_ptr` aliases, opaque `gs_ref_memory_t`, and the public GC descriptor macro for `ref_stack_t`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isstate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isstate.h

Purpose: defines `alloc_save_t`, the saved-state object used by `isave.c`.

Fields:
- Embedded `gs_ref_memory_t state` must be first, allowing saved allocator state to be treated as a memory-state snapshot.
- `vm_spaces spaces` records the saved local/global/system memory layout.
- `restore_names` controls whether name-table entries are rolled back.
- `is_current` remembers whether this memory space was the current allocator.
- `id` stores the externally visible save ID, with zero used for invisible internal saves.
- `client_data` carries caller-owned data through save/restore.

The file also defines the private GC descriptor macro that subclasses `st_ref_memory` and adds `client_data`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/isstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.c

Purpose: implements expandable interpreter stacks of refs, used for Ghostscript operand, execution, and dictionary stacks.

Main operations:
- `ref_stack_init` initializes a stack over an initial ref-array block, allocates parameter storage if needed, sets guards, initializes null body slots, and records allocator/max-stack state.
- `ref_stack_set_max_count`, `ref_stack_set_margin`, and `ref_stack_allow_expansion` adjust stack limits and expansion policy.
- `ref_stack_count`, `ref_stack_index`, and `ref_stack_counttomark` inspect stack contents across linked blocks.
- `ref_stack_store_check` and `ref_stack_store` copy stack ranges into arrays while enforcing VM-space store rules and save/undo semantics.
- `ref_stack_push`, `ref_stack_extend`, `ref_stack_push_block`, `ref_stack_pop`, and `ref_stack_pop_block` manage linked-block growth and shrinkage.
- Enumeration and cleanup routines support GC scanning, and release/free routines tear down all stack blocks.

Block behavior:
- Stack blocks are represented as `t_array` objects whose first refs store `next` and `used` metadata.
- Pushing a new block keeps roughly one third of the current top block, moves the rest into the lower block's `used` interval, and nulls unused areas.
- Popping can either merge two blocks and free the top block or move data upward if both blocks do not fit together.

GC support relocates current block refs and adjusts raw stack pointers by the packed-ref relocation delta.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.h

Purpose: declares the expandable ref-stack representation and procedural API.

Important types:
- `ref_stack_block` overlays the leading refs of each stack block with `next` and `used` array refs.
- `ref_stack_enum_t` supports top-to-bottom enumeration across stack blocks.

Important API groups:
- Initialization and configuration: init, expansion flag, error codes, max count, margin.
- Inspection: count, max count, index, count-to-mark.
- Store/copy: store checks and stack-to-array copy with optional save/undo handling.
- Mutation: pop, clear, pop-to-depth, pop-block, extend, push.
- GC/lifecycle: enumerate, cleanup, release, free.

The header documents the invariant that stack-related underflow/overflow recovery is handled by top-level interpreter error recovery, with special stack-specific wrappers elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istkparm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istkparm.h

Purpose: defines `ref_stack_params_t`, the mostly immutable initialization parameters for expandable ref stacks.

Fields capture bottom/top guard sizes, block size, usable data size, guard value, underflow/overflow error codes, and whether stack expansion is allowed. The file also declares the private simple GC descriptor macro used by `istack.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istkparm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istream.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istream.h

Purpose: declares interpreter-level stream support routines exported by `zfproc.c`.

APIs:
- `sread_proc` and `swrite_proc` initialize procedure-backed streams for filters.
- `s_handle_read_exception` and `s_handle_write_exception` integrate stream interrupts/callouts with interpreter execution-stack continuations.

This header is the bridge between the stream package and interpreter continuation handling used by scanners, file IO, filters, and painting code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istruct.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istruct.h

Purpose: extends generic Ghostscript structure/GC support with interpreter ref-aware pointer handling.

Key definitions:
- `ptr_ref_type` identifies GC pointer procedures for refs.
- `st_refs` is the structure descriptor for blocks of refs, exported for save/restore scanning.
- `gc_procs_with_refs_t` extends the common GC procedure table with relocation of ref pointers and blocks of packed/full refs.
- Macros such as `ENUM_RETURN_REF`, `RELOC_REF_PTR_VAR`, `RELOC_REFS`, and `RELOC_REF_VAR` make GC descriptors for interpreter objects with embedded refs concise.
- Ref-struct descriptor helpers support structs whose payload is actually refs, used for client data of some library objects.

This header is a small but critical adapter between the interpreter ref model and the generic movable-GC infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/istruct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/itoken.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/itoken.h

Purpose: declares exported token-handling procedures from `ztoken.c`.

APIs:
- `ztokenexec_continue` resumes token execution after a procedure stream refill or callout.
- `ztoken_handle_comment` handles scanner comment/DSC-comment returns, with optional scanner-state saving and file pushing for continuations.
- `ztoken_scanner_options` updates cached scanner options after `setuserparams`.

The header ties the low-level scanner return codes to interpreter operators and execution-stack continuation flow.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/itoken.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.c

Purpose: provides general Ghostscript interpreter utilities for refs, packed arrays, object printing, operands, strings, operators, store checks, and matrices.

Major areas:
- Ref copying and initialization: `refcpy_to_old`, `refcpy_to_new`, and `refset_null_new`, including VM-space and save/undo handling.
- Equality: `obj_eq` implements PostScript-style equality across numeric integer/real pairs, name/string pairs, arrays, dictionaries, files, operators, save IDs, devices, structs, and font IDs; `obj_ident_eq` tightens string comparison to identity.
- String/name data: `obj_string_data`, `string_to_ref`, and `ref_to_string`.
- Printing: `obj_cvp` and `obj_cvs` implement `cvs`, `=`, `==`, and `===`-style conversion, including escaped strings, real-number formatting with required decimal points, operator names, type markers, and partial output via `start_pos`.
- Operators and arrays: `op_find_index`, `op_index_ref`, `array_get`, and `packed_get` convert operator indexes and unpack ordinary/mixed/short arrays.
- Store checks: `refs_check_space` enforces generation ordering when copying refs into non-local containers.
- Operand decoding: numeric, float, integer, real, and array-of-floats helpers validate stack/array operands.
- Matrix helpers: `read_matrix` and `write_matrix_in` convert six-element PostScript matrix arrays to/from `gs_matrix`, with save-aware writes.

Dependencies: name table, dictionary APIs, packed ref encoding, operator tables, stream string escaping, VM-space macros, matrix definitions, and interpreter memory/save macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.h

Purpose: declares the interpreter utility functions implemented in `iutil.c`.

The interface covers:
- Ref copying/filling and object equality/identity.
- Name/string data extraction and printable conversion (`obj_cvp`, `obj_cvs`).
- Array and packed-array element extraction.
- VM-space interval checking.
- C string/ref string conversion.
- Numeric operand extraction and real/float creation.
- Matrix read/write helpers, including macros for new-array and save-aware writes.

The comments document precision caveats for float conversions and the special return behavior of printable conversion routines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.c

Purpose: implements Level 2 interpreter password utilities.

Functions:
- `param_read_password` reads a password from a parameter list as a string, or accepts an integer by converting it to decimal text after an initial typecheck.
- `param_write_password` writes password bytes to a parameter list.
- `param_check_password` compares a supplied `Password` parameter against a configured password.
- `dict_read_password` and `dict_write_password` read/write encoded password strings in dictionaries, using a first-byte length convention and optional change authorization.

Important validation: password size is capped by `MAX_PASSWORD`; dictionary password storage must be a string without read access and with a valid embedded length byte.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.h

Purpose: declares Level 2 password helper types and APIs.

Defines `MAX_PASSWORD` as 64, the `password` struct with size plus fixed byte buffer, and `NULL_PASSWORD`. Declares parameter-list password read/write/check routines and dictionary password read/write routines.

The header notes that `MAX_PASSWORD` must match initial password lengths in `gs_lev2.ps`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutilasm.asm -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutilasm.asm

Purpose: provides MS-DOS x86 assembly support routines for Ghostscript interpreter builds.

Contents:
- Optional 80386 replacements for Turbo C long multiply/divide/modulo routines using 32-bit operand prefixes.
- Non-386 long signed/unsigned divide and modulo routines replacing slow Turbo C library implementations.
- Optional `NOFPU` fixed-point multiply routines (`_fmul2fixed_`, `_dfmul2fixed_`) for faster coordinate transformations without an FPU.
- `_memflip8x8`, an 8-by-8 bit-matrix transpose helper used for bitmap manipulation.

The assembly is heavily conditional on build flags such as `FOR80386`, `DEBUG`, and `NOFPU`. It is platform-specific legacy performance support, not portable interpreter logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutilasm.asm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmem2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmem2.h

Purpose: declares VM control user-parameter setters exported by `zvmem2.c` for `zusparam.c`.

APIs:
- `set_vm_reclaim(i_ctx_t *, long)` updates VM reclaim policy.
- `set_vm_threshold(i_ctx_t *, long)` updates VM threshold behavior.

This is a small cross-module header for interpreter user-parameter plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmem2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmspace.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmspace.h

Purpose: defines interpreter VM-space attribute encoding and store-check rules for refs.

VM spaces:
- `avm_foreign`, `avm_system`, `avm_global`, and `avm_local` are encoded into ref type attributes using `r_space_bits`/`r_space_shift`.
- Helpers extract, index, and set a ref's VM space.

Store-check model:
- Object spaces are treated as generations: foreign < system < global < local.
- Storing a ref into a destination is legal only if the referenced object's generation is not younger than the destination's generation.
- Macros `store_check_space` and `store_check_dest` enforce this and return `e_invalidaccess` on violations.

The comments document PostScript's local-into-global restriction plus Ghostscript initialization exceptions for systemdict-like dictionaries and global operators, with GC-root implications.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jasper.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jasper.mak

Purpose: Ghostscript partial makefile for integrating the JasPer JPEG 2000 support library.

Build model:
- Supports either linking an external `jasper` library (`SHARE_JASPER=1`) or compiling selected JasPer source files into Ghostscript (`SHARE_JASPER=0`).
- Defines source/object/generated directories, object lists for base, JPC, and JP2 components, and header dependency lists.
- Generates `libjasper.dev` by copying the selected shared/compiled `.dev` module file.
- Compiled mode builds explicit object rules for selected JasPer 1.701.x source files.

Configuration details:
- `JAS_EXCF_` disables unrelated JasPer formats such as BMP, JPG, MIF, PGX, PNM, RAS, and PNG, leaving the JPEG 2000 paths Ghostscript needs.
- Clean targets remove generated `.dev` files and object files, with comments noting object/gen deletion should be more selective.

Research notes: This is build integration for an embedded third-party image codec, not runtime code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jasper.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jbig2.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jbig2.mak

Purpose: Ghostscript partial makefile for integrating the `jbig2dec` library.

Build model:
- Supports external linking to `jbig2dec` or compiling selected JBIG2 source files directly into Ghostscript.
- Defines object lists for core arithmetic/generic/refinement/Huffman/MMR/image modules and page/segment/symbol/text/metadata modules.
- Generates `libjbig2.dev` by selecting the shared or compiled module file.
- Provides explicit compile rules for library files plus optional command-line-tool support files such as `getopt`, `sha1`, and `jbig2dec`.

Version notes:
- Comments say the makefile is known to work with jbig2dec v0.7, with one object list known good for v0.2-v0.6.
- Clean targets have comments warning that object/generated file deletion is not selective enough.

Research notes: This file is build glue for an embedded third-party JBIG2 decoder used by Ghostscript image/PDF processing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jbig2.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig.h

Purpose: generated/combined configuration header for Independent JPEG Group code in the Ghostscript build.

Contents:
- Starts with deprecated `stdpn.h`-style `P0` through `P16` prototype macros for older Ghostscript/IJG compatibility.
- Includes Ghostscript `stdpre.h` platform abstraction: compiler feature detection, prototype/inline handling, standard integer aliases, bool definitions, pointer comparison macros, rounding/count/offset helpers, `private`/`public` conventions, `client_name_t`, and exit status definitions.
- Ends with the IJG `gsjconf.h` configuration body, including `arch.h`, prototype support, unsigned char/short support, optional standard headers under `__STDC__`, disabled BSD/sys/types/far-pointer/short-name workarounds, small-int `MAX_ALLOC_CHUNK`, and JPEG-internal right-shift behavior based on `ARCH_ARITH_RSHIFT`.

Research notes:
- The comments explain that `stdpre.h` is concatenated into this file because of the IJG library build directory layout.
- This file is compile-time portability and third-party JPEG configuration, not Ghostscript interpreter runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig.h -->
# Group Research: group_139_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_isave_c_sources_os_fe84974ce96c

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.c

Implements the Ghostscript interpreter save/restore manager. It treats `save` as a transaction boundary over the interpreter VM allocator: saving closes current chunks, creates inner chunks over unallocated regions, records free-list and allocator state, and assigns externally visible save IDs. Restoring unwinds changed ref slots, finalizes and frees newer allocations, restores allocator state, font/name resources, and can also restore global VM for the outermost local save.

The core change log is `alloc_change_t`, recording a slot address, old contents, and whether the slot lives in a static object, a ref object, or inside a struct. The file uses the `l_new` bit as a per-slot write-barrier marker, with `save_set_new` scanning changed slots and newly allocated ref blocks. It also supports invisible inner saves to reduce repeated scan costs after large allocations.

Major APIs include `alloc_save_state`, `alloc_save_change_in`, `alloc_find_save`, `alloc_is_since_save`, `alloc_restore_step_in`, `alloc_forget_save_in`, and `alloc_restore_all`. The logic is tightly coupled to GC relocation, local/global VM spaces, streams, names, and font cache restoration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.h

Declares the interpreter save/restore interface. It explains why save objects are represented by unique numeric save IDs rather than direct `t_struct` references: this avoids requiring all save objects to live in global VM and avoids special invalidation after restore.

Exports initialization, save lookup, save creation, current save lookup, pointer/name recency checks, restore stepping, save forgetting, and full VM release. It also exposes internal state toggles `alloc_set_in_save` and `alloc_set_not_in_save`, plus hooks used by restore logic such as `font_restore`, `restore_check_save`, and `dorestore`.

This header is the public contract for `isave.c` and expects interpreter memory types from `imemory.h` and `idosave.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.c

Implements the Ghostscript PostScript token scanner. It reads tokens from streams or strings, handling whitespace, comments, names, literal names, immediate lookup names, numbers, arrays/procedures, strings, hex strings, ASCII85 strings, Level 2 delimiters, binary tokens, EOF, and stream errors.

The scanner is resumable. It stores partial state in `scanner_state` when input refill, VM allocation failure, interrupts, or stream callouts occur. Dynamic token text is managed with `dynamic_area`, initially using an embedded buffer and growing to heap storage when needed. Procedure bodies are accumulated on the operand stack until matching `}` and can be packed arrays when `ref_array_packing` is enabled.

Important entry points are `scanner_state_init_options`, `scan_token`, `scan_string_token_options`, and `scan_handle_refill`. Comment handling is pluggable through `scan_dsc_proc` and `scan_comment_proc`, or returned as scanner status codes when options request it. Number parsing is delegated to `scan_number`; binary tokens are delegated to `scan_binary_token`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.h

Defines scanner state and scanner API. `scanner_state` captures resumable parsing state: procedure stack depth, scanner options, current scan type, dynamic token buffer, and a union of substates for binary tokens, names, and string decoding filters.

Defines scanner options such as `SCAN_FROM_STRING`, `SCAN_CHECK_ONLY`, comment processing modes, PDF name rules, and PDF invalid-number compatibility. Defines special return codes: `scan_BOS`, `scan_EOF`, `scan_Refill`, `scan_Comment`, and `scan_DSC_Comment`.

Also exports `scan_token`, `scan_string_token_options`, `scan_handle_refill`, and comment hook pointers. This header deliberately exposes the full scanner state so callers can allocate it on the stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.c

Implements binary token scanning and writing for Ghostscript Level 2 binary object support. It recognizes token byte values 128 through 159, including binary object sequences, fixed and encoded numbers, booleans, strings, system/user names, and numeric arrays. Numeric decoding uses format metadata from `ibnum.h` and handles endian and float representation variants.

Binary object sequences are parsed into a preallocated ref array, then resized after determining how much payload is object records versus string data. The parser supports null, integer, real, name, evaluated name, boolean, string, array, mark, and a Ghostscript dictionary extension. It can suspend and resume while reading strings or object sequence payloads.

The write side is `encode_binary_token`, which serializes refs into binary sequence records, including array/dictionary offsets and string/name character offsets. The file depends on name tables, dictionaries, object stack support, VM-space checks, and scanner continuation state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.h

Declares the internal binary-token scanner entry point `scan_binary_token`. The main scanner calls it only when binary tokens are enabled and recognized.

The header notes that it exists because Ghostscript can provide either a real Level 2 implementation or a dummy Level 1 implementation. Its return contract mirrors scanner conventions: `0` or `scan_BOS` on success, negative errors on failure, and `scan_Refill` for resumable input.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.c

Implements the scanner’s numeric parser. It is performance-tuned and uses a deliberately dense control flow because number scanning is hot in PostScript workloads. The parser starts with fast integer accumulation, promotes to `long` on overflow risk, and then to `double` for very large or fractional values.

It handles signs, decimal integers, reals, exponent notation, radix notation with `#`, power-of-two radix fast paths, overflow and limit checks, and PostScript syntax errors. It also has a PDF compatibility mode where Acrobat-style invalid fractional forms containing `-` after `.` can be tolerated by swallowing the invalid fractional suffix.

The single exported function, `scan_number`, returns `0` when the whole span is consumed, `1` when a valid numeric prefix was consumed and `*psp` points after it, or a negative Ghostscript error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.h

Declares `scan_number`, the Ghostscript interpreter number scanner. The interface accepts a byte span, a pre-parsed sign, destination `ref`, output pointer for the first unconsumed byte, and a PDF compatibility flag.

The header notes that `scan_number` does not mark the resulting ref as new; callers such as `iscan.c` apply that marking where appropriate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isdata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isdata.h

Defines the core data structure for expandable interpreter ref stacks. It documents the GC cleanliness requirements for stack blocks: unused areas must contain valid refs, often nulls, so the collector can scan blocks safely without following stale pointers.

Defines `s_ptr`, `const_s_ptr`, opaque `gs_ref_memory_t`, `ref_stack_t`, and `ref_stack_params_t`. `ref_stack_s` contains the dynamic top pointer, current block boundaries, current block ref, extension accounting, maximum stack ref, failing request size, stack margin, body size, immutable params, and allocator pointer.

Also declares the GC structure macro `public_st_ref_stack`, with two GC-visible pointers: `current` and `params`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isstate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isstate.h

Defines `struct alloc_save_s`, the saved allocator state object used by `isave.c`. Its first field is a complete `gs_ref_memory_t state`, allowing it to act as a saved allocator snapshot. Additional fields record VM spaces, whether names must be restored, whether the saved allocator was current, the save ID, and opaque client data.

Provides `private_st_alloc_save`, the GC descriptor macro for save objects, built as a suffix of `st_ref_memory` with `client_data` as an extra pointer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/isstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.c

Implements expandable stacks of Ghostscript refs, used by the operand, execution, and dictionary stacks. Each stack is a linked list of `t_array` blocks whose leading refs encode `ref_stack_block` metadata, followed by guard slots, used refs, unused refs, and optional top guards.

The file handles initialization, guard setup, max count and margin management, counting, indexing across blocks, count-to-mark, VM-space store checks, copying stack contents to arrays with save/write barriers, popping, pushing, extending, block split/merge, enumeration, GC cleanup, and release/free.

It is GC-aware: the stack object has custom mark/relocate procedures, and block unused areas are nulled to avoid stale GC roots. Store operations enforce local/global/system/foreign VM-space rules through `refs_check_space` and `ref_assign_old/new`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.h

Declares the expandable ref-stack interface and `ref_stack_block` layout. It describes how Ghostscript’s principal interpreter stacks are represented as linked array blocks and how guard regions are included in the containing arrays.

Exports initialization, expansion control, error-code setup, maximum count and margin setters, count/index/counttomark helpers, store checking and storing, pop/clear operations, block pop, extension, push, block enumeration, GC cleanup, release, and free.

Also defines convenience macros such as `ref_stack_count_inline`, `ref_stack_max_count`, `ref_stack_clear`, and `ref_stack_pop_to`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istkparm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istkparm.h

Defines `struct ref_stack_params_s`, the mostly immutable configuration attached to a ref stack. Fields cover bottom and top guard counts, total block size, usable data size, guard value, underflow and overflow error codes, and whether expansion is allowed.

Also provides `private_st_ref_stack_params`, a simple GC descriptor macro used by `istack.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istkparm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istream.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istream.h

Declares interpreter support procedures for streams exported by `zfproc.c`. It includes procedure stream initialization functions `sread_proc` and `swrite_proc`, plus read/write exception handlers used by the interpreter, scanner, file I/O, and painting code.

These handlers bridge stream interrupts or callbacks into the execution-stack continuation model through `op_proc_t` continuations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istruct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istruct.h

Extends Ghostscript structure/GC support for interpreter refs. It declares `ptr_ref_procs`, the `st_refs` structure descriptor, and `gc_procs_with_refs_t`, which adds ref-pointer relocation and ref-block relocation callbacks to common GC procedures.

Provides macros for enumerating and relocating refs inside GC-managed objects: `ENUM_RETURN_REF`, `RELOC_REF_PTR_VAR`, `RELOC_REFS`, and `RELOC_REF_VAR`. It also defines descriptor helpers for structures that are allocated as structs but contain refs, such as client data attached to library objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/istruct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/itoken.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/itoken.h

Declares exported token-related procedures implemented elsewhere, primarily in `ztoken.c`. It includes `ztokenexec_continue` for continuing after procedure-stream refill or callout, and `ztoken_handle_comment` for handling `scan_Comment` or `scan_DSC_Comment` returns from the scanner.

Also declares `ztoken_scanner_options`, which updates cached scanner options in the interpreter context after user parameter changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/itoken.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.c

Provides general interpreter utilities for refs, strings, operands, packed arrays, operators, and matrices. It defines `ref_type_properties`, ref copy helpers with save/write barriers, null filling, equality and identity comparison, name/string data extraction, printable object conversion for `cvs`, `=`, `==`, and related operations, and operator index lookup/ref reconstruction.

Array helpers include `array_get`, `packed_get`, and `refs_check_space`, supporting ordinary, mixed, and short packed arrays. String helpers convert between C strings and Ghostscript string refs. Operand helpers extract numeric parameters, single real/float/int parameters, create real refs, and compute appropriate type/procedure check errors.

Matrix helpers read and write six-element matrices, including save-aware writes into existing arrays. The file intentionally avoids taking an interpreter context pointer and instead receives memory arguments directly where needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.h

Declares the interpreter utility API implemented by `iutil.c`. It covers ref copying, null initialization, object equality and identity, name/string data extraction, printable conversion, array and packed-array access, VM-space checks, string conversion, numeric operand extraction, real/float/int parameter helpers, real construction, and matrix read/write helpers.

It also defines `CVP_MAX_STRING`, the truncation threshold for full string printing, and compatibility macros such as `refset_null`, `write_matrix_new`, and `write_matrix`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.c

Implements Level 2 password utility routines. Parameter-list helpers can read passwords as strings or integer values, write passwords back as strings, and compare a supplied `"Password"` parameter against a stored password.

Dictionary helpers locate password strings in dictionaries, read the length-prefixed stored password form, and write a new password when allowed. Access and range checks protect against malformed password storage, oversized values, and unauthorized password changes.

The file depends on parameter-list APIs, dictionary lookup, byte comparison, and interpreter error conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.h

Declares Level 2 password utilities and defines the fixed-size `password` structure. `MAX_PASSWORD` is 64 and must match initial password lengths in Ghostscript Level 2 PostScript resources.

Exports parameter-list read/write/check helpers and dictionary read/write helpers. Also defines `NULL_PASSWORD` for an empty password initializer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutilasm.asm -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutilasm.asm

Contains legacy MS-DOS assembly support for the Ghostscript interpreter. Under `FOR80386`, it replaces Turbo C long multiply/divide/modulo library routines with 80386-prefixed 32-bit operations. Without `FOR80386`, it implements optimized 32-bit signed and unsigned division/modulo routines using 16-bit instructions, including Knuth-style normalization for 32-by-32 division.

Under `NOFPU`, it implements fixed-point multiply helpers `_fmul2fixed_` and `_dfmul2fixed_`, intended to avoid slow emulated floating point on systems without an FPU. The file also implements `_memflip8x8`, an 8-by-8 bit matrix transpose used by bitmap code.

This file is platform-specific compatibility/performance code and is unrelated to Plan 9 runtime behavior except as vendored Ghostscript source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iutilasm.asm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmem2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmem2.h

Declares VM control user-parameter procedures exported by `zvmem2.c` for use by `zusparam.c`. The two entry points are `set_vm_reclaim` and `set_vm_threshold`, both taking an interpreter context and a `long` value.

This header is a narrow bridge between user parameter handling and VM policy control.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmem2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmspace.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmspace.h

Defines interpreter VM-space tags and store-check rules. VM space is encoded in ref attribute bits as `avm_foreign`, `avm_system`, `avm_global`, or `avm_local`, with helper macros to get, index, and set ref space.

The file documents Ghostscript’s extension of PostScript local/global VM rules into four generations. Stores are legal only when the referenced object is not from a younger space than the destination. Macros include `r_is_local`, `r_is_foreign`, `store_check_space`, `store_check_dest`, and compatibility `check_store_space`.

It also documents special systemdict-related exceptions handled elsewhere for initialization and global operators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ivmspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jasper.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jasper.mak

Makefile fragment for integrating the Jasper JPEG 2000 library with Ghostscript. It supports either linking to a shared/external Jasper library or compiling selected Jasper 1.701.x source files into Ghostscript.

Defines source, object, and generated directories; object groups for base, JPC, and JP2 components; header dependencies; clean targets; Jasper-specific compile flags; excluded format support macros; generated `.dev` module rules; and explicit compile rules for each selected Jasper source.

The fragment intentionally disables unrelated Jasper image formats and builds only the pieces Ghostscript needs for JPEG 2000 support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jasper.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jbig2.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jbig2.mak

Makefile fragment for integrating the `jbig2dec` library with Ghostscript. It supports either linking to a shared `jbig2dec` library or compiling selected library sources into Ghostscript. Comments note compatibility with jbig2dec v0.7 and older object lists for v0.2 through v0.6.

Defines source/object/generated directories, object groups, headers, optional extra objects, clean targets, compiler command variables, generated `.dev` module rules, and explicit compile rules for JBIG2 arithmetic, Huffman, generic, refinement, image, MMR, page, segment, symbol dictionary, text, metadata, and related support files.

The clean rule contains an explicit warning that object/generated deletion should be more selective.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jbig2.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig.h

Concatenated Ghostscript configuration header for IJG JPEG compilation, combining `stdpn.h`, `stdpre.h`, and `gsjconf.h` style content. It defines deprecated `P0` through `P16` prototype macros, compiler/platform compatibility flags, inline handling, discard macros, alignment workarounds, type aliases, Boolean definitions, pointer comparison macros, min/max, rounding macros, `floatp`, `BEGIN`/`END`, client-name strings, `public`/`private`, and exit status macros.

The IJG section includes `arch.h`, maps Ghostscript prototype support to IJG `HAVE_PROTOTYPES`, declares unsigned char/short support, optional standard headers, far-pointer and short-name settings, allocation chunk limits for small `int` platforms, and JPEG internal right-shift behavior.

This header is portability glue for building IJG code inside Ghostscript’s cross-platform build system.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig.h -->
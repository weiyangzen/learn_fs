# Group Research: group_138_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_inamedef_h_sources_3be017e09924

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inamedef.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inamedef.h

Ghostscript internal name-table definition header. It ties together `inameidx.h`, `inamestr.h`, `inames.h`, and GC structure definitions to expose the concrete `name` and `name_table` layouts needed by inline interpreter code.

Key contents:
- Defines name table capacity behavior around `EXTEND_NAMES`, with `max_name_index` and `max_name_count`.
- Defines `struct name_s`, including the cached `pvalue` optimization for names defined only in common dictionaries.
- Defines `pv_no_defn`, `pv_other`, and `pv_valid` markers for cached name-definition state.
- Defines the two-level name table layout: `name_sub_table` blocks and `name_table_s` with allocation/free-list metadata, permanent string count, VM attributes, hash table, memory pointer, and paired name/string subtables.
- Provides inline macros for converting name refs, indices, strings, and table entries: `names_index_string_inline`, `names_string_inline`, `names_index_inline`, `names_index_ptr_inline`, and `names_index_ref_inline`.
- Defines `make_name`, forcing name refs into system VM space so the GC treats name objects as traceable.

Notable dependencies:
- `inameidx.h` for name index/subtable sizing.
- `inamestr.h` for string subtable data.
- `inames.h` for public name-table declarations.
- `gsstruct.h` for `gc_state_t`.

Research notes:
- This is performance-sensitive interpreter infrastructure, not filesystem code.
- The header intentionally exposes implementation internals so interpreter code can inline name/index lookup.
- Extended-name support changes how a ref’s `r_size` field maps back to the full name index, using `high_index` in the subtable when `EXTEND_NAMES` is enabled.
- GC and save/restore integration is explicit through `names_unmark_all`, `names_trace_finish`, and `names_restore`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inamedef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inameidx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inameidx.h

Ghostscript name-index configuration header. It defines how name counts map to physical name-table indices and how the name table is partitioned into subtables.

Key contents:
- Includes `gconfigv.h` for `EXTEND_NAMES` and defaults it to `0`.
- Defines `NT_LOG2_SUB_SIZE`, `NT_SUB_SIZE`, and `NT_SUB_INDEX_MASK`, scaling subtable size with extended-name mode.
- Reserves entry 0, entry 1 for the zero-length name, and entries 2 through 129 for 128 one-character names.
- Defines `NT_1CHAR_NAMES_DATA`, the static one-character name initialization data.
- Defines `name_count_to_index`, which scrambles allocation count order within a subtable using factor `23`.
- Defines the unused inverse mapping `name_index_to_count` with factor `1959`.

Notable dependencies:
- `gconfigv.h`.

Research notes:
- The count-to-index permutation is designed to avoid separate hash scrambling during dictionary lookup.
- The permutation preserves the subtable portion of the index and only permutes the low subtable index bits.
- The inverse factor comment says it works for `NT_SUB_SIZE` values up to 4096, but the inverse macro is not currently used.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inameidx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inames.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inames.h

Public name-table interface independent of a particular name-table instance. It declares the `names_` API used by the interpreter and memory/GC code.

Key contents:
- Forward-declares `name_table` and defines `name_index_t`.
- Exposes `name_max_string`.
- Declares name table allocation and memory access: `names_init`, `names_memory`.
- Declares name lookup/interning APIs: `names_ref`, `names_enter_string`, and `names_from_string`.
- Documents `names_ref` enter modes: no-enter, static string, copied string, and already dynamically allocated string.
- Defines `names_eq` as pointer equality between interned name objects.
- Declares value-cache invalidation, index/ref conversion, valid-index iteration, GC marking, and subtable object lookup routines.

Notable dependencies:
- Uses Ghostscript `ref`, `name`, `gs_memory_t`, `gs_ref_memory_t`, and `bool` types supplied by surrounding interpreter headers.

Research notes:
- The API separates public name operations from implementation details in `inamedef.h`.
- The name table is tightly integrated with GC relocation because callers can ask for the object/subtable containing a name or name string.
- Name refs are canonicalized, so equality can be tested by comparing `value.pname`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inamestr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inamestr.h

Internal name-string representation header for Ghostscript’s name table. It defines the Pearson hash data and the per-name string metadata stored parallel to `name` entries.

Key contents:
- Includes `inameidx.h`.
- Defines `NAME_HASH_PERMUTATION_DATA`, a 256-byte permutation used for Pearson-style string hashing.
- Defines `NAME_HASH`, a macro that computes a rolling hash for non-empty byte strings.
- Defines `name_string_t` with bitfields for `next_index`, `foreign_string`, GC `mark`, and `string_size`.
- Derives `name_extension_bits`, `name_string_size_bits`, and `max_name_string` from `EXTEND_NAMES`.
- Defines `name_next_index` and `set_name_next_index` macros.
- Defines `name_string_sub_table_t`, matching the name subtable size.
- Defines `NT_HASH_SIZE`, scaled by extended-name mode.

Notable dependencies:
- `inameidx.h`.

Research notes:
- `NAME_HASH` assumes `size >= 1`; zero-length name handling is special-cased elsewhere by the initialized name-table entries.
- The same `next_index` field is used for both hash chains and the free-name list.
- Extended-name mode trades maximum string length for a larger name index space by shifting bits from `string_size` into `next_index`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inamestr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inobtokn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inobtokn.c

Level 1 stub implementation for binary token scanning.

Key behavior:
- Defines `scan_binary_token`.
- Always returns `e_unregistered`.

Notable dependencies:
- `ghost.h`, `ierrors.h`, `stream.h`, `iscan.h`, and `iscanbin.h`.

Research notes:
- This is the fallback module used when binary-token support is not built.
- `int.mak` packages it into `nobtoken.dev`; full binary token support replaces it with `btoken.dev`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inobtokn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inouparm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inouparm.c

Level 1 stub implementation for user-parameter support.

Key behavior:
- Defines `set_user_params`.
- Ignores the supplied parameter dictionary and returns success.

Notable dependencies:
- `ghost.h`.
- `icontext.h` for the `set_user_params` prototype.

Research notes:
- This is the fallback module used when full Level 2 user/system parameter support is not built.
- `int.mak` packages it into `nousparm.dev`; `usparam.dev` replaces it with `zusparam`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/inouparm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/instcopy -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/instcopy

Portable shell wrapper for install-like file copying.

Key behavior:
- Accepts `instcopy -c [-m <mode>] <srcfile> (<dstdir>|<dstfile>)`.
- Parses `-c` and optional `-m`.
- Validates that exactly two positional arguments remain and that the source is a regular file.
- If destination is a directory, appends the source basename.
- Copies to a temporary file named `#inst.$$#` in the destination directory, optionally chmods it, removes the old destination, then renames the temporary file into place.
- Installs a trap to remove the temp file on exit.

Notable dependencies:
- POSIX-style `/bin/sh`, `cp`, `chmod`, `rm`, `mv`, `basename`, and `sed`.

Research notes:
- This is build/install tooling, not interpreter runtime code.
- Paths and variable expansions are unquoted, so filenames containing spaces or shell metacharacters are not handled safely.
- The temp filename is predictable and process-ID based, reflecting old portable-install-script conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/instcopy -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/int.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/int.mak

Platform-independent Ghostscript makefile for the PostScript and PDF interpreter layers. It defines source/include variables, module dependencies, object build rules, feature `.dev` modules, interpreter levels, PDF support, font support, filter support, plugin bridges, and main-program build targets.

Key contents:
- Defines interpreter source/object prefixes such as `PSSRC`, `PSLIB`, `PSGEN`, `PSOBJ`, `PSCC`, and `PSJBIG2CC`.
- Declares core interpreter support headers and nested include relationships, including the headers in this group: `inameidx.h`, `inamestr.h`, `inamedef.h`, `ipacked.h`, `iref.h`, `interp.h`, `iparam.h`, `iosdata.h`, `iostack.h`, `iparray.h`, `ipcolor.h`, and `iplugin.h`.
- Builds core support modules such as `ialloc`, `igc`, `igcref`, `igcstr`, `ilocate`, `iname`, and `isave` into `isupport.dev`.
- Builds interpreter support objects including `iparam`, `iplugin`, and the main `interp` object.
- Defines `psbase.dev` from interpreter runtime objects, non-graphics operators, graphics operators, scanner/token support, streams, basic IODevices, and default replacements `nobtoken` and `nousparm`.
- Defines feature modules for Level 1, Level 2, Level 3, Display PostScript, PDF, filters, fonts, CMaps, CIDFonts, CIE color, patterns, separation, transparency, ICC, `%disk` IODevices, and FAPI bridges.
- Provides explicit fallback and replacement modules:
  - `nobtoken.dev` from `inobtokn.c`, replaced by `btoken.dev`.
  - `nousparm.dev` from `inouparm.c`, replaced by `usparam.dev`.
- Defines build rules for auxiliary/generated artifacts such as compiled init code, compiled fonts, stochastic halftones, and generated configuration tables.
- Defines main program object rules for `gs.c`, `iapi.c`, `icontext.c`, `idisp.c`, `imainarg.c`, `imain.c`, `interp.c`, and `ireclaim.c`.

Notable dependencies:
- Graphics-library make variables and generated module tooling: `SETMOD`, `ADDMOD`, `GENCONF_XE`, `GENINIT_XE`, `GENHT_XE`.
- Core Ghostscript graphics library modules under `GLD`, `GLOBJ`, and `GLSRC`.
- Optional external libraries or bridges for zlib, JPEG, JBIG2, JPX/Jasper, UFST, and FreeType depending on enabled features.

Research notes:
- This file is the build graph for much of the language interpreter, not ordinary C source.
- It shows that several files in this group are low-level defaults or infrastructure rather than standalone features.
- The PDF build intentionally pulls in nearly all LanguageLevel 3 support rather than finely factoring only the needed operators.
- Some old compatibility comments remain, including alias targets `level1.dev`/`level2.dev`, DOS shell line-length constraints for font lists, and linker-order constraints around core libraries.
- There is a likely typo in the AES filter section: `faes4_=$(PSOBJ)zfaes.$(OBJ)` is defined, but `faes.dev` depends on and adds `$(faes_)`, which is not defined in the visible file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/int.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.c

Main Ghostscript language interpreter implementation. It owns interpreter initialization/reset, stack allocation, optimized operator dispatch, execution of refs and packed refs, scanner integration, error recovery, garbage collection signaling, time slicing, and internal oparray stack-protection operators.

Key behavior:
- Registers GC descriptors for dictionary, execution, and operand stacks.
- Defines default reschedule and optional time-slice hooks.
- Defines hard-coded fast operator pseudo-types for common operators: `add`, `def`, `dup`, `exch`, `if`, `ifelse`, `index`, `pop`, `roll`, and `sub`.
- Exposes `gs_interp_max_op_num_args`, `gs_interp_num_special_ops`, and `tx_next_index`.
- Defines `interp_op_defs`, including special operators plus internal `.currentstackprotect`, `.setstackprotect`, `%interp_exit`, and `%oparray_pop`.
- `gs_interp_init` allocates and loads an interpreter context.
- `gs_interp_alloc_stacks` allocates operand, execution, and dictionary stacks from stable memory with guard slots, error codes, and maximum counts.
- `gs_interp_free_stacks` releases stacks in inverse order.
- `gs_interp_reset` clears operand/execution stacks, installs `%interp_exit`, resets dictionary stack to the minimum depth, and refreshes dictionary cache state.
- `gs_interp_make_oper` assigns special extended types to hard-coded fast operators.
- `interp_reclaim` invokes the allocator GC hook while rooting the interpreter context pointer.
- `gs_interpret` roots the returned error object, delegates to `gs_call_interp`, and clears GC signal pointers before returning.
- `gs_call_interp` wraps the core loop with GC retry, stack overflow/underflow recovery, error-object handling, quit/fatal handling, and errordict dispatch.
- `set_gc_signal` installs or clears a GC signal pointer across all VM spaces and stable-memory allocators.
- `copy_stack` copies an overflowed stack into a local array for error reporting.
- `gs_errorname` maps error codes through `systemdict /ErrorNames`.
- `gs_errorinfo_put_string` stores a string in `$error /errorinfo`.
- The private `interp` loop dispatches literal refs, executable arrays, names, files, strings, packed integers, packed names, packed executable operators, and packed/full refs.
- Executable files and strings are scanned through `scan_token`; EOF, refill, comments, DSC comments, and binary object sequences are handled specially.
- Packed arrays use `ipacked.h` encoding and can execute packed special operators directly when `PACKED_SPECIAL_OPS` is enabled.
- `e_RemapColor`, `o_push_estack`, `o_pop_estack`, `o_reschedule`, interrupts, GC thresholds, and time slices all store enough execution state to resume.
- `oparray_pop`, `oparray_cleanup`, `.setstackprotect`, and `.currentstackprotect` manage stack restoration policy for pseudo-operator arrays.

Notable dependencies:
- Interpreter stack APIs: `estack.h`, `ostack.h`, `dstack.h`, `istack.h`.
- Memory and GC APIs: `ialloc.h`, `iastruct.h`, `ivmspace.h`, `gsstruct.h`.
- Name/dictionary APIs: `iname.h`, `inamedef.h`, `iddict.h`.
- Scanner/token APIs: `iscan.h`, `itoken.h`, `files.h`, `stream.h`, `sfilter.h`.
- Operator APIs: `oper.h`, `opdef` data, and operator implementations declared elsewhere.
- Packed ref definitions from `ipacked.h`.

Research notes:
- This is the central interpreter execution engine and one of the most performance-sensitive files in the subtree.
- The dispatch loop is heavily macro- and goto-based to preserve old compiler performance and handle packed refs without excessive branching.
- Several comments document compiler and architecture workarounds, especially around unaligned packed refs and aliasing assumptions.
- Execution stack expansion is explicitly marked not implemented; overflow is handled by error/reporting paths rather than normal extension.
- Some comments mark known questionable areas, such as handling `e_ExecStackUnderflow`, ignored negative `context_state_store/load` codes during GC, and disabled time-slice jumps for operators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.h

Internal interface header for `interp.c` and initialization code.

Key contents:
- Declares systemdict initialization helpers: `i_initial_enter_name`, `i_initial_remove_name`, and convenience macros using `i_ctx_p`.
- Exposes `gs_interp_max_op_num_args`.
- Exposes `gs_interp_num_special_ops`.
- Declares `gs_interp_make_oper`, which creates operators and assigns special fast-dispatch types when applicable.
- Declares `interp_reclaim`.
- Declares error support: `gs_errorname` and `gs_errorinfo_put_string`.
- Declares `gs_interp_init`, `gs_interp_alloc_stacks`, `gs_interp_free_stacks`, `gs_interp_reset`, and top-level `gs_interpret`.

Notable dependencies:
- Uses `i_ctx_t`, `ref`, `op_proc_t`, `gs_dual_memory_t`, `gs_ref_memory_t`, and `gs_context_state_t` from interpreter headers.

Research notes:
- This is a narrow internal ABI between interpreter initialization, context management, and the main execution loop.
- The special-operator count is shared with initialization so operator tables and packed execution agree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/interp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iosdata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iosdata.h

Operand-stack data header.

Key contents:
- Includes `isdata.h`.
- Defines `op_stack_t` as a wrapper around a generic `ref_stack_t`.
- Defines `public_st_op_stack`, a GC structure descriptor macro layered on `st_ref_stack`.
- Defines `st_op_stack_num_ptrs` as the same pointer count as `st_ref_stack`.

Notable dependencies:
- `isdata.h` and the ref-stack GC descriptor machinery.

Research notes:
- The operand stack currently has no extra fields beyond the generic ref stack.
- The wrapper type exists so the operand stack can have a distinct structure descriptor and API identity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iosdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iostack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iostack.h

Operand-stack pointer API header.

Key contents:
- Includes `iosdata.h` and `istack.h`.
- Defines `os_ptr` as `s_ptr`.
- Defines `const_os_ptr` as `const_s_ptr`.

Notable dependencies:
- `iosdata.h`.
- `istack.h`.

Research notes:
- This header gives operand-stack-specific names to generic ref-stack pointer types.
- It is intentionally minimal; actual stack behavior comes from the shared stack implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iostack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ipacked.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ipacked.h

Ghostscript packed-array encoding header. It documents and defines the compact 2-byte `ref_packed` representation used alongside full-size refs in packed arrays.

Key contents:
- Documents the bit layout for full refs, executable operators, packed integers, literal names, and executable names.
- Defines `packed_type` values: `pt_full_ref`, `pt_executable_operator`, `pt_integer`, unused tags, `pt_literal_name`, and `pt_executable_name`.
- Defines packed/ref alignment helpers: `packed_per_ref` and `align_packed_per_ref`.
- Defines tag and mask macros: `pt_tag`, `packed_value_mask`, `packed_max_value`.
- Defines packed detection helpers: `r_is_packed`, `r_packed_is_name`, and `r_packed_is_exec_name`.
- Defines packed name extraction and maximum index.
- Defines packed integer min/max values and mask.
- Defines packed mark-bit helpers for GC.
- Defines `packed_next` to advance through mixed packed/full refs.
- Defines `ref_array_packing` as the current setpacking/currentpacking state stored in `i_ctx_p`.

Notable dependencies:
- Requires `ref`, `ref_packed`, and architecture alignment macros supplied by surrounding interpreter headers.

Research notes:
- `interp.c`, `zpacked.c`, and GC compaction code know more about the packed representation than this header alone abstracts.
- The file emphasizes that mixed arrays must preserve full-ref alignment on architectures that fault on unaligned access.
- Packed names can only encode indices up to 12 bits; larger name indices require full refs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ipacked.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.c

Interpreter-side implementations of Ghostscript parameter-list APIs. It bridges PostScript refs, dictionaries, arrays, and stacks to the generic `gs_param_list` interface used by devices, operators, filters, and configuration code.

Key behavior:
- Converts parameter keys between `gs_param_name` strings and PostScript refs, supporting both name keys and integer keys.
- Converts name/int refs back into `gs_param_key_t` for enumeration.
- Defines generic write procedures for scalars, strings, names, arrays, dictionaries, integer-key dictionaries, and nested collections.
- Writes parameters to dictionaries, indexed arrays, or stacks depending on the concrete list type.
- Honors a wanted-key dictionary during parameter writing, skipping unrequested keys.
- Allocates arrays for typed array writes and fills refs using type-specific helpers.
- Copies non-persistent strings into interpreter memory and stores persistent strings as foreign read-only strings.
- Writes name values through `name_ref`.
- Defines generic read procedures for typed values, nested collections, arrays, policy lookup, error signaling, commit, and key enumeration.
- Reads int, float, string, and name arrays from PostScript arrays or packed arrays.
- Guesses array parameter type from the first element when reading generic typed values.
- Reads dictionaries and detects integer-key dictionaries by enumerating keys.
- Tracks per-parameter results in a `results` array: untouched, successful, or error code.
- Supports `require_all`, where commit marks unread parameters as `e_undefined`.
- Provides concrete readers for empty collections, indexed arrays, name/value arrays, stacks, and dictionaries.
- Provides concrete writers for stacks, dictionaries, and newly allocated indexed arrays.

Notable dependencies:
- Parameter API: `gsparam.h` through `iparam.h`.
- Interpreter data APIs: `oper.h`, `opcheck.h`, `ialloc.h`, `idict.h`, `imemory.h`, `iname.h`, `istack.h`, `iutil.h`, `ivmspace.h`, and `store.h`.

Research notes:
- This file is shared interpreter plumbing, not a device-specific implementation.
- The write path stores only requested keys when a wanted dictionary is present.
- The read path intentionally records individual parameter errors so callers can inspect detailed results and policy decisions.
- Integer-key support is used for array-like parameter collections and integer-key dictionaries.
- Some allocations for read arrays are marked persistent and rely on the parameter-list memory lifecycle or GC rather than immediate caller-owned freeing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.h

Header defining interpreter parameter-list structures and constructors for `iparam.c`.

Key contents:
- Includes `gsparam.h`.
- Documents three parameter-list implementations: dictionary objects, name/value pairs in arrays, and name/value pairs on a stack.
- Defines `iparam_loc`, pairing a value ref with the result slot for that parameter.
- Defines `iparam_list_common`, extending `gs_param_list_common` with interpreter ref memory, read/write function pointers, policy/wanted dictionaries, enumeration hook, results array, count, and integer-key mode.
- Defines `iparam_list`, `dict_param_list`, `array_param_list`, and `stack_param_list`.
- Declares constructors for reading and writing dictionaries, indexed arrays, raw arrays, and stacks.
- Defines `iparam_list_release`, freeing the results array.

Notable dependencies:
- Requires interpreter allocation/stack types from `ialloc.h` and `istack.h` in practice, as noted by the file comment.
- `gsparam.h` for generic parameter-list types.

Research notes:
- The read and write modes share the same base structure but use different union members.
- The `results` array is meaningful for read lists; write lists set it to zero.
- `int_keys` changes key conversion from names to decimal integer strings and integer refs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iparray.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iparray.h

Small interface header for packed-array construction.

Key contents:
- Explains that the header exists to avoid forcing `ipacked.h` and `istack.h` to include each other.
- Declares `make_packed_array`, implemented in `zpacked.c`, which creates a packed array from the top `N` stack elements.

Notable dependencies:
- Requires packed-array and stack types from `ipacked.h` and `istack.h` in the including context.

Research notes:
- This is a dependency-separation shim.
- Packed-array construction is tied to interpreter stack state and dual-memory allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iparray.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ipcolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ipcolor.h

Interpreter header for Pattern color client data.

Key contents:
- Defines `int_pattern`, storing the original pattern dictionary ref.
- Defines `private_st_int_pattern`, the GC descriptor macro for the pattern client-data struct.
- Declares `int_pattern_alloc`, which creates interpreter pattern data from a PostScript object.

Notable dependencies:
- Uses `ref` and Ghostscript memory/structure descriptor types from surrounding interpreter headers.

Research notes:
- The comment explains that this is a structure rather than a ref array for the same reasons used by graphics state and font data.
- This header is paired with pattern-color implementation code such as `zpcolor.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ipcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.c

Ghostscript interpreter plugin manager implementation.

Key behavior:
- Wraps raw, non-GC memory allocation in `i_plugin_client_memory`.
- `i_plugin_make_memory` installs allocation/free callbacks backed by a `gs_memory_t`.
- `i_plugin_init` iterates the generated `i_plugin_table`, instantiates each plugin, allocates an `i_plugin_holder`, and pushes it onto `i_ctx_p->plugin_list`.
- `i_plugin_finit` walks the plugin holder list, calls each plugin descriptor’s `finit`, and frees the holder.
- `i_plugin_get_list` returns the current context’s plugin list.
- `i_plugin_find` searches by descriptor `type` and `subtype`.

Notable dependencies:
- `malloc_.h`, `string_.h`, `ghost.h`, `gxalloc.h`, `ierrors.h`, `ialloc.h`, `iplugin.h`, and `icstate.h`.
- Generated or configured `i_plugin_table`.

Research notes:
- Plugin metadata lives in raw memory because it must survive PostScript VM restore operations and finalization of plugin-managed objects.
- If a plugin instantiation succeeds but later holder allocation fails, the function returns `e_Fatal` without visibly finalizing the just-created plugin instance.
- Plugin lookup is a simple linear search over the context list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.h

Public/internal plugin manager interface for Ghostscript interpreter plugins.

Key contents:
- Forward-declares `i_ctx_t` and `gs_memory_t` if not already defined.
- Declares plugin holder, instance, descriptor, and client-memory structures.
- Defines `i_plugin_descriptor` with `type`, `subtype`, and `finit` destructor.
- Defines `i_plugin_instance` as a base object containing a descriptor pointer.
- Defines `i_plugin_holder` as a linked-list node.
- Defines `i_plugin_client_memory`, a callback-based allocation interface.
- Defines `plugin_instantiation_proc` and `extern_i_plugin_table` macros.
- Declares memory wrapper, init/finalize, lookup, and list-access functions.

Notable dependencies:
- Paired with `iplugin.c`.
- Used by interpreter features such as FAPI bridges.

Research notes:
- The plugin interface is intentionally small: type/subtype RTTI, destructor, and custom allocation callbacks.
- The instantiation table is provided externally by generated configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ireclaim.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ireclaim.c

Interpreter interface to Ghostscript garbage collection.

Key behavior:
- Installs `ireclaim` as the interpreter allocator’s GC hook during initialization.
- `ireclaim` selects the VM space to collect based on allocator requests or explicit `vmreclaim` space, resets requested flags, runs `gs_vmreclaim`, resets allocation limits, and enforces `max_vm`.
- `gs_vmreclaim` recovers the interpreter context from the embedded `gs_dual_memory_t`, stores context state, closes allocation chunks, prepares file lists/allocation state for GC, registers the context root, invokes `GS_RECLAIM`, reloads relocated context state, updates `systemdict`, cleans up dictionary/name cached value pointers, and reopens chunks.
- Exports `ireclaim_l2_op_defs` with `op_def_end(ireclaim_init)`.

Notable dependencies:
- Memory/GC and context headers: `gsstruct.h`, `iastate.h`, `icontext.h`, `isave.h`, `isstate.h`.
- Stack headers: `dstack.h`, `estack.h`, `ostack.h`.
- `interp.h`, `opdef.h`, and `store.h`.

Research notes:
- The file assumes `gs_dual_memory_t` is embedded in `i_ctx_t` and recovers the context pointer with `offset_of`.
- Both normal VM spaces and stable-memory allocators are included in the memory list when needed.
- Comments mark unhandled failure cases after `context_state_store` and `context_state_load`.
- After collection, dictionary/name caches are explicitly refreshed with `dicts_gc_cleanup`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ireclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iref.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iref.h

Core Ghostscript interpreter object-reference definition header. It defines `ref`, object types, type/attribute bit layout, type-property tables, debug/type strings, pointer/value union fields, and common ref inspection/manipulation macros.

Key contents:
- Defines `ref` and opaque packed refs (`ref_packed`).
- Defines the `ref_type` enum: invalid, boolean, dictionary, file, array variants, struct/astruct, fontID, integer, mark, name, null, operator, real, save, string, device, oparray, and `t_next_index`.
- Documents which types are composite, executable-sensitive, access-protected, and size-bearing.
- Defines array and struct type spans used by fast type tests.
- Defines type-property flags and `REF_TYPE_PROPERTIES_DATA`.
- Defines debug/type/print string tables for diagnostics and PostScript type names.
- Defines location attributes (`l_mark`, `l_new`), VM-space bit placement, access bits (`a_write`, `a_read`, `a_execute`), `a_readonly`, `a_all`, executable bit, and type bit placement.
- Defines `REF_ATTR_PRINT_MASKS` for debug printing.
- Forward-declares interpreter object support types such as `dict`, `name`, `stream`, `gx_device`, and `obj_header_t`.
- Defines `op_proc_t`.
- Defines the concrete `ref_s` layout: a `tas_s` header containing `type_attrs` and `rsize`, plus a union for integer, bool, real, save id, byte pointers, ref pointers, names, dictionaries, packed refs, operator procs, files, devices, and structures.
- Provides fast macros for size access, type access, base type conversion, array/procedure/struct checks, type/attribute setting, interpreter dispatch key generation, attribute tests, attribute mutation, and struct pointer access.
- Defines `empty_ref_data`, `arch_sizeof_ref`, `arch_align_ref_mod`, `max_array_size`, and `max_string_size`.

Notable dependencies:
- Relies on architecture macros such as `arch_is_big_endian`, `arch_align_*`, and `arch_log2_sizeof_short`.
- Used by nearly every interpreter component through `ghost.h` and related headers.
- Closely related to `ipacked.h`, `store.h`, GC code, and the main interpreter dispatch in `interp.c`.

Research notes:
- The first field of `ref` must remain `type_attrs` because packed arrays and interpreter dispatch depend on the first two bytes being distinguishable from `ref_packed`.
- Types beyond `t_next_index` are reserved for interpreter pseudo-types used to speed high-frequency operators.
- Adding a new type requires coordinated updates in type string tables, initialization PostScript, debug printing, GC dispatch, interpreter dispatch, object conversion/equality code, and restore checks.
- The dispatch macro `r_type_xe` deliberately casts through a less-strictly-aligned type because the interpreter may point it at packed refs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iref.h -->
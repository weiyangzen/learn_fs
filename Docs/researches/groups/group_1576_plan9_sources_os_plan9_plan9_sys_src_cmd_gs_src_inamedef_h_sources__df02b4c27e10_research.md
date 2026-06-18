# Group Research: group_1576_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_inamedef_h_sources__df02b4c27e10

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamedef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamedef.h

Ghostscript internal name table definition. It ties together name indices, name strings, name references, GC hooks, and save/restore support.

Key behavior:
- Includes `inameidx.h`, `inamestr.h`, `inames.h`, and `gsstruct.h`.
- Caps `EXTEND_NAMES` at 6 extension bits, giving a maximum name-index space derived from `0x10000 << EXTEND_NAMES`.
- Defines `struct name_s`, including `pvalue`, a cached value pointer for global/operator names.
- Defines `name_sub_table` and `name_table_s`, a two-level table of name records and string records.
- Provides inline conversions between name indices, name refs, `name *`, and `name_string_t *`.
- Defines `make_name`, forcing name refs into system VM space so GC can trace them.
- Declares GC/save-restore hooks: `names_unmark_all`, `names_trace_finish`, and `names_restore`.

Notable dependencies:
- `inameidx.h` provides sub-table size and count/index scrambling.
- `inamestr.h` provides string metadata and hash sizing.
- `inames.h` provides public `name_table` API types.

Research notes:
- `pvalue` uses sentinel pointer values `0` and `1`, so code must only treat values above `1` as valid refs through `pv_valid`.
- The inline `names_index_inline` path changes under `EXTEND_NAMES`, deriving high bits from the owning sub-table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamedef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inameidx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inameidx.h

Name index constants and count/index permutation support for Ghostscript names.

Key behavior:
- Includes `gconfigv.h` for `EXTEND_NAMES`, defaulting it to `0`.
- Defines sub-table dimensions: `NT_LOG2_SUB_SIZE`, `NT_SUB_SIZE`, and `NT_SUB_INDEX_MASK`.
- Reserves initial entries for unused index 0, empty name, and 128 one-character names.
- Provides `NT_1CHAR_NAMES_DATA`, the initial one-byte-name data table.
- Defines `name_count_to_index` and `name_index_to_count` permutations so name allocation order is scrambled within sub-tables.

Research notes:
- The permutation factor is 23, with reverse factor 1959 for power-of-two sub-table sizes up to 4096.
- The comments explain the performance motivation: dictionary lookup benefits because it does not need to scramble separately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inameidx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inames.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inames.h

Public name table interface independent of implementation details or a singleton instance.

Key behavior:
- Defines/forwards `name_table` and `name_index_t`.
- Declares `name_max_string`.
- Declares initialization, allocator lookup, and name lookup/entry APIs.
- `names_ref` supports enter modes for no-enter, static string, copied string, or dynamically allocated string ownership.
- Declares conversion helpers: string ref, C-string entry, string-to-name conversion, index-to-ref/name, and next-valid-index traversal.
- Provides `names_eq` as pointer equality on `value.pname`.
- Declares GC support: mark by index and locate the sub-table objects for refs, indices, and strings.
- Declares `names_invalidate_value_cache`.

Research notes:
- This header is intentionally API-level; inline internals live in `inamedef.h`.
- Name equality is identity-based, relying on interning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamestr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamestr.h

Name string storage and hashing definitions for Ghostscript’s interned-name system.

Key behavior:
- Includes `inameidx.h`.
- Defines a 256-byte Pearson hash permutation via `NAME_HASH_PERMUTATION_DATA`.
- Provides `NAME_HASH`, which hashes a non-empty byte string with Pearson hashing.
- Defines `name_string_t`, holding chained hash/free-list next index, foreign/static ownership flag, GC mark bit, string size, and byte pointer.
- Adjusts bit-field widths according to `EXTEND_NAMES`.
- Defines `name_string_sub_table_t`, an array of `NT_SUB_SIZE` string records.
- Defines `NT_HASH_SIZE` as `1024 << (EXTEND_NAMES / 2)`.

Research notes:
- `name_string_t.next_index` is used for both hash chains and the free list.
- `max_name_string` shrinks when `EXTEND_NAMES` grows, matching the broader index-space tradeoff described in the other name headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamestr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inobtokn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inobtokn.c

Level 1 dummy implementation for binary-token scanning.

Key behavior:
- Includes interpreter/scanner headers: `ghost.h`, `ierrors.h`, `stream.h`, `iscan.h`, and `iscanbin.h`.
- Defines `scan_binary_token`.
- Always returns `e_unregistered`.

Research notes:
- This file backs the `nobtoken` module in `int.mak`; full binary-token support is supplied by `iscanbin.c` when the `btoken` feature replaces it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inobtokn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inouparm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inouparm.c

Level 1 dummy implementation for user-parameter setting.

Key behavior:
- Includes `ghost.h` and `icontext.h`.
- Defines `set_user_params`.
- Ignores the parameter dictionary and returns success.

Research notes:
- This is the `nousparm` fallback in `int.mak`; the Level 2 `usparam` feature replaces it with `zusparam.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/inouparm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/instcopy -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/instcopy

Portable shell helper implementing a limited `install`-style copy command.

Key behavior:
- Accepts `instcopy -c [-m mode] srcfile (dstdir|dstfile)`.
- Parses only `-c` and optional `-m`.
- Validates there are two operands and that the source is a regular file.
- If destination is a directory, appends the source basename.
- Copies to a temporary file named `#inst.$$#` in the destination directory, optionally applies mode, removes the old destination, and renames the temporary file into place.

Research notes:
- This is build/install plumbing, not interpreter logic.
- Variables are unquoted, so paths containing spaces or shell metacharacters are not handled safely.
- The temp name is predictable and process-id based, reflecting legacy portability assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/instcopy -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/int.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/int.mak

Platform-independent Ghostscript makefile for PostScript, PDF, Display PostScript, and related interpreter features.

Key behavior:
- Defines interpreter source/object directory macros and compiler command wrappers.
- Declares common interpreter headers, nested header dependencies, and object build rules.
- Builds core support modules such as allocator, GC, name table, save/restore, dictionaries, stacks, parameters, scanner, plugin manager, and interpreter.
- Defines `psbase.dev`, the base PostScript interpreter module, including core operators, IODevices, support modules, and stream filters.
- Defines feature `.dev` modules for Level 1, Level 2, Level 3, PDF, DSC parsing, color, patterns, CIE, separations, filters, binary tokens, user parameters, Display PostScript, CID/CMap, Type 1/2/32/42 fonts, compiled fonts, stochastic halftones, transparency, ICC, disk IODevices, and Font API bridges.
- Uses module composition commands such as `SETMOD` and `ADDMOD` to add objects, operators, PostScript resources, emulators, IODevices, plugins, replacement modules, function types, and links.
- Provides stub modules such as `nobtoken`, `nousparm`, `fapiu`, and `fapif` that can be replaced by richer features.
- Defines final main-program object dependencies for `gs.c`, `iapi.c`, `icontext.c`, `idisp.c`, `imainarg.c`, `imain.c`, `interp.c`, and `ireclaim.c`.

Notable dependencies:
- Ties interpreter C files in `PSSRCDIR` to graphics-library modules under `GLSRC`, `GLD`, and `GLOBJ`.
- References optional external libraries/bridges including JBIG2, JPX/Jasper, UFST, and FreeType.

Research notes:
- This file is the central interpreter feature graph; changing it can affect which operators, PostScript initialization files, and replacement stubs are present in a build.
- It explicitly separates small fallback implementations from feature replacements, for example `nobtoken` versus `btoken`, and `nousparm` versus `usparam`.
- There is a likely typo in the `zht2.$(OBJ)` dependency list: it references `$(iname)` rather than the established `$(iname_h)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/int.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.c

Ghostscript language interpreter implementation. It initializes interpreter stacks, defines special hard-coded operators, executes refs and packed refs, handles executable files/strings/procedures, coordinates errors, and invokes GC/time-slicing.

Key behavior:
- Defines GC descriptors for operand, execution, and dictionary stacks.
- Installs default reschedule/time-slice hooks, with rescheduling returning `invalidcontext` until context machinery replaces it.
- Defines fast special operator pseudo-types for `add`, `def`, `dup`, `exch`, `if`, `ifelse`, `index`, `pop`, `roll`, and `sub`.
- `gs_interp_init` allocates and loads context state.
- `gs_interp_alloc_stacks` allocates one stable ref array and partitions it into operand, execution, and dictionary stacks with guard zones and limits.
- `gs_interp_reset` clears operand/execution stacks, reinstalls `%interp_exit`, trims dict stack, and refreshes cached dictionary top.
- `gs_interp_make_oper` assigns hard-coded special operator types when possible.
- `interp_reclaim` calls the active dual-memory GC while registering the context pointer as a root.
- `gs_interpret` wraps `gs_call_interp`, roots the error object, and clears GC signal pointers afterward.
- `gs_call_interp` loops around the core interpreter, handling GC requests, `quit`, interpreter exit, VM reclaim, input-needed returns, stack growth/recovery, and errordict dispatch.
- `interp` is the main threaded dispatch loop. It:
  - keeps private operand and execution stack pointers for speed;
  - executes arrays, packed arrays, op arrays, names, operators, files, and strings;
  - uses cached name `pvalue` pointers and falls back to dictionary lookup by name index;
  - scans executable files and strings with `scan_token`;
  - handles binary object sequences, refill continuations, comments, and DSC comments;
  - directly decodes packed integers, names, and executable operators;
  - stores execution state back to the e-stack around calls, errors, and scheduling;
  - triggers time slicing or GC when `ticks_left` crosses thresholds.
- Error paths convert packed refs into full refs for `perror_object`, push interrupt objects back onto the execution stack, and log errors with source line information.
- Provides hidden stack-protection operators `.setstackprotect` and `.currentstackprotect` for `t_oparray` cleanup behavior.

Notable dependencies:
- Core interpreter state and stacks: `icontext.h`, `dstack.h`, `estack.h`, `ostack.h`.
- Object representation and packing: `iref.h`, `ipacked.h`.
- Name/dictionary machinery: `iname.h`, `inamedef.h`, `iddict.h`.
- Scanner/token handling: `iscan.h`, `itoken.h`, streams and filters.

Research notes:
- The loop is highly macro- and goto-driven for speed; packed-array and full-ref dispatch are intentionally interleaved.
- Several comments flag known limitations or fragile areas, including e-stack expansion being not implemented, an `ExecStackUnderflow` recovery comment marked wrong, and disabled time-slice jump experiments.
- The interpreter relies on exact type/attribute bit layout from `iref.h` and packed encoding from `ipacked.h`; changing either requires coordinated edits here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.h

Internal interface for interpreter initialization, systemdict entry helpers, stack allocation, GC, errors, and the top-level interpreter entry point.

Key behavior:
- Declares `i_initial_enter_name` and `i_initial_remove_name`, with macros using local `i_ctx_p`.
- Exposes `gs_interp_max_op_num_args` and `gs_interp_num_special_ops`.
- Declares `gs_interp_make_oper`.
- Declares `interp_reclaim`.
- Declares `gs_errorname` and `gs_errorinfo_put_string`.
- Declares `gs_interp_init`, `gs_interp_alloc_stacks`, `gs_interp_free_stacks`, `gs_interp_reset`, and `gs_interpret`.

Research notes:
- This header bridges `iinit.c`, `interp.c`, and code creating additional interpreter contexts.
- `gs_interpret` returns normal completion, input-needed statuses, quit/fatal codes, or PostScript error handling outcomes depending on `user_errors`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/interp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iosdata.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iosdata.h

Operand-stack data wrapper for Ghostscript.

Key behavior:
- Includes `isdata.h`.
- Defines `op_stack_t` as a wrapper containing a generic `ref_stack_t`.
- Defines `public_st_op_stack()` GC descriptor macro as a suffix of `st_ref_stack`.
- Defines `st_op_stack_num_ptrs`.

Research notes:
- The operand stack is currently just a generic ref stack; this wrapper gives it a distinct public structure descriptor and type identity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iosdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iostack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iostack.h

Operand-stack pointer type header.

Key behavior:
- Includes `iosdata.h` and `istack.h`.
- Defines `os_ptr` as `s_ptr`.
- Defines `const_os_ptr` as `const_s_ptr`.

Research notes:
- This is a thin specialization layer so operand-stack code can use semantic pointer names while sharing generic stack machinery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iostack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipacked.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipacked.h

Packed-array encoding definitions for Ghostscript refs.

Key behavior:
- Documents the 16-bit `ref_packed` format used in `t_mixedarray` and `t_shortarray`.
- Defines packed types for full refs, executable operators, integers, literal names, and executable names.
- Defines packed tag/value masks and helper predicates such as `r_is_packed`, `r_packed_is_name`, and `r_packed_is_exec_name`.
- Defines packed integer range as signed 12-bit values biased by `packed_min_intval`.
- Defines packed-name maximum index as the 12-bit value mask.
- Defines packed mark-bit helpers for GC.
- Defines `packed_next` to advance by either one packed slot or a full `ref` width.
- Defines `ref_array_packing` storage through `i_ctx_p->array_packing`.

Research notes:
- The comments state that `zpacked.c` and `interp.c` know representation details beyond this header.
- Alignment constraints drive mixed-array construction: preceding packed elements may be expanded so full refs remain correctly aligned.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipacked.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.c

Interpreter-backed implementations of Ghostscript parameter lists. It converts between generic `gs_param_list` reads/writes and PostScript refs stored in dictionaries, arrays, or stacks.

Key behavior:
- Converts parameter keys to refs with `ref_param_key`, supporting name keys or integer keys encoded as decimal strings.
- Converts ref keys back to `gs_param_key_t` with `ref_to_key`.
- Defines write-side list procs for typed values, nested collections, key enumeration, and wanted-key filtering.
- Writes scalar values as refs: null, bool, int/long, float, string, and name.
- Writes arrays by allocating ref arrays and filling integer, float, string, or name elements.
- Writes nested dictionaries and arrays through child `dict_param_list` instances.
- Provides stack-backed writing by pushing key/value pairs on a ref stack.
- Provides dictionary-backed writing via `dict_put`.
- Provides indexed-array writing using integer keys and direct array element assignment.
- Defines read-side list procs for typed values, nested collections, policy lookup, error signaling, and commit.
- Reads arrays as int, float, string, or name arrays, guessing by the first element for generic typed reads.
- Reads strings from either names or readable strings.
- Supports dictionary, array-pair, indexed-array, stack, and empty-collection readers.
- Tracks per-parameter results so commit can enforce `require_all` and mark unqueried parameters as `undefined`.

Notable dependencies:
- Interpreter object and stack APIs: `oper.h`, `opcheck.h`, `istack.h`, `store.h`.
- Dictionary/name APIs: `idict.h`, `iname.h`.
- Generic parameter API: `iparam.h`, `gsparam.h`.

Research notes:
- Read result slots use `0` for untouched, `1` for successful access, and negative error codes.
- Integer-key dictionaries are represented externally as decimal string keys but internally as integer refs.
- `ref_to_key` allocates integer-key strings with GC-managed memory and marks them persistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.h

Header for interpreter parameter-list implementations.

Key behavior:
- Includes `gsparam.h`.
- Documents three implementations: dictionary objects, name/value arrays, and name/value stack entries.
- Defines `iparam_loc`, pairing a value ref pointer with its result slot.
- Defines shared `iparam_list_common`, embedding `gs_param_list_common`, ref memory, read/write callbacks, policies/wanted dictionaries, enumerator callback, results array, count, and integer-key flag.
- Defines concrete list structs: `dict_param_list`, `array_param_list`, and `stack_param_list`.
- Declares read/write constructors for dictionary, indexed array, pair array, and stack parameter lists.
- Defines `iparam_list_release` to free the results array.

Research notes:
- The header relies on callers including allocator/stack prerequisites noted in comments.
- The same `dict_param_list` struct is reused for dictionaries and indexed arrays, with `dict` holding either kind of ref.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparray.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparray.h

Small bridge header for packed-array construction.

Key behavior:
- Exists because packed-array construction needs both `ipacked.h` and `istack.h`.
- Declares `make_packed_array`, implemented in `zpacked.c`.
- The function builds a packed array from the top N stack elements using dual VM memory and a client allocation name.

Research notes:
- This header intentionally avoids placing cross-dependencies in either `ipacked.h` or `istack.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparray.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipcolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipcolor.h

Interpreter-side Pattern color data header.

Key behavior:
- Defines `int_pattern`, holding the PostScript pattern dictionary ref.
- Defines `private_st_int_pattern()` GC descriptor macro for `zpcolor.c`.
- Declares `int_pattern_alloc`, which creates interpreter pattern client data from a pattern dictionary ref.

Research notes:
- The comment explains this is a structure rather than a ref array for the same GC/template reasons used by interpreter graphics state and font data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.c

Ghostscript interpreter plugin manager implementation.

Key behavior:
- Defines client-memory allocation/free wrappers backed by raw non-GC memory.
- `i_plugin_make_memory` initializes an `i_plugin_client_memory` wrapper around `gs_memory_t`.
- `i_plugin_init` walks `i_plugin_table`, instantiates each plugin, allocates a holder in raw memory, and links it into `i_ctx_p->plugin_list`.
- `i_plugin_finit` walks the plugin list, calls each instance descriptor’s finalizer, and frees holders.
- `i_plugin_get_list` returns the context’s plugin list.
- `i_plugin_find` searches by descriptor `type` and `subtype`.

Notable dependencies:
- Uses `icstate.h` for context plugin-list storage.
- Uses `iplugin.h` for plugin descriptors and table declarations.

Research notes:
- The file explicitly uses raw memory so plugin instances survive PostScript VM restore operations long enough to finalize objects they manage.
- If an instantiation succeeds but later holder allocation fails, the new instance is not finalized before returning fatal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.h

Public/private plugin manager interface for interpreter plugins.

Key behavior:
- Forwards `i_ctx_t` and `gs_memory_t`.
- Defines plugin descriptor, instance, linked-list holder, and client-memory callback structs.
- A descriptor contains `type`, `subtype`, and an instance finalizer/deallocator.
- An instance embeds a descriptor pointer as base-class RTTI.
- `plugin_instantiation_proc` macro defines plugin factory signatures.
- `extern_i_plugin_table()` declares the external plugin factory table.
- Declares plugin memory setup, initialization, finalization, lookup, and list access functions.

Research notes:
- This is a small object-model layer for optional interpreter plugins such as font APIs.
- The client memory interface requires copying/allocation behavior supplied by the plugin manager.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ireclaim.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ireclaim.c

Interpreter interface to Ghostscript garbage collection and VM reclaim.

Key behavior:
- Installs `ireclaim` as `gs_imemory.reclaim` during initialization.
- `ireclaim` is called either for allocation-pressure GC (`space < 0`) or explicit `vmreclaim`.
- Locates the requesting memory space, resets allocation requests, chooses local versus global collection, and calls `gs_vmreclaim`.
- After allocation-pressure GC, checks total allocated memory against `max_vm` and returns `VMerror` if still over limit.
- `gs_vmreclaim` reconstructs `i_ctx_t` from embedded `gs_dual_memory_t`, stores context state, collects active memory spaces and stable-memory companions, closes allocator chunks, prepares allocators for GC, registers the context pointer as a root, invokes `GS_RECLAIM`, reloads context state, refreshes `systemdict`, cleans dictionary/name caches, and reopens chunks.
- Defines `ireclaim_l2_op_defs` with an init hook.

Notable dependencies:
- Context save/load from `icontext.h`.
- Save-state traversal via `isave.h` and `isstate.h`.
- Stack globals from `dstack.h`, `estack.h`, and `ostack.h`.

Research notes:
- Comments contain two explicit “ABORT IF code < 0” placeholders after context store/load, indicating incomplete failure handling.
- The code assumes `gs_dual_memory_t` is embedded inside context state at a known offset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ireclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iref.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iref.h

Core Ghostscript object reference representation and type/attribute macro definitions.

Key behavior:
- Forwards `ref` and defines opaque `ref_packed`.
- Defines PostScript/interpreter object types including scalar types, dictionaries, files, arrays, packed arrays, structs, names, operators, strings, devices, and op arrays.
- Documents which types are composite, executable-sensitive, access-controlled, and size-bearing.
- Defines type property tables and type-name string tables for debugging, `type`, and printing.
- Defines location attributes (`l_mark`, `l_new`), VM-space bits, access bits, executable bit, and type-bit layout.
- Defines debug attribute print masks.
- Forwards abstract runtime types such as `dict`, `name`, `stream`, `gx_device`, and `obj_header_t`.
- Defines `op_proc_t`.
- Defines `struct ref_s`, with `tas.type_attrs`, `tas.rsize`, and a union for integer, bool, real, save id, byte/string pointers, ref arrays, packed arrays, operators, streams, devices, dictionaries, names, and structs.
- Provides macros for size access, type access, base type normalization, array/procedure/struct tests, structure type tests, type/attribute mutation, fast interpreter `type_xe` dispatch, attribute tests/mutation, and struct pointer access.
- Defines empty ref data, ref size/alignment requirements, maximum array size, and maximum string size.

Research notes:
- The first field layout is constrained by packed-array decoding in `ipacked.h` and `interp.c`.
- Extended pseudo-types starting at `t_next_index` encode high-frequency operators for dispatch speed; `r_btype` maps them back to `t_operator`.
- Comments list every subsystem that must be updated when adding new ref types.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iref.h -->
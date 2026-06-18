# Group Research: group_520_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_aa967ea75e26

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all requested files under `usr/src/uts/common/fs/zfs/lua/` were read completely. This group covers the Lua 5.2-derived runtime embedded in ZFS channel programs, including local illumos/ZFS compatibility changes.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.c

## Role

`lapi.c` implements the public Lua C API entry points used by embedders and Lua libraries. It is the main bridge between external C callers and the internal Lua VM objects, stack frames, tables, closures, coroutines, parser, dumper, allocator, and garbage collector.

## Main Responsibilities

- Converts API stack indexes, including positive stack indexes, negative relative indexes, registry indexes, and C-closure upvalue pseudo-indexes, into internal `TValue *` addresses.
- Implements stack manipulation: `lua_checkstack`, `lua_xmove`, `lua_absindex`, `lua_gettop`, `lua_settop`, `lua_remove`, `lua_insert`, `lua_replace`, `lua_copy`, and `lua_pushvalue`.
- Implements C-to-Lua and Lua-to-C value access: type tests, numeric/string/userdata/thread/pointer conversions, raw length, raw equality, arithmetic, and comparison.
- Implements push APIs for nil, numbers, integers, unsigned values, strings, formatted strings, C closures, booleans, light userdata, and current thread.
- Implements table/global/userdata/metatable accessors and mutators, including raw table operations and write-barrier calls after storing collectable objects.
- Implements calls, protected calls, continuations, loading, dumping, status queries, GC control, table iteration, concatenation, object length, userdata allocation, allocator replacement, and upvalue inspection/mutation/joining.

## Integration Points

The file depends on almost every Lua core subsystem: `ldo` for calls/protected execution, `lvm` for table/arithmetic/metamethod operations, `lstring` and `ltable` for objects, `lgc` for barriers and GC stepping, `lundump` for binary chunks, and `lfunc` for closures/upvalues.

## Risk Notes

API correctness depends on stack-index validation, frame-top adjustment, and GC barriers. The `moveto`, raw table setters, metatable setters, userdata environment setters, load upvalue initialization, and upvalue APIs are especially sensitive because stale barriers or invalid pseudo-index handling can corrupt the incremental collector or closure state.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.h

## Role

`lapi.h` provides small internal helpers used by the Lua API implementation.

## Main Responsibilities

- Defines `api_incr_top(L)`, which advances the Lua stack top and checks against the active call frame limit.
- Defines `adjustresults(L,nres)`, which expands the current call frame top for `LUA_MULTRET` results.
- Defines `api_checknelems(L,n)`, which validates that enough API stack elements exist for an operation.

## Integration Points

It includes `llimits.h` and `lstate.h`, and is consumed by API and call-path files such as `lapi.c` and `ldo.c`.

## Risk Notes

These macros are small but central to stack discipline. Bugs here affect nearly every public API operation.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.c

## Role

`lauxlib.c` implements the Lua auxiliary library, using only the official Lua API. It provides reusable helpers for library authors: tracebacks, argument validation, userdata metatables, buffer building, registry references, loading strings/buffers, module registration, and version checks.

## Main Responsibilities

- Builds compact stack tracebacks with function-name discovery, tail-call notation, and level elision.
- Reports argument errors with method/self adjustment and source-location prefixes.
- Creates, retrieves, validates, and assigns userdata metatables by registry name.
- Implements type and value checkers for strings, numbers, integers, unsigned integers, options, stack space, and arbitrary values.
- Implements `luaL_Buffer` growth and result emission using stack userdata for large temporary buffers.
- Implements the reference free-list system for tables via `luaL_ref` and `luaL_unref`.
- Loads Lua source from memory buffers and strings through `lua_load`.
- Implements metatable lookup/calls, `luaL_len`, `luaL_tolstring`, optional Lua 5.1 module compatibility helpers, `luaL_setfuncs`, `luaL_getsubtable`, `luaL_requiref`, `luaL_gsub`, and `luaL_checkversion_`.

## Integration Points

The file intentionally stays on the public API surface (`lua.h`, `lauxlib.h`) rather than using private core internals. It is therefore a reusable support layer for base, coroutine, bit, and other libraries.

## Risk Notes

Stack balance is the key invariant. Helpers such as `luaL_addvalue`, `luaL_setfuncs`, `luaL_requiref`, traceback generation, and registry references depend on precise stack placement and cleanup. Version checks also validate number-to-integer conversion assumptions for this build.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.h

## Role

`lauxlib.h` declares the Lua auxiliary-library API and convenience macros used to build Lua C libraries.

## Main Responsibilities

- Defines `luaL_Reg`, `LUA_ERRFILE`, and pre-defined reference constants.
- Declares argument checking, metatable, traceback, buffer, reference, load, length, string substitution, registration, and module helper functions.
- Provides macros for common type checks, optional arguments, loading strings/buffers, opening libraries, and generic buffer append operations.
- Defines `luaL_Buffer`, including the fixed initial buffer and stack-backed expansion protocol.

## Integration Points

This is the public support header for Lua libraries in this embedded runtime. Library files include it to register functions and validate Lua arguments.

## Risk Notes

The macros wrap stack-mutating operations. Callers must account for their stack effects, especially `luaL_newlib`, `luaL_getmetatable`, `luaL_opt`, and buffer macros.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbaselib.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbaselib.c

## Role

`lbaselib.c` implements the base Lua library exposed to ZFS channel programs, with several standard Lua functions deliberately removed.

## Main Responsibilities

- Provides base functions: `assert`, `collectgarbage`, `error`, `getmetatable`, `ipairs`, `next`, `pairs`, `rawequal`, `rawlen`, `rawget`, `rawset`, `select`, `setmetatable`, `tonumber`, `tostring`, and `type`.
- Registers `_G` and `_VERSION` in the global table via `luaopen_base`.
- Implements `tonumber` with optional base conversion from 2 through 36, including whitespace and sign handling.
- Implements protected metatable behavior through `__metatable`.
- Implements `pairs` and `ipairs`, honoring `__pairs` and `__ipairs` metamethods when present.
- Exposes GC controls through `collectgarbage`.

## Local/ZFS Adaptation

The file explicitly removes `dofile`, `loadfile`, `load`, `pcall`, `print`, and `xpcall` for ZFS channel programs. It also includes illumos/ZFS headers and local character handling.

## Risk Notes

The exposed base library is part of the sandbox surface. Reintroducing removed functions would materially change channel-program capabilities. The `collectgarbage` function gives scripts control over collector mode and pacing.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbaselib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbitlib.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbitlib.c

## Role

`lbitlib.c` implements Lua's `bit32` library for fixed-width bitwise operations.

## Main Responsibilities

- Defines a 32-bit default bit width via `LUA_NBITS`.
- Implements `band`, `btest`, `bor`, `bxor`, `bnot`, logical shifts, arithmetic right shift, rotations, field extraction, and field replacement.
- Trims all results to the configured bit width.
- Validates bit field positions and widths before extraction/replacement.
- Registers the module through `luaopen_bit32`.

## Integration Points

The file uses only public Lua and auxiliary APIs for argument conversion and function registration.

## Risk Notes

Shift and rotate operations avoid undefined full-width shifts by checking bounds and masking counts. Field argument validation prevents access beyond `LUA_NBITS`.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbitlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.c

## Role

`lcode.c` is the Lua bytecode generator. It converts parser expression state into VM instructions, manages registers and constants, patches jumps, folds constants, and emits opcodes for expressions, control flow, assignments, calls, and table constructors.

## Main Responsibilities

- Emits `Instruction` values into a function prototype and maintains matching line-number metadata.
- Manages register allocation, stack-size limits, and expression placement into registers or RK operands.
- Builds and patches jump lists for boolean expressions, control flow, close-upvalue jumps, and labels.
- Deduplicates constants in the function constant table, including special handling for `-0` and NaN numeric constants.
- Emits loads, stores, table indexing, method calls, returns, varargs, concatenation, arithmetic, comparisons, unary operators, and table constructor `SETLIST` batches.
- Optimizes adjacent `LOADNIL` operations and chained concatenations.

## Local/ZFS Adaptation

Constant folding includes a patch that refuses to fold `INT64_MIN / -1`, avoiding an overflow/undefined arithmetic edge case in this integer-oriented embedding.

## Risk Notes

The most sensitive invariants are jump offsets, register lifetimes, constant-table indexing, RK operand limits, and `pc`/lineinfo synchronization. A wrong patch or missing register free can produce invalid bytecode that fails later in the VM rather than at parse time.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.h

## Role

`lcode.h` declares the compiler code-generation API and expression operator enums.

## Main Responsibilities

- Defines `NO_JUMP`, binary operators, unary operators, and helpers for accessing generated instructions.
- Provides wrappers for emitting signed `sBx` jumps and multi-result expressions.
- Declares code emission, register reservation, constant creation, expression discharge, boolean jump handling, variable stores, prefix/infix/postfix operator generation, list construction, jump patching, and return generation functions.

## Integration Points

The parser consumes this header to emit VM bytecode into `Proto` objects. It ties together lexer/parser expression descriptors and `lopcodes.h` instruction formats.

## Risk Notes

The operator enum order is intentionally coupled to parser and opcode mapping. Reordering requires coordinated updates.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcompat.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcompat.c

## Role

`lcompat.c` provides illumos/ZFS compatibility helpers used by the embedded Lua runtime where standard libc behavior or numeric operations need local substitutes.

## Main Responsibilities

- Implements `lcompat_sprintf` as a bounded `vsnprintf` wrapper returning `ssize_t`.
- Implements `lcompat_strtoll` with whitespace skipping, optional sign, base-10/base-8/base-16 prefix handling, digit scanning, and end-pointer reporting.
- Implements integer exponentiation by squaring in `lcompat_pow`, returning zero for negative exponents.
- Implements `lcompat_hashnum`, a deterministic integer hash mixer for numeric table keys.

## Integration Points

`llimits.h` routes numeric hashing through `lcompat_hashnum` when building table code. `lobject.c` uses `lcompat_sprintf` for `%p` formatting in Lua error/string helpers.

## Risk Notes

These helpers intentionally implement a small subset of libc-like behavior. Overflow is not checked in `lcompat_strtoll` or `lcompat_pow`; callers rely on Lua's surrounding numeric semantics.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcompat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcorolib.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcorolib.c

## Role

`lcorolib.c` implements Lua's coroutine library.

## Main Responsibilities

- Creates coroutine threads with `coroutine.create`.
- Resumes coroutines with argument/result transfer across Lua states sharing the same global state.
- Implements `wrap`, which converts resume failures into raised Lua errors with location information.
- Implements `yield`, `status`, and `running`.
- Registers the coroutine library through `luaopen_coroutine`.

## Integration Points

The library is a public wrapper around core thread APIs: `lua_newthread`, `lua_resume`, `lua_yield`, `lua_xmove`, `lua_status`, and stack inspection.

## Risk Notes

The code carefully handles dead coroutine detection, too many arguments/results, and stack transfer failures. Coroutine behavior is constrained by `ldo.c` yieldability rules.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcorolib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.c

## Role

`lctype.c` provides Lua's internal character classification table when the build does not use the host C `ctype` library.

## Main Responsibilities

- Defines `luai_ctype_`, indexed with an extra leading entry so EOZ (`-1`) can be classified safely.
- Encodes alphabetic, digit, printable, space, and hexadecimal flags for ASCII input.
- Gives Lua fixed parser behavior independent of locale when `LUA_USE_CTYPE` is false.

## Integration Points

The lexer and object numeric parser use these classifications through `lctype.h` macros.

## Risk Notes

This table assumes ASCII when selected. Non-ASCII source text is not treated as identifier characters by this path.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.h

## Role

`lctype.h` defines Lua-specific character classification macros for the lexer and numeric parser.

## Main Responsibilities

- Selects the internal fixed ASCII table when the platform encoding matches ASCII; otherwise falls back to standard C `ctype`.
- Defines Lua-specific predicates for alphabetic/alphanumeric characters, where `_` counts as alphabetic.
- Provides digit, whitespace, printable, hexadecimal, and lowercase conversion helpers.
- Declares `luai_ctype_` when using the internal table.

## Integration Points

Used by `llex.c` and `lobject.c` for source scanning, escape processing, and numeric conversion.

## Risk Notes

These macros do not exactly match standard `ctype.h`; they are tuned for Lua syntax and should not be reused as general-purpose locale-aware classification.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.c

## Role

`ldebug.c` implements Lua's debug interface, hook configuration, stack/local/upvalue inspection, debug information retrieval, symbolic bytecode analysis for names, and runtime error construction.

## Main Responsibilities

- Supports debug hooks for calls, returns, lines, and counts through `lua_sethook` and related getters.
- Implements `lua_getstack`, `lua_getlocal`, `lua_setlocal`, and `lua_getinfo`.
- Handles yielded call frames by swapping `CallInfo.extra` and `func` when needed.
- Builds function metadata: source, line ranges, current line, parameters, vararg status, tail-call status, active line table, and function objects.
- Symbolically scans bytecode to infer local/global/field/upvalue/method/metamethod names for better error messages.
- Implements type, concatenation, arithmetic, ordering, and generic runtime error reporting with source-line prefixes.
- Invokes error handlers through `luaG_errormsg`.

## Integration Points

The VM, API, auxiliary library, and call layer use this file for diagnostics and error throwing. It depends on opcode metadata, function prototypes, stack frames, tables, strings, and metamethod names.

## Risk Notes

Most code is diagnostic, but it runs during errors and hooks, so stack handling must be conservative. Symbolic execution must tolerate conditional control flow and unknown register origins without producing invalid memory access.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.h

## Role

`ldebug.h` declares internal debug/error helpers and small macros for program-counter and line mapping.

## Main Responsibilities

- Defines `pcRel`, `getfuncline`, `resethookcount`, and `ci_func`.
- Declares non-returning runtime error helpers for type, concat, arithmetic, ordering, generic run errors, and final error dispatch.

## Integration Points

Included by VM, API, memory, object, and call-path files that need debug metadata or error throwing.

## Risk Notes

`ci_func` assumes an active Lua closure in the `CallInfo`. Callers must only use it in contexts where `isLua(ci)` holds.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.c

## Role

`ldo.c` implements Lua's stack, call, protected-call, coroutine resume/yield, hook-call, and protected parser machinery.

## Main Responsibilities

- Implements error handling with a linked stack of `lua_longjmp` records.
- Uses a kernel-specific branch with `label_t`, `setjmp`, and `longjmp` under `_KERNEL`.
- Throws errors to thread or main-thread handlers, invokes panic functions when available, and panics if no error handler exists.
- Reallocates, grows, shrinks, and corrects stacks while preserving open upvalue and `CallInfo` pointers.
- Runs debug hooks safely with stack/top restoration and hook reentrancy suppression.
- Prepares C, C-closure, Lua-closure, and `__call` metamethod calls; handles varargs and missing fixed parameters.
- Completes calls by moving results to requested slots and restoring caller frames.
- Enforces C-call depth and non-yieldable call boundaries.
- Implements coroutine resume, recovery from yielded protected calls, continuation calls, `lua_yieldk`, and unrolling back to C boundaries.
- Implements protected calls and protected parser execution for text/binary chunks, with cleanup of scanner/parser dynamic buffers.

## Integration Points

This file is the control-flow center for `lapi.c`, `lvm.c`, parser/loading code, coroutines, hooks, and error reporting. It calls into `lfunc`, `lgc`, `lundump`, `lparser`, `lzio`, and `lvm`.

## Risk Notes

The highest-risk areas are non-local jumps, stack relocation, yielded continuations, protected-call recovery, and parser cleanup. Kernel embedding makes the `_KERNEL` longjmp path and panic behavior particularly important.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.h

## Role

`ldo.h` declares the internal stack and call-control API.

## Main Responsibilities

- Defines stack growth helpers and pointer save/restore macros used across reallocations.
- Defines the protected function callback type `Pfunc`.
- Declares protected parsing, hooks, pre-call/post-call, direct calls, protected calls, stack reallocation/growth/shrink, non-local throws, and protected execution.

## Integration Points

This header is used by API, debug, lexer/parser, memory, object, and VM code that can grow stacks, run protected operations, or throw errors.

## Risk Notes

`savestack` and `restorestack` encode stack pointers as byte offsets. Misusing them with non-stack pointers would corrupt call recovery after stack reallocations.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldump.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldump.c

## Role

`ldump.c` serializes Lua function prototypes into precompiled binary chunks.

## Main Responsibilities

- Defines `DumpState` with Lua state, writer callback, callback data, strip flag, and status.
- Emits binary blocks, characters, integers, numbers, vectors, strings, bytecode, constants, nested prototypes, upvalue descriptors, and debug metadata.
- Omits source, line, local, and upvalue-name debug data when `strip` is set.
- Writes the Lua binary chunk header through `luaU_header`.
- Exposes `luaU_dump` for dumping a `Proto` through a `lua_Writer`.

## Integration Points

Used by `lua_dump` in `lapi.c`. The output format matches `lundump` expectations for loading binary chunks.

## Risk Notes

The writer callback runs with the Lua lock released and then reacquired. Dump format is tightly coupled to the exact `Proto`, `TValue`, opcode, and numeric representation of this build.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.c

## Role

`lfunc.c` manages Lua closures, prototypes, and upvalues.

## Main Responsibilities

- Allocates C closures, Lua closures, fresh upvalues, and function prototypes.
- Finds or creates open upvalues for stack slots, keeping open upvalues sorted by stack level.
- Resurrects dead open upvalues when reused.
- Closes open upvalues at or above a stack level by copying stack values into the upvalue object and moving it to the regular GC list.
- Frees upvalues and prototypes, including all prototype arrays.
- Looks up active local-variable names for debug information.

## Integration Points

The parser creates prototypes, the VM creates/finds upvalues for closures, `ldo.c` closes upvalues during error recovery, and `lgc.c` frees/traverses these objects.

## Risk Notes

Open upvalue list ordering and GC color transitions are critical. Closing an upvalue must preserve the captured value and update collector invariants.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.h

## Role

`lfunc.h` declares closure/prototype/upvalue helpers and closure sizing macros.

## Main Responsibilities

- Defines `sizeCclosure(n)` and `sizeLclosure(n)` for variable-sized closure allocation.
- Declares constructors for prototypes, C closures, Lua closures, and upvalues.
- Declares open-upvalue lookup, upvalue closing/freeing, prototype freeing, and local-name lookup.

## Integration Points

Used by API, call, GC, parser, and VM code whenever closures or prototypes are allocated, freed, or inspected.

## Risk Notes

The closure size macros must match the flexible-array layout in `lobject.h`.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.c

## Role

`lgc.c` implements Lua's garbage collector: incremental mark-and-sweep, generational mode, weak-table handling, finalization, write barriers, object allocation links, emergency/full collections, and collector pacing.

## Main Responsibilities

- Allocates new collectable objects and links them to the appropriate GC list.
- Implements forward, backward, and prototype-specific write barriers.
- Marks roots: main thread, registry, metatables, and pending-finalization objects.
- Traverses tables, closures, prototypes, threads, userdata, strings, and upvalues.
- Handles weak-value, weak-key, all-weak, and ephemeron tables, including convergence of ephemeron propagation.
- Sweeps strings, finalizable objects, regular objects, open upvalues, thread stacks, and call-info lists.
- Separates finalizable userdata/objects into `finobj` and `tobefnz` lists and invokes `__gc` metamethods under protected calls.
- Controls state transitions across pause, propagate, atomic, sweep-string, sweep-udata, and sweep phases.
- Supports generational and incremental modes, mode switching, forced steps, ordinary steps, emergency collections, full collections, and free-all shutdown.

## Integration Points

This file coordinates with every collectable runtime type declared in `lobject.h`, closure/prototype management in `lfunc.c`, tables/strings, state management, the call layer for finalizers, and memory accounting in `lmem.c`.

## Risk Notes

Collector invariants are the main risk: black objects must not point to white objects while the invariant is active, weak tables need delayed clearing, and finalizers can resurrect objects or allocate. Emergency GC deliberately avoids finalizers.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.h

## Role

`lgc.h` defines the garbage collector state machine, color bits, invariants, barrier macros, and GC API declarations.

## Main Responsibilities

- Defines collector states, sweep-phase tests, generational-mode tests, and invariant predicates.
- Defines object mark bits for white, black, finalized, separated, fixed, and old states.
- Provides bit manipulation helpers and liveness tests.
- Defines `luaC_checkGC`, conditional GC stepping, and value/object write-barrier macros.
- Declares object allocation, barriers, finalizer checks, upvalue color checks, mode changes, steps, full collection, and free-all operations.

## Integration Points

Included by allocation, API, table, string, closure, state, and VM code to preserve collector invariants when object graphs change.

## Risk Notes

Barrier macros depend on correct object/value type tagging. Missing a barrier in callers can create collector-visible corruption that may surface much later.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.c

## Role

`llex.c` implements Lua's lexical analyzer. It reads a `ZIO` input stream and produces parser tokens with semantic values for names, strings, and numbers.

## Main Responsibilities

- Initializes and fixes reserved-word strings.
- Converts tokens to printable strings for diagnostics.
- Maintains a growable scanner buffer with overflow checks.
- Reports lexical and syntax errors with chunk IDs and line numbers.
- Interns scanned strings and anchors them in the active function table during compilation.
- Tracks line numbers and handles all Lua newline combinations.
- Sets lexer input state, source name, environment-name string, decimal point, lookahead token, and scanner buffer.
- Reads decimal and hexadecimal numerals, with locale decimal-point retry.
- Reads long strings/comments with `[=*[` delimiters.
- Reads short strings and escapes, including simple escapes, hex escapes, decimal escapes, escaped newlines, and `\z` whitespace skipping.
- Tokenizes comments, operators, punctuation, reserved words, identifiers, strings, numbers, and EOF.
- Provides one-token lookahead.

## Integration Points

The parser drives this file through `luaX_next` and `luaX_lookahead`. It depends on `lctype`, `lobject`, `lstring`, `ltable`, `lzio`, and `ldo` for classification, interned strings, dynamic buffers, and syntax errors.

## Risk Notes

Lexer risks include buffer growth limits, long-string delimiter matching, numeric locale behavior, escape validation, and line-number overflow. String anchoring prevents GC from collecting tokens during parsing.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.h

## Role

`llex.h` defines token IDs, token semantic payloads, and lexer state.

## Main Responsibilities

- Defines `FIRST_RESERVED`, reserved-word/token enum values, and `NUM_RESERVED`.
- Defines `SemInfo` for numeric and string token values.
- Defines `Token` and `LexState`, including current character, line counters, current/lookahead tokens, parser function state, stream, buffer, dynamic parser data, source, environment name, and decimal point.
- Declares lexer initialization, input setup, string interning, token advance/lookahead, syntax error, and token-to-string helpers.

## Integration Points

Shared between the lexer, parser, and code generator.

## Risk Notes

The enum order is coupled to `luaX_tokens` and reserved-word initialization. Changes require coordinated updates.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llimits.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llimits.h

## Role

`llimits.h` centralizes Lua's internal limits, memory-size types, casts, assertions, stack/call limits, instruction type, number conversion helpers, locking hooks, and hard-test hooks.

## Main Responsibilities

- Defines `lu_int32`, `lu_mem`, `l_mem`, `lu_byte`, memory maxima, `MAX_INT`, pointer hashing conversion, and alignment type.
- Defines internal and API assertion helpers, casts, unused markers, and `l_noret`.
- Sets `LUAI_MAXCCALLS` to 20 in this tree, with a comment noting amd64 stack-margin concerns.
- Defines `MAXUPVAL`, `Instruction`, `MAXSTACK`, minimum string-table size, and minimum scanner buffer size.
- Provides default no-op locking/yield/userstate hooks.
- Implements or selects number-to-integer/unsigned conversions and unsigned-to-number conversion.
- Routes numeric hashing through `lcompat_hashnum` when compiling table code and no other `luai_hashnum` is defined.
- Defines `condmovestack` and `condchangemem` hard-test hooks.

## Integration Points

Included by nearly all internal Lua headers. It adapts the upstream Lua runtime to illumos/ZFS kernel constraints through headers, call-depth limits, and compatibility hooks.

## Risk Notes

Build-wide numeric and stack assumptions live here. The low `LUAI_MAXCCALLS` is a deliberate safety bound; raising it can increase kernel stack risk. Numeric conversion and hashing settings affect table key behavior.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llimits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.c

## Role

`lmem.c` implements Lua's memory manager interface around the configured allocator.

## Main Responsibilities

- Grows dynamic arrays with doubling up to a limit, enforcing minimum array size and reporting limit errors by object type.
- Reports oversized allocations with a Lua runtime error.
- Implements `luaM_realloc_`, including allocator invocation, emergency full-GC retry on allocation failure, shrink invariants, memory-error throwing, and GC debt accounting.

## Integration Points

All runtime allocation macros in `lmem.h` route to this implementation. It calls into `lgc` for emergency collection and `ldo` for memory-error throws.

## Risk Notes

The allocator contract is strict: shrinking cannot fail, freeing returns `NULL`, and allocation failures throw `LUA_ERRMEM`. GC debt accounting drives collector pacing.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.h

## Role

`lmem.h` defines allocation, free, reallocation, vector growth, and overflow-checking macros for the Lua core.

## Main Responsibilities

- Provides `luaM_reallocv` with element-count overflow checking.
- Defines macros for freeing memory/arrays, allocating objects/vectors, growing vectors, and reallocating vectors.
- Declares `luaM_toobig`, `luaM_realloc_`, and `luaM_growaux_`.

## Integration Points

Used by nearly every file that allocates dynamic runtime structures: prototypes, bytecode arrays, strings, tables, stacks, parser buffers, and GC objects.

## Risk Notes

The overflow check protects `n * element_size` calculations. Callers must pass correct old sizes so allocator accounting and frees remain valid.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.c

## Role

`lobject.c` implements generic helpers over Lua objects: nil sentinel, integer/log encodings, arithmetic dispatch, numeric parsing, formatted string construction, and chunk ID formatting.

## Main Responsibilities

- Defines the global immutable nil object used for invalid indexes.
- Converts integers to and from Lua's floating-point-byte encoding for table size hints.
- Computes ceiling log2 for table sizing.
- Dispatches arithmetic operations through `luai_num*` macros.
- Parses hex digits and numeric strings, rejecting NaN/Inf spellings.
- Provides a fallback C99-style hexadecimal numeric parser.
- Builds Lua strings from a restricted internal format set: `%s`, `%c`, `%d`, `%f`, `%p`, and `%%`.
- Formats source names into chunk IDs for diagnostics, handling literal sources, file sources, and string snippets.

## Integration Points

Used by lexer, parser, VM, API, debug, and table code. It relies on `lcompat_sprintf` for pointer formatting in this illumos/ZFS environment.

## Risk Notes

Numeric parsing and formatting affect compiler diagnostics and constants. The fallback hex parser uses `1 << e`, so it inherits assumptions from Lua's numeric configuration.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.h

## Role

`lobject.h` defines Lua's core runtime object model: tagged values, collectable-object headers, strings, userdata, prototypes, upvalues, closures, tables, nodes, and object access/mutation macros.

## Main Responsibilities

- Defines extra internal tags for prototypes, upvalues, and dead table keys.
- Encodes type variants for Lua closures, light C functions, C closures, short strings, and long strings.
- Defines `TValue`, `Value`, type tests, accessors, false-value logic, collectability tests, liveness checks, and setter macros.
- Supports optional NaN-trick representation.
- Defines `TString`, `Udata`, `Upvaldesc`, `LocVar`, `Proto`, `UpVal`, `CClosure`, `LClosure`, `Closure`, `TKey`, `Node`, and `Table`.
- Defines table sizing helpers, fixed nil object declaration, and object helper declarations.

## Integration Points

This is the central internal header for the Lua runtime. All major subsystems depend on these layouts and macros.

## Risk Notes

The type/tag layout is foundational. Setter macros include liveness checks but not write barriers; callers that store collectable values into already-black objects must invoke the appropriate GC barrier.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.c

## Role

`lopcodes.c` provides opcode names and opcode-mode metadata for the Lua VM.

## Main Responsibilities

- Defines `luaP_opnames`, mapping every opcode to a printable name.
- Defines `luaP_opmodes`, describing each opcode's instruction format, whether it is a test, whether it sets register A, and how B/C operands are interpreted.

## Integration Points

Code generation, debug symbolic execution, disassembly-style diagnostics, and the VM depend on these arrays matching the `OpCode` enum order in `lopcodes.h`.

## Risk Notes

The arrays are order-coupled to `OpCode`. Any opcode insertion, removal, or reorder must update this file atomically.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.h

## Role

`lopcodes.h` defines Lua VM instruction encoding, operand extraction/mutation macros, RK operand encoding, opcode enum values, and opcode metadata accessors.

## Main Responsibilities

- Defines instruction formats `iABC`, `iABx`, `iAsBx`, and `iAx`.
- Defines bit sizes and positions for opcode, A, B, C, Bx, sBx, and Ax fields.
- Defines maximum operand values, instruction masks, `GETARG_*`, `SETARG_*`, and `CREATE_*` macros.
- Defines RK constant/register operand tagging through `BITRK`, `ISK`, `INDEXK`, `MAXINDEXRK`, and `RKASK`.
- Defines `NO_REG`.
- Enumerates all VM opcodes from `OP_MOVE` through `OP_EXTRAARG`, with comments describing register effects.
- Documents open-argument behavior for `CALL`, `VARARG`, `RETURN`, `SETLIST`, and `LOADKX`.
- Defines opcode argument-mode metadata helpers and `LFIELDS_PER_FLUSH`.

## Integration Points

Used by the VM, compiler, dumper/undumper, and debug symbolic execution. It must remain synchronized with `lopcodes.c` and `lvm.c`.

## Risk Notes

Instruction encoding assumes unsigned 32-bit-compatible `Instruction` values. Field-size or enum changes affect binary chunk compatibility and all generated bytecode.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.h -->
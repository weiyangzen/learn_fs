# Group Research: group_521_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_2163605ebcc4

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.c

## Purpose

Implements the Lua 5.2 parser and bytecode-generation front end for the ZFS-embedded Lua runtime. It consumes tokens from `llex`, builds `Proto` objects, manages lexical scopes/upvalues/goto labels, and emits VM instructions through `lcode`.

## Main Entry Point

- `luaY_parser(lua_State *L, ZIO *z, Mbuffer *buff, Dyndata *dyd, const char *name, int firstchar)`: creates the top-level closure/prototype, initializes lexical input, parses the main function, and returns the closure anchored on the Lua stack.

## Core Behavior

- Tracks function compilation with `FuncState`: current `Proto`, constants table, active blocks, bytecode PC, active locals, upvalues, and register allocation.
- Tracks parser dynamic state with `Dyndata`: active locals, pending gotos, and visible labels.
- Implements Lua grammar for expressions, table constructors, function definitions/calls, assignments, `if`, `while`, `repeat`, numeric/generic `for`, `do`, `local`, labels, `goto`, `break`, and `return`.
- Resolves names as locals, upvalues, or `_ENV` indexed globals.
- Handles closure creation by adding child prototypes to the parent and emitting `OP_CLOSURE`.
- Enforces parser limits including `MAXVARS`, `MAXUPVAL`, bytecode argument limits, and recursive C-call depth.
- Handles assignment conflicts where a later local/upvalue assignment would invalidate earlier table assignment operands.
- Implements Lua 5.2 label/goto rules, including prevention of jumping into local variable scope and generation of close instructions when gotos leave upvalue-owning scopes.

## Dependencies

- Lexer/token APIs: `llex.h`.
- Bytecode emission and patching: `lcode.h`, `lopcodes.h`.
- Runtime object model: `lobject.h`, `lfunc.h`, `lstate.h`, `lstring.h`, `ltable.h`.
- Error reporting and GC barriers: `ldebug.h`, `ldo.h`, `lmem.h`.

## Risks And Notes

- Scope and goto handling is the most error-prone area: `closegoto`, `findlabel`, `movegotosout`, and `leaveblock` must preserve Lua’s no-jump-into-scope rule and close upvalues on exits.
- Register allocation depends on the invariant `freereg >= nactvar`; each statement resets temporary registers after code generation.
- `anchor_token` protects token strings across function closure finalization and GC.
- The main chunk is always vararg and receives `_ENV` as its sole upvalue.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.h

## Purpose

Defines parser-facing data structures used by `lparser.c` and bytecode generation.

## Key Definitions

- `expkind`: expression forms such as constants, locals, upvalues, indexed expressions, jumps, relocatable instructions, calls, and varargs.
- `expdesc`: expression descriptor with kind-specific payload plus true/false jump patch lists.
- `Vardesc`: active local variable descriptor.
- `Labeldesc` and `Labellist`: label/goto tracking records.
- `Dyndata`: parser dynamic arrays for active locals, gotos, and labels.
- `FuncState`: compilation state for one Lua function/prototype.

## Public Interface

- `luaY_parser(...)`: parser entry point implemented in `lparser.c`.

## Dependencies

- `llimits.h`, `lobject.h`, and `lzio.h`.

## Risks And Notes

- The numeric sizes of `FuncState` fields are tied to Lua bytecode limits, especially `lu_byte` counts for active locals/upvalues/registers.
- `VINDEXED` stores table/index register-or-constant metadata compactly; misuse can generate invalid `OP_GETTABLE`/`OP_SETTABLE` operands.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.c

## Purpose

Implements creation, initialization, thread allocation, and teardown of Lua runtime state for the embedded ZFS Lua interpreter.

## Main APIs

- `lua_newstate(lua_Alloc f, void *ud)`: allocates main `lua_State` plus `global_State`, seeds hashing, initializes GC state, and runs protected runtime initialization.
- `lua_close(lua_State *L)`: closes the main thread and frees all runtime state.
- `lua_newthread(lua_State *L)`: creates a coroutine/thread sharing the same global state.
- `luaE_freethread(lua_State *L, lua_State *L1)`: frees a thread.
- `luaE_extendCI`, `luaE_freeCI`: manage dynamic call-info frames.
- `luaE_setdebt`: adjusts GC accounting while preserving total allocation accounting.

## Core Behavior

- `stack_init` allocates the initial Lua stack and base `CallInfo`.
- `init_registry` creates the registry and stores `LUA_RIDX_MAINTHREAD` and `LUA_RIDX_GLOBALS`.
- `f_luaopen` initializes stack, registry, string table, tag-method names, lexer reserved words, memory-error string, and runtime version.
- `makeseed` mixes `gethrtime()`, stack/heap/global/function addresses, and `luaS_hash` to seed string/table hashing.
- `close_state` closes upvalues, frees all GC objects, string table, global buffer, stack, and the top-level allocation.

## Dependencies

- Memory and protected-call internals: `lmem.h`, `ldo.h`.
- GC and object lifecycle: `lgc.h`, `lfunc.h`, `lstring.h`, `ltable.h`.
- Lexer/metamethod initialization: `llex.h`, `ltm.h`.

## Risks And Notes

- Partial initialization failures are handled through `luaD_rawrunprotected`; `close_state` must tolerate partially built state.
- `lua_close` always closes the main thread, even if called with a coroutine.
- Hash seed generation is adapted for illumos via `gethrtime()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.h

## Purpose

Defines Lua global state, per-thread state, call-frame state, GC object union, and core state-management declarations.

## Key Structures

- `stringtable`: interned short-string hash table.
- `CallInfo`: stack frame metadata for Lua and C calls, including saved PC/base for Lua functions and continuation/error metadata for C calls.
- `global_State`: allocator, GC accounting/lists, string table, registry, hash seed, global buffer, panic handler, main thread, fixed memory-error string, tag-method names, and per-type metatables.
- `lua_State`: per-thread execution stack, current call info, hook state, open upvalues, error jump, and base C-call frame.
- `GCObject`: union over all collectable object types: strings, userdata, closures, tables, prototypes, upvalues, and threads.

## Important Constants

- `EXTRA_STACK`: extra stack slots for metamethod calls and runtime internals.
- `BASIC_STACK_SIZE`: initial stack size.
- `KGC_NORMAL`, `KGC_EMERGENCY`, `KGC_GEN`: GC modes.
- `CIST_*`: call-status flags for Lua/C frame state, yields, protected calls, tail calls, and hooks.

## Public/Internal APIs

- `luaE_setdebt`
- `luaE_freethread`
- `luaE_extendCI`
- `luaE_freeCI`

## Risks And Notes

- GC list comments describe object ownership invariants; violating these breaks collector reachability.
- `CallInfo` state is central to VM reentry/yield behavior.
- `gettotalbytes(g)` combines `totalbytes + GCdebt`; allocation accounting assumes that invariant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.c

## Purpose

Implements Lua string hashing, short-string interning, long-string creation/equality, string-table resizing, and userdata allocation.

## Main APIs

- `luaS_hash`: seeded hash over a bounded sample of string bytes.
- `luaS_eqlngstr`, `luaS_eqstr`: long/general string equality.
- `luaS_resize`: resize and rehash the interned short-string table.
- `luaS_newlstr`, `luaS_new`: create strings.
- `luaS_newudata`: allocate userdata with environment/metatable fields.

## Core Behavior

- Short strings up to `LUAI_MAXSHORTLEN` are interned and reused.
- Long strings are not interned; equality compares length and content.
- Dead short strings found during lookup are resurrected with `changewhite`.
- String-table resize waits until GC is not in string-sweep state and resets old bits during rehash.
- New string objects store a trailing NUL after explicit-length payloads.

## Dependencies

- GC object allocation: `lgc.h`.
- Memory helpers: `lmem.h`.
- State/string table: `lstate.h`.

## Risks And Notes

- Hashing samples at most roughly `2^LUAI_HASHLIMIT` bytes, so adversarial long strings rely on randomized seed for mitigation.
- Short-string interning assumes the string table has already been initialized by `luaS_resize`.
- Long-string hash is initially the global seed and may be lazily computed elsewhere for table hashing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.h

## Purpose

Declares Lua string/userdata allocation and equality helpers plus string-size and interned-string macros.

## Key Definitions

- `sizestring`, `sizeudata`: allocation-size helpers.
- `luaS_newliteral`: literal string creation.
- `luaS_fix`: marks a string as fixed/non-collectable.
- `isreserved`: detects reserved-word short strings using `extra`.
- `eqshrstr`: short-string equality by pointer identity.

## APIs

- `luaS_hash`
- `luaS_eqlngstr`
- `luaS_eqstr`
- `luaS_resize`
- `luaS_newudata`
- `luaS_newlstr`
- `luaS_new`

## Risks And Notes

- `eqshrstr` depends on all short strings being interned.
- `isreserved` reuses the `extra` byte; code that mutates it must preserve lexer/metamethod assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstrlib.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstrlib.c

## Purpose

Implements Lua’s standard `string` library for the ZFS-embedded Lua runtime.

## Library Functions

Registers:

- `string.byte`
- `string.char`
- `string.dump`
- `string.find`
- `string.format`
- `string.gmatch`
- `string.gsub`
- `string.len`
- `string.lower`
- `string.match`
- `string.rep`
- `string.reverse`
- `string.sub`
- `string.upper`

## Core Behavior

- Basic string functions operate on explicit byte lengths, not C-string length.
- Pattern matching implements Lua patterns with captures, balanced matches `%b`, frontier `%f`, back references, greedy/minimal repetitions, and recursion-depth protection.
- `find` uses a plain byte search when requested or when the pattern contains no special characters.
- `gmatch` returns a closure over source, pattern, and current byte offset.
- `gsub` supports string/number replacements, function replacements, and table lookups.
- `format` scans restricted printf-style format specifiers, supports quoted `%q`, integer formats, string formats, and conditionally floating formats depending on build macros.
- `luaopen_string` creates the library table and installs it as the metatable `__index` for strings.

## illumos/ZFS Adaptations

- Includes `<sys/ctype.h>` and `<sys/zfs_context.h>`.
- Adds local `tolower`, `toupper`, `isgraph`, and `ispunct` macros.
- Adds local `iscntrl`.
- Uses `str_sprintf` wrapper over `vsnprintf` because the available `sprintf` compatibility function does not match the expected return type.

## Dependencies

- Public Lua API: `lua.h`.
- Auxiliary library and standard-library registration: `lauxlib.h`, `lualib.h`.

## Risks And Notes

- Pattern matching uses recursive calls bounded by `MAXCCALLS`; complex patterns throw `"pattern too complex"`.
- Capture storage is fixed at `LUA_MAXCAPTURES` default 32.
- `str_rep`, `str_byte`, and `unpack`-style result pushing guard against overflow/stack exhaustion.
- Character classification is ASCII-oriented in the patched macros.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstrlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.c

## Purpose

Implements Lua table storage: split array/hash layout, lookup, insertion, resizing, iteration, and length-boundary search.

## Main APIs

- `luaH_new`, `luaH_free`
- `luaH_get`, `luaH_getint`, `luaH_getstr`
- `luaH_set`, `luaH_setint`, `luaH_newkey`
- `luaH_resize`, `luaH_resizearray`
- `luaH_next`
- `luaH_getn`

## Core Behavior

- Tables have an array part for positive integer keys and a hash part for all other keys.
- Array size is chosen so at least half the slots up to the chosen power-of-two boundary are used.
- Hash part uses chained scatter with Brent’s variation; if a colliding node is not in its main position, insertion moves it to preserve lookup performance.
- Short-string lookups use interned-string pointer/hash fast path.
- Long-string keys lazily compute their hash in `mainposition`.
- `luaH_next` traverses array entries first, then hash nodes.
- `luaH_getn` implements Lua length boundary search using binary search in array part or exponential/binary search into hash part.

## Dependencies

- Lua object model and equality: `lobject.h`, `lvm.h`.
- Memory/GC/error support: `lmem.h`, `lgc.h`, `ldebug.h`, `ldo.h`.
- State and strings: `lstate.h`, `lstring.h`.

## Risks And Notes

- `luaH_newkey` rejects nil and NaN table keys.
- Callers of `luaH_set` must handle write barriers and metamethod-cache invalidation as needed.
- `lastfree` scanning and dummy-node handling are important for empty hash tables.
- Length behavior follows Lua’s boundary semantics and is undefined for sparse arrays with multiple valid boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.h

## Purpose

Declares Lua table operations and node-access macros.

## Key Definitions

- `gnode`, `gkey`, `gval`, `gnext`: access table hash nodes.
- `invalidateTMcache`: clears cached absence flags for metamethod lookup.
- `keyfromval`: derives a node key pointer from its value pointer.

## APIs

- Lookup/set/allocation/resizing/freeing APIs implemented in `ltable.c`.
- Debug-only `luaH_mainposition` and `luaH_isdummy`.

## Risks And Notes

- `keyfromval` relies on `Node` field layout and is pointer-arithmetic-sensitive.
- `invalidateTMcache` must be called when table mutations can affect metamethod lookup assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltablib.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltablib.c

## Purpose

Implements Lua’s standard `table` library.

## Library Functions

Registers:

- `table.concat`
- `table.insert`
- `table.pack`
- `table.unpack`
- `table.remove`
- `table.sort`
- optional `table.maxn` under `LUA_COMPAT_MAXN`
- optional global `unpack` under `LUA_COMPAT_UNPACK`

## Core Behavior

- `insert` appends or shifts entries upward to insert at a validated position.
- `remove` returns the removed entry, shifts entries down, and nils the old tail.
- `concat` concatenates table elements in a requested range with an optional separator.
- `pack` creates an array-like table and stores argument count in field `n`.
- `unpack` pushes a range of raw integer-indexed table entries with stack overflow checks.
- `sort` uses quicksort with median-of-three pivoting, tail-recursion reduction, and optional comparator function.

## Dependencies

- Public Lua API and auxiliary checks: `lua.h`, `lauxlib.h`.
- Standard library declarations: `lualib.h`.

## Risks And Notes

- `sort` detects invalid order functions when partition scans cross bounds.
- Length comes from `luaL_len`, so sparse-table behavior follows Lua length semantics.
- Integer positions use `int`, so very large table lengths can be constrained by C integer limits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltablib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.c

## Purpose

Implements tag-method/metamethod name initialization and lookup helpers.

## Main APIs

- `luaT_init`: interns and fixes all metamethod names.
- `luaT_gettm`: optimized table metamethod lookup used by `fasttm`; caches absence for fast-access metamethods.
- `luaT_gettmbyobj`: retrieves the relevant metatable for tables, userdata, or primitive types and returns the event value.

## Core Behavior

- Defines human-readable type names in `luaT_typenames_`.
- Interns `__index`, `__newindex`, `__gc`, `__mode`, `__len`, `__eq`, arithmetic/comparison names, `__concat`, and `__call`.
- Caches absent fast metamethods by setting bits in `Table.flags`.

## Dependencies

- `lobject.h`, `lstate.h`, `lstring.h`, `ltable.h`, `ltm.h`.

## Risks And Notes

- The order of `luaT_eventname` must match the `TMS` enum in `ltm.h`.
- `luaT_gettm` asserts `event <= TM_EQ`; later metamethods are not absence-cached through this path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.h

## Purpose

Defines Lua metamethod event enumeration and lookup macros.

## Key Definitions

- `TMS`: ordered metamethod IDs from `TM_INDEX` through `TM_CALL`.
- `gfasttm` / `fasttm`: quick metamethod lookup with cached absence flags.
- `ttypename`, `objtypename`: type-name lookup helpers.

## APIs

- `luaT_gettm`
- `luaT_gettmbyobj`
- `luaT_init`
- `luaT_typenames_`

## Risks And Notes

- Enum order is shared with arithmetic opcode constants and event-name arrays; changing it requires coordinated changes across the VM and object code.
- Only events up to `TM_EQ` use fast absence caching.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lua.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lua.h

## Purpose

Public Lua 5.2.4 C API header, adapted to include ZFS kernel context and local `luaconf.h`.

## Main Contents

- Version constants: Lua 5.2 release 5.2.4.
- Basic public types: `lua_State`, `lua_CFunction`, `lua_Reader`, `lua_Writer`, `lua_Alloc`, `lua_Number`, `lua_Integer`, `lua_Unsigned`.
- Type tags and status/error codes.
- Registry pseudo-index and registry predefined keys.
- Public state, stack, access, push, get, set, load/call, coroutine, GC, and miscellaneous APIs.
- Convenience macros for common stack/API operations.
- Debug API event codes, masks, `lua_Hook`, and `lua_Debug`.

## Dependencies

- Includes `<sys/zfs_context.h>` and `luaconf.h`.

## Risks And Notes

- This header exposes the ABI expected by the embedded Lua runtime; `luaconf.h` changes such as `lua_Number=int64_t` affect chunk compatibility and API behavior.
- `lua_dump` here has the Lua 5.2 three-argument public signature, while internal dump helpers may carry strip flags.
- Debug metadata structure layout is part of the public API for debug hooks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lua.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/luaconf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/luaconf.h

## Purpose

Configures the embedded Lua build for illumos/ZFS.

## Important Local Adaptations

- Includes `<sys/zfs_context.h>` and `<sys/int_fmtio.h>`.
- Declares compatibility helpers:
  - `lcompat_sprintf`
  - `lcompat_strtoll`
  - `lcompat_pow`
- Uses `zfs_dbgmsg` for `luai_writestringerror` when `_KERNEL` is defined.
- Defines `LUA_NUMBER` as `int64_t`, not `double`.
- Defines numeric parsing/formatting through `lcompat_strtoll` and `lcompat_sprintf`.
- Defines `LUA_UNSIGNED` as `uint64_t`.
- Forces locale decimal point to `'.'`.
- Supplies local `abs` and `UCHAR_MAX` fallback definitions.

## Core Configuration

- Default Lua module paths and C module paths are retained for non-Windows builds.
- `LUA_API` defaults to `extern`; internal symbols may use ELF hidden visibility under GCC/ELF.
- `LUAI_MAXSHORTLEN` is 40.
- `LUAI_MAXSTACK` is 1,000,000 on 32-bit-or-larger `int`.
- `LUAL_BUFFERSIZE` is 1024.
- Compatibility macros are available when `LUA_COMPAT_ALL` is defined.

## Numeric Semantics

- Arithmetic macros operate on integral `int64_t` Lua numbers.
- `%` is integer modulo.
- Power calls `lcompat_pow`.
- `lua_number2str` formats with `PRId64`.

## Risks And Notes

- Integer `lua_Number` is a major behavioral difference from stock Lua 5.2’s typical `double` configuration.
- Binary chunks are ABI-sensitive; `lundump.c` validates `sizeof(lua_Number)` and whether it is integral.
- Floating `string.format` support is conditional and may be unavailable unless configured.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/luaconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lualib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lualib.h

## Purpose

Declares Lua standard library opening functions and standard library names.

## Declared Libraries

- Base
- Coroutine
- Table
- IO
- OS
- String
- Bit32
- Math
- Debug
- Package

## Main API

- `luaL_openlibs(lua_State *L)`: opens all standard libraries.

## Dependencies

- `lua.h`.

## Risks And Notes

- This header declares all standard Lua libraries, but an embedded/kernel build may compile or expose only a subset.
- Defines `lua_assert` as no-op if not already defined.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lualib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.c

## Purpose

Loads precompiled Lua binary chunks into runtime `Closure`/`Proto` structures.

## Main APIs

- `luaU_undump(lua_State *L, ZIO *Z, Mbuffer *buff, const char *name)`: loads one precompiled chunk from a `ZIO`.
- `luaU_header(lu_byte *h)`: constructs the expected binary chunk header for this build.

## Core Behavior

- Reads primitive values, vectors, strings, bytecode, constants, nested prototypes, upvalues, line info, local-variable debug info, and upvalue names.
- Validates all integer counts are non-negative.
- Validates the binary header against signature, Lua version, format, endianness, `sizeof(int)`, `sizeof(size_t)`, `sizeof(Instruction)`, `sizeof(lua_Number)`, and integral-number flag.
- Creates a top-level Lua closure, loads its prototype, and adjusts closure upvalue count if needed.
- Throws `LUA_ERRSYNTAX` on truncated, incompatible, or corrupted chunks.

## Dependencies

- Object/prototype allocation: `lfunc.h`, `lobject.h`.
- Protected error throwing: `ldo.h`.
- Memory and strings: `lmem.h`, `lstring.h`.
- Buffered input: `lzio.h`.

## Risks And Notes

- Binary chunks are not portable across builds with different integer sizes, instruction sizes, endianness, or `lua_Number` configuration.
- `LoadString` reads the serialized trailing NUL but interns/creates the string without it.
- `luai_verifycode` is empty unless configured; bytecode verification may be absent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.h

## Purpose

Declares Lua binary chunk dump/undump helpers and binary chunk header constants.

## APIs

- `luaU_undump`
- `luaU_header`
- `luaU_dump`

## Constants

- `LUAC_TAIL`: byte trailer used to detect conversion/corruption errors.
- `LUAC_HEADERSIZE`: expected binary header size.

## Risks And Notes

- Header size must remain consistent with both `luaU_header` and `LoadHeader` in `lundump.c`.
- `luaU_dump` is declared here but implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.c

## Purpose

Implements the Lua virtual machine execution engine and core runtime operations for arithmetic, comparison, table access, concatenation, length, closures, hooks, and bytecode dispatch.

## Main APIs

- `luaV_execute`: main bytecode interpreter loop.
- `luaV_finishOp`: completes an opcode interrupted by yield.
- `luaV_gettable`, `luaV_settable`: table indexing/assignment with metamethod handling.
- `luaV_arith`: arithmetic with numeric conversion and metamethod fallback.
- `luaV_concat`: concatenation with conversion and `__concat`.
- `luaV_objlen`: length operation with `__len`.
- `luaV_lessthan`, `luaV_lessequal`, `luaV_equalobj_`: comparison/equality semantics.
- `luaV_tonumber`, `luaV_tostring`: conversion helpers.

## Core Behavior

- Dispatches all Lua 5.2 VM opcodes including loads, upvalues, table ops, arithmetic, comparisons, tests, calls, tail calls, returns, numeric/generic loops, `SETLIST`, closures, varargs, and `EXTRAARG`.
- Handles metamethod loops with a `MAXTAGLOOP` bound.
- Performs hook dispatch for line/count hooks and preserves yield semantics from hooks/metamethods.
- Reuses cached closures when a prototype’s upvalue identities match.
- Maintains stack and `CallInfo` invariants across calls, tail calls, returns, GC checks, and stack reallocations.

## illumos/ZFS Adaptations

- Defines `strcoll(l,r)` as `strcmp((l),(r))`.
- Patches division and modulo behavior using Lua 5.3.2-derived `luaV_div` and `luaV_mod` to avoid divide-by-zero crashes under integral `lua_Number`.
- `OP_DIV` and `OP_MOD` use patched helpers directly in the fast numeric path.

## Dependencies

- Call/stack/error support: `ldo.h`, `ldebug.h`.
- Functions/upvalues: `lfunc.h`.
- GC barriers: `lgc.h`.
- Objects/opcodes/state/strings/tables/metamethods: `lobject.h`, `lopcodes.h`, `lstate.h`, `lstring.h`, `ltable.h`, `ltm.h`.

## Risks And Notes

- Integral `lua_Number` changes division, modulo, comparison, formatting, and binary chunk behavior relative to stock double-based Lua.
- Yield-resume paths in `luaV_finishOp` must match every opcode that can yield through a metamethod or call.
- `luaV_gettable`/`luaV_settable` protect against metamethod cycles via `MAXTAGLOOP`.
- Stack pointers can be invalidated by calls and GC; the VM uses `Protect` and recomputes `base`/`ra`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.h

## Purpose

Declares Lua VM helper functions and common conversion/equality macros.

## Key Macros

- `tostring(L,o)`: true if already string or convertible number.
- `tonumber(o,n)`: true if already number or parseable string.
- `equalobj(L,o1,o2)`: raw tag equality plus Lua equality.
- `luaV_rawequalobj`: equality without metamethods.

## APIs

- Equality/comparison helpers.
- Numeric/string conversion helpers.
- Table get/set helpers.
- VM execution and yield-finish helpers.
- Concatenation, arithmetic, and length helpers.

## Risks And Notes

- `tonumber` mutates its first macro argument when conversion succeeds; callers must pass an assignable expression.
- `luaV_rawequalobj` passes `NULL` as state, suppressing metamethod equality.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.c

## Purpose

Implements Lua buffered input streams and reusable parser/loader buffers.

## Main APIs

- `luaZ_init`: initializes a `ZIO` from a Lua reader callback and user data.
- `luaZ_fill`: obtains the next reader buffer and returns the first byte.
- `luaZ_read`: reads an exact byte count or returns missing byte count at EOF.
- `luaZ_openspace`: ensures an `Mbuffer` has at least the requested size.

## Core Behavior

- `luaZ_fill` unlocks the Lua state while calling the external reader, then relocks it.
- `luaZ_read` copies from buffered chunks and refills as needed.
- `luaZ_openspace` grows buffers to at least `LUA_MINBUFFER`.

## Dependencies

- Memory resizing macros from `lmem.h`.
- State locking macros from `lstate.h`/`lua.h`.

## Risks And Notes

- Reader callbacks must keep returned buffers valid until consumed.
- `luaZ_read` returns the remaining unread byte count, not a conventional success/failure boolean.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.h

## Purpose

Declares buffered stream and memory-buffer structures used by the lexer/parser and binary chunk loader.

## Key Definitions

- `EOZ`: end-of-stream sentinel.
- `ZIO`: buffered reader state.
- `zgetc`: fast byte fetch macro.
- `Mbuffer`: growable temporary memory buffer.
- Buffer macros for init, access, length reset, resize, and free.

## APIs

- `luaZ_openspace`
- `luaZ_init`
- `luaZ_read`
- `luaZ_fill`

## Risks And Notes

- `zgetc` decrements `n` before checking; it relies on unsigned wrap behavior matching the macro’s intended fast path.
- `Mbuffer.n` is separate from allocated `buffsize`; callers must maintain logical length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lzjb.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lzjb.c

## Purpose

Provides ZFS’s private deterministic copy of the LZJB compression algorithm for on-disk-format stability and deduplication consistency.

## Main APIs

- `lzjb_compress(void *s_start, void *d_start, size_t s_len, size_t d_len, int n)`: compresses source into destination and returns compressed size, or original source length if output would overflow.
- `lzjb_decompress(void *s_start, void *d_start, size_t s_len, size_t d_len, int n)`: decompresses into a fixed-size destination and returns 0 or -1 for invalid back-reference offset.

## Core Behavior

- Uses 3-byte minimum matches, 6 match-length bits, 10 offset bits, and a 1024-entry Lempel table.
- Compression initializes the Lempel table to zero for deterministic output.
- Emits a copymap byte for each group of literal/match decisions.
- Compression bounds output against destination space and falls back by returning `s_len` if compression would not fit.
- Decompression follows copymap bits and copies either literal bytes or back-referenced match runs until destination is filled.

## Dependencies

- `<sys/types.h>` and `<sys/param.h>` for illumos types and `NBBY`.

## Risks And Notes

- This copy is intentionally separate from common OS compression code because changes would affect ZFS on-disk compatibility.
- Decompression trusts compressed source length less than destination length; it primarily bounds destination writes and validates back-reference origin.
- The `n` argument is unused in both functions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lzjb.c -->
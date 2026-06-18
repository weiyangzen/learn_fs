# subset-b-009337 Research

Grouped research for the requested strace architecture source files. Each section title preserves the source path and each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/syscallent.h -->
# sources/test-tools/strace/src/linux/sparc64/syscallent.h

## Purpose
Defines the SPARC64 primary syscall dispatch table consumed by `syscall.c` through the `syscallent.h` include path. The entries map numeric syscall IDs to argument counts, strace classification flags, decoder symbols via `SEN(...)`, and displayed syscall names. This table is SPARC-specific rather than a generic 64-bit table because SPARC keeps historical numbering, sparc32 holes, SPARC-only calls, socket subcalls, and IPC placement.

## Important APIs, Types, and Functions
The file contributes initializer rows for `struct_sysent` arrays built in `syscall.c`. It uses strace table macros such as `SEN`, flags like `TD`, `TF`, `TP`, `TS`, `TCL`, `TM`, `TI`, `NF`, `PU`, and decoder names including `clock_sparc64_adjtime`, `adjtimex64`, `rt_sigtimedwait_time64`, `futex_time64`, and `printargs`. It defines `SYS_socket_subcall 500` before including `../64/subcallent.h`, which aligns socket subcall decoding for SPARC64.

## Control Flow and Integration
There is no runtime control flow in this header; compile-time inclusion creates the syscall table. `syscall.c` indexes the resulting table by `tcp->scno` after architecture-specific syscall-number extraction. The table includes `syscallent-common.h` after a reserved SPARC range and includes 64-bit subcalls after setting the socket subcall base. Comments mark sparc32-only slots and reserved gaps so the primary 64-bit personality does not accidentally decode 32-bit-only syscalls.

## State and Persistence
The file stores no mutable state. Its persistent effect is the compiled static syscall metadata used for tracing, filtering, seccomp BPF generation, counting, and syscall name lookup.

## Dependencies
Depends on the surrounding strace syscall table machinery: `syscall.c` table inclusion, decoder declarations, flag macros, SPARC common entries, and `../64/subcallent.h`. Several decoder names depend on architecture-specific time/stat/IPCs support elsewhere in the source tree.

## Risks
Wrong numbers or flags cause silent mis-decoding, incorrect filtering, or wrong argument formatting for SPARC64. Time-related rows are sensitive because SPARC64 uses 64-bit time decoders for many historical syscall numbers. The socket subcall base must remain coordinated with `../64/subcallent.h`. Gaps documented as sparc32-only or reserved should not be filled without confirming kernel ABI numbering.

## Test Signals
Useful signals include successful compile of the SPARC64 table, syscall name lookup tests around holes and high-number common syscalls, SPARC64 traces for `clock_adjtime`, `adjtimex`, IPC calls at 392-402, and socket subcalls beginning at 500. Generated table sanity checks should verify no entry exceeds `MAX_ARGS` and that common includes land after the intended reserved range.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/syscallent1.h -->
# sources/test-tools/strace/src/linux/sparc64/syscallent1.h

## Purpose
Provides the secondary SPARC64 personality syscall table by including `../sparc/syscallent.h`. In strace's multi-personality builds this represents the 32-bit SPARC personality traced by a SPARC64 build.

## Important APIs, Types, and Functions
Exports no functions or local definitions. Its only API surface is the include indirection that lets `syscall.c` build `sysent1` when `SUPPORTED_PERSONALITIES > 1`.

## Control Flow and Integration
Compile-time inclusion pulls in the SPARC 32-bit syscall initializer rows. Runtime personality selection in `syscall.c` and architecture code determines whether the table from this file or the primary `sparc64/syscallent.h` table is used.

## State and Persistence
No local state. The compiled result is a static syscall metadata table for the 32-bit SPARC personality.

## Dependencies
Depends entirely on `sources/test-tools/strace/src/linux/sparc/syscallent.h` and on the multi-personality table logic in `syscall.c`.

## Risks
The risk is mostly ABI routing: if SPARC64 personality detection chooses this table incorrectly, syscall names and argument widths will be wrong. Changes to the included SPARC table automatically affect SPARC64 compat tracing.

## Test Signals
Look for successful multi-personality SPARC64 builds and traces from 32-bit SPARC processes under a 64-bit tracer. Filter syntax using the secondary personality should resolve syscall names from the included SPARC table.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/syscallent1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/userent.h -->
# sources/test-tools/strace/src/linux/sparc64/userent.h

## Purpose
Defines SPARC64-specific `struct user` offset names for ptrace/user area decoding, then includes the shared `userent0.h` table. It feeds strace's `ptrace` decoder when printing offsets used by `PTRACE_PEEKUSER`, `PTRACE_POKEUSER`, and similar requests.

## Important APIs, Types, and Functions
Uses `XLAT_UOFF(...)` entries for `u_tsize`, `u_dsize`, `u_ssize`, `signal`, `magic`, and `u_comm`. The macro expands into architecture-specific xlat entries expected by `ptrace.c`.

## Control Flow and Integration
There is no runtime branching. The header is included in the generated user-offset xlat table for the SPARC64 Linux port. `#include "userent0.h"` appends common or generated offsets after the SPARC64-specific user-structure fields.

## State and Persistence
No mutable state. The result is static metadata for printing user-area offsets.

## Dependencies
Depends on `XLAT_UOFF` being defined by the including xlat-generation context and on `userent0.h` existing for the rest of the architecture table.

## Risks
Offsets must match the kernel/user ABI used by strace's build headers. Stale entries make ptrace offset output misleading. Since this is table data, build failures usually catch macro problems, but ABI drift may only show up in ptrace decoding tests.

## Test Signals
Exercise `ptrace` decoding with user-area offsets and verify names appear for the listed SPARC64 fields. Regeneration of xlat tables and a SPARC64 build are the strongest compile-time signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_defs_.h -->
# sources/test-tools/strace/src/linux/tile/arch_defs_.h

## Purpose
Defines Tile architecture personality metadata used by the generic `arch_defs.h` layer. Tile supports two personalities: native TILE-Gx and either TILEPro or TILE-Gx32 compat, depending on the build target.

## Important APIs, Types, and Functions
Defines `SUPPORTED_PERSONALITIES 2`, `PERSONALITY0_AUDIT_ARCH` as `AUDIT_ARCH_TILEGX`, and `PERSONALITY1_AUDIT_ARCH` as `AUDIT_ARCH_TILEPRO` on `__tilepro__` builds or `AUDIT_ARCH_TILEGX32` otherwise. It also sets `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL 1` and defaults to personality 1 on TILEPro builds.

## Control Flow and Integration
All behavior is preprocessor-driven. `syscall_name.c`, `filter_seccomp.c`, `basic_filters.c`, and `syscall.c` consume these definitions to size personality arrays, label audit arches, and decide compat behavior.

## State and Persistence
No runtime state. The persistent result is compile-time personality configuration baked into strace.

## Dependencies
Depends on Linux audit architecture constants and on `arch_defs.h` defaults for names, word sizes, and personality designators not overridden here.

## Risks
Misconfigured audit arches break seccomp filter generation and syscall-info personality detection. The `__tilepro__` conditional is sensitive because it changes both compat audit arch and default personality.

## Test Signals
Build TileGx and TilePro variants, inspect `strace -V` personality reporting where available, and verify syscall filtering by audit arch for native and compat Tile processes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/tile/arch_get_personality.c

## Purpose
Maps `PTRACE_GET_SYSCALL_INFO` audit architecture values to the Tile personality index. It lets strace select the compat Tile table directly from kernel syscall-info metadata.

## Important APIs, Types, and Functions
Implements `get_personality_from_syscall_info(const struct_ptrace_syscall_info *sci)`. It returns true, as integer personality `1`, when `sci->arch` is `AUDIT_ARCH_TILEGX32` or `AUDIT_ARCH_TILEPRO`; otherwise it returns `0` for native TILE-Gx.

## Control Flow and Integration
The function is called through `get_personality.c` when syscall-info data is available. It is a simple boolean expression with no error return. Native Tile stays personality 0; compat Tile uses personality 1.

## State and Persistence
No state is retained. The chosen personality updates the per-tracee `tcb` through the generic personality-selection flow outside this file.

## Dependencies
Depends on `struct_ptrace_syscall_info` and audit arch constants. Its return values must match `arch_defs_.h` personality ordering and the two `syscallent` tables.

## Risks
Assumes any non-compat arch reported to this Tile build is native personality 0. If a future Tile audit arch is introduced, this fallback could classify it as native without an explicit guard.

## Test Signals
Trace native TILE-Gx, TILE-Gx32, and TILEPro syscalls with kernels supporting `PTRACE_GET_SYSCALL_INFO`; verify syscall table selection and printed personality suffixes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_regs.c -->
# sources/test-tools/strace/src/linux/tile/arch_regs.c

## Purpose
Declares the Tile register cache and maps generic register-access macros to Tile's `struct pt_regs` layout. It is included by `syscall.c` to support syscall number, argument, return-value, program-counter, and stack-pointer extraction.

## Important APIs, Types, and Functions
Defines static `struct pt_regs tile_regs`, `ARCH_REGS_FOR_GETREGS tile_regs`, `ARCH_PC_REG tile_regs.pc`, and `ARCH_SP_REG tile_regs.sp`.

## Control Flow and Integration
No functions are defined here. The generic register helpers use `ARCH_REGS_FOR_GETREGS` with ptrace `GETREGS`, then Tile-specific files read or modify `tile_regs`.

## State and Persistence
`tile_regs` is process-global static storage inside the strace process. It is a transient cache refreshed from the current tracee when generic register helpers run; it is not persisted.

## Dependencies
Depends on kernel `struct pt_regs` and the generic `get_regs`, `set_regs`, `get_stack_pointer`, and syscall engine macros. Other Tile files directly share the same `tile_regs` symbol.

## Risks
Because many Tile helpers read this static cache, stale registers can corrupt syscall decoding if `get_regs` was not called on the current tracee before use. `set_regs` writes the whole cached register set back, so callers must avoid preserving stale unrelated fields.

## Test Signals
Tile syscall tracing should show correct PC/SP reporting, syscall arguments, return values, and injected return/error changes. Build-time tests should ensure `struct pt_regs` exposes `pc` and `sp`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/tile/arch_sigreturn.c

## Purpose
Prints the signal mask restored by Tile's old `sigreturn` path. It computes the mask address inside the kernel signal frame from the tracee stack pointer and delegates decoding to `print_sigset_addr`.

## Important APIs, Types, and Functions
Defines static `arch_sigreturn(struct tcb *tcp)`. It calls `get_stack_pointer`, uses `C_ABI_SAVE_AREA_SIZE`, `sizeof(siginfo_t)`, and `offsetof(ucontext_t, uc_sigmask)`, then calls `print_sigset_addr(tcp, addr)`.

## Control Flow and Integration
Called from generic `sigreturn.c` during decoding. If stack pointer retrieval fails, it returns without output. Otherwise it adds the Tile sigframe ucontext offset and prints the saved signal mask.

## State and Persistence
No state is modified except normal output state. It reads tracee memory indirectly through `print_sigset_addr`.

## Dependencies
Depends on Tile ABI frame layout matching `rt_sigframe.h`, libc/kernel `ucontext_t`, `siginfo_t`, and generic stack-pointer helpers.

## Risks
The offset is layout-sensitive. Changes in Tile sigframe ABI, incorrect `C_ABI_SAVE_AREA_SIZE`, or mismatched headers can make strace read the wrong signal-mask address. Failure to fetch the stack pointer produces intentionally silent incomplete decoding.

## Test Signals
Tile signal-return tests should verify printed signal masks for `sigreturn` and `rt_sigreturn`. ABI offset checks against kernel headers or crafted signal frames are useful regression signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/get_error.c -->
# sources/test-tools/strace/src/linux/tile/get_error.c

## Purpose
Decodes Tile syscall return values and errno into `tcp->u_rval` and `tcp->u_error`.

## Important APIs, Types, and Functions
Includes `negated_errno.h` and defines `arch_get_error(struct tcb *tcp, const bool check_errno)`. It reads `tile_regs.regs[0]`, calls `is_negated_errno`, writes `tcp->u_rval = -1` and positive `u_error` for negative errno, otherwise stores the raw return in `u_rval`.

## Control Flow and Integration
Generic `get_error` calls this function after syscall exit. Although the Tile calling convention has `r0` as value or negative errno and `r1` as zero or positive errno, the code intentionally relies on `r0` because older kernels did not expose the updated `r1` in ptregs at this point.

## State and Persistence
Mutates only the current tracee control block fields `u_rval` and `u_error`. It reads the transient `tile_regs` cache.

## Dependencies
Depends on `tile_regs` from `arch_regs.c`, `is_negated_errno`, `struct tcb`, and the generic syscall-exit path.

## Risks
The historical `r1` workaround is correct for old kernels but means decoding is entirely dependent on negative-errno encoding in `r0`. If Tile kernel behavior diverges, errno reporting could be wrong.

## Test Signals
Trace Tile syscalls that succeed, return large positive values, and fail with common errors such as `ENOENT`. Fault-injection tests should verify printed errno uses `u_error` and success values preserve `u_rval`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/get_scno.c -->
# sources/test-tools/strace/src/linux/tile/get_scno.c

## Purpose
Extracts Tile syscall number and selects the current strace personality.

## Important APIs, Types, and Functions
Defines `arch_get_scno(struct tcb *tcp)`. It computes `currpers`, calls `update_personality(tcp, currpers)`, assigns `tcp->scno = tile_regs.regs[10]`, and returns `1`.

## Control Flow and Integration
On `__tilepro__`, the function always selects personality 1. Otherwise it checks `tile_regs.flags & PT_FLAGS_COMPAT`, defining `PT_FLAGS_COMPAT 0x10000` locally if old headers lack it, and selects personality 1 for compat or 0 for native. Generic `get_scno` then uses `tcp->scno` to index the active syscall table.

## State and Persistence
Mutates per-tracee fields through `update_personality` and `tcp->scno`. Reads the transient `tile_regs` cache.

## Dependencies
Depends on register layout from `arch_regs.c`, Tile kernel `PT_FLAGS_COMPAT`, and the personality order in `arch_defs_.h`.

## Risks
Wrong compatibility flag handling selects the wrong syscall table and word-size assumptions. Because the function always returns success, bad register contents are not signaled locally.

## Test Signals
Run native TileGx and compat TileGx32/TILEPro traces and verify syscall numbers resolve against the expected `syscallent.h` or `syscallent1.h` table. Tests should include headers with and without `PT_FLAGS_COMPAT`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/tile/get_syscall_args.c

## Purpose
Copies Tile syscall arguments from registers into strace's normalized argument array.

## Important APIs, Types, and Functions
Defines `arch_get_syscall_args(struct tcb *tcp)`. It maps `tile_regs.regs[0]` through `regs[5]` to `tcp->u_arg[0]` through `u_arg[5]` and returns `1`.

## Control Flow and Integration
Generic `get_syscall_args` calls this after syscall number resolution. There is no conditional logic; Tile uses six argument registers starting at `r0`.

## State and Persistence
Mutates only `tcp->u_arg[]` for the current syscall. Reads the transient register cache.

## Dependencies
Depends on Tile register layout, `struct tcb`, and generic syscall argument decoding.

## Risks
If Tile ABI argument order changes or register cache is stale, every syscall decoder receives wrong arguments. No local error path validates register availability.

## Test Signals
Trace syscalls with six distinct arguments, such as `mmap`, `clone`, or `pselect6`, and verify each printed argument matches the tracee call.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/tile/ioctls_arch0.h

## Purpose
Placeholder/generated architecture-specific ioctl table for Tile personality 0.

## Important APIs, Types, and Functions
Contains only the generator provenance comment from `ioctls_gen.sh`; it contributes no ioctl rows.

## Control Flow and Integration
Included by the ioctl xlat machinery for personality 0. Because it is empty apart from a comment, decoding falls through to generic include tables such as `ioctls_inc0.h`.

## State and Persistence
No state or generated metadata rows are present.

## Dependencies
Depends conceptually on the generated-ioctl include contract. Its lack of rows means architecture-specific Tile kernel headers did not contribute supported ioctls at generation time.

## Risks
New Tile-specific ioctl constants would be missed until this generated file is refreshed. Empty generated files should remain syntactically valid when included in table initializers.

## Test Signals
Ioctl table generation should preserve a valid empty file. Tile ioctl decoding should still resolve generic ioctl entries through the included common tables.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/tile/ioctls_arch1.h

## Purpose
Placeholder/generated architecture-specific ioctl table for Tile personality 1.

## Important APIs, Types, and Functions
Contains only the `ioctls_gen.sh` provenance comment and no ioctl initializer rows.

## Control Flow and Integration
Included for the secondary Tile personality ioctl table. Actual decoding relies on generic/compat ioctl include files rather than local architecture-specific rows.

## State and Persistence
No runtime or table state is introduced.

## Dependencies
Depends on ioctl table generation and the personality-specific include layout.

## Risks
Compat-specific Tile ioctl constants are absent unless the generator later adds rows. Since this file is intentionally empty, regressions are more likely in include ordering than in logic.

## Test Signals
Build the secondary Tile personality ioctl table and confirm generic 32-bit ioctl entries are still available through `ioctls_inc1.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_arch1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/tile/ioctls_inc0.h

## Purpose
Routes Tile personality 0 ioctl decoding to the generic 64-bit ioctl include table.

## Important APIs, Types, and Functions
The file contains `#include "../64/ioctls_inc.h"` and exports no local symbols.

## Control Flow and Integration
Compile-time inclusion populates personality 0's ioctl table with 64-bit generic ioctl definitions after any architecture-specific rows.

## State and Persistence
No local mutable state; the include contributes static ioctl metadata to the compiled decoder.

## Dependencies
Depends on `../64/ioctls_inc.h` and the ioctl table assembly context.

## Risks
Using the wrong generic include would produce incorrect ioctl sizes for pointer-width-sensitive commands. This file must stay aligned with Tile native word size.

## Test Signals
Trace common ioctls on native Tile and verify decoded request names and structure sizes match 64-bit ABI expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/tile/ioctls_inc1.h

## Purpose
Routes Tile personality 1 ioctl decoding to the generic 32-bit ioctl include table.

## Important APIs, Types, and Functions
The file contains `#include "../32/ioctls_inc.h"` and defines no local rows or functions.

## Control Flow and Integration
Compile-time inclusion fills the secondary Tile ioctl table with compat 32-bit ioctl metadata.

## State and Persistence
No local state. The compiled table metadata is static.

## Dependencies
Depends on `../32/ioctls_inc.h`, whose internal alignment choices depend on architecture macros and structure sizes.

## Risks
Compat ioctl sizes are pointer-width and alignment sensitive. Wrong routing would break decoding for TileGx32 or TILEPro processes.

## Test Signals
Run compat Tile ioctl traces and verify size-sensitive ioctls decode with 32-bit layouts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/ioctls_inc1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/raw_syscall.h -->
# sources/test-tools/strace/src/linux/tile/raw_syscall.h

## Purpose
Implements a Tile inline raw syscall helper for strace's own internal zero-argument syscalls.

## Important APIs, Types, and Functions
Defines guarded `raw_syscall_0(kernel_ulong_t nr, kernel_ulong_t *err)`. Inline assembly executes `swint1`, passes the syscall number in register `r10`, captures `r0` as return value and `r1` as error channel, marks clobbered registers, stores `*err = e`, and returns `r`.

## Control Flow and Integration
Used when architecture-specific raw syscall support is needed by strace internals. The function has no branches; the kernel trap transfers control and returns register results.

## State and Persistence
No persistent state. It writes through the caller-provided `err` pointer and clobbers CPU registers according to the assembly constraint list.

## Dependencies
Depends on Tile compiler register constraints such as `R00`, `R01`, and `R10`, `kernel_types.h`, and the Tile syscall ABI.

## Risks
Inline assembly is fragile: wrong clobbers can corrupt caller state, wrong constraints can fail compilation, and wrong syscall trap instruction breaks all internal raw syscalls. The helper reports the Tile convention's `r1` error channel, unlike `get_error.c` which reads tracee `r0` for historical ptrace reasons.

## Test Signals
Native Tile builds must compile the constraints. Runtime smoke tests should cover strace internal raw syscalls and compare returned value/error behavior against libc or kernel expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/tile/rt_sigframe.h

## Purpose
Defines the Tile real-time signal frame shape used by generic `rt_sigreturn` decoding.

## Important APIs, Types, and Functions
Declares `struct_rt_sigframe` with `save_area[C_ABI_SAVE_AREA_SIZE]`, `siginfo_t info`, and `ucontext_t uc`. It includes `<signal.h>` and uses an include guard.

## Control Flow and Integration
No functions are present. `rt_sigreturn.c` includes this type through `DEF_MPERS_TYPE(struct_rt_sigframe)` and computes offsets such as `uc.uc_sigmask` for decoding saved signal masks.

## State and Persistence
No state. The type definition is compile-time metadata describing tracee memory layout.

## Dependencies
Depends on `C_ABI_SAVE_AREA_SIZE`, libc/kernel definitions of `siginfo_t` and `ucontext_t`, and the generic rt-sigframe decoding path.

## Risks
Any mismatch with the kernel's Tile sigframe layout makes strace read the wrong fields during signal-return decoding. Header definitions from the build environment must match the target ABI.

## Test Signals
Tile `rt_sigreturn` tests should validate signal-mask decoding. Static layout checks around `offsetof(struct_rt_sigframe, uc.uc_sigmask)` are useful if available.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/set_error.c -->
# sources/test-tools/strace/src/linux/tile/set_error.c

## Purpose
Implements Tile register mutation for syscall fault injection and return-value tampering.

## Important APIs, Types, and Functions
Defines `arch_set_error(struct tcb *tcp)` and `arch_set_success(struct tcb *tcp)`. The error path writes `tile_regs.regs[0] = -tcp->u_error`; the success path writes `tile_regs.regs[0] = tcp->u_rval`; both call `set_regs(tcp->pid)`.

## Control Flow and Integration
Generic `set_error` calls these hooks when strace injects or changes syscall results. The functions update the cached return register and write the entire register set back to the tracee.

## State and Persistence
Mutates the transient `tile_regs` cache and persists the modification into the stopped tracee through ptrace `set_regs`.

## Dependencies
Depends on `tile_regs`, `set_regs`, and Tile syscall return-value convention.

## Risks
Because only `r0` is set, any consumers expecting `r1` to carry a positive errno may not see a fully canonical Tile return state. Whole-register writes also rely on `tile_regs` being fresh.

## Test Signals
Fault-injection tests should confirm Tile syscalls can be forced to fail with specific errno values and forced to return chosen success values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/set_scno.c -->
# sources/test-tools/strace/src/linux/tile/set_scno.c

## Purpose
Changes a Tile tracee's syscall number for syscall injection or tampering.

## Important APIs, Types, and Functions
Defines `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)`. It refreshes registers with `get_regs(tcp)` when syscall-info data is valid, writes `tile_regs.regs[10] = scno`, and calls `set_regs(tcp->pid)`.

## Control Flow and Integration
Generic `set_scno` invokes this hook. The conditional register refresh prevents overwriting newer register data when `PTRACE_GET_SYSCALL_INFO` supplied syscall metadata without refreshing the architecture register cache.

## State and Persistence
Mutates `tile_regs` and writes the changed register set to the tracee. No durable state exists beyond the tracee's stopped register state.

## Dependencies
Depends on Tile syscall number register `r10`, `ptrace_syscall_info_is_valid`, `get_regs`, and `set_regs`.

## Risks
If register refresh fails, the function returns `-1` and the syscall number is not changed. If the cache is stale and the refresh is skipped, unrelated registers could be written back incorrectly.

## Test Signals
Syscall tampering/injection tests should change Tile syscall numbers and verify the kernel executes or reports the replacement syscall.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/syscallent.h -->
# sources/test-tools/strace/src/linux/tile/syscallent.h

## Purpose
Defines Tile native personality syscall table entries by including the generic 64-bit syscall table and appending Tile architecture-specific calls.

## Important APIs, Types, and Functions
Includes `../64/syscallent.h`, then adds entries `[244] cmpxchg_badaddr` and `[245] cacheflush` using `SEN(printargs)`. These rows are initializer data for `struct_sysent`.

## Control Flow and Integration
No runtime control flow. The include produces the base 64-bit table, and the local rows override/fill the architecture-specific range `[244 ... 259]`.

## State and Persistence
No local mutable state. The compiled static table drives syscall decoding for Tile personality 0.

## Dependencies
Depends on generic 64-bit syscall table numbering, `SEN` and flag macros, and Tile personality selection in `get_scno.c`.

## Risks
The arch-specific slots use `printargs`, so decoding is intentionally generic. Incorrect placement would collide with generic syscall numbers or leave Tile-specific calls unknown.

## Test Signals
Native Tile traces for syscall numbers 244 and 245 should print `cmpxchg_badaddr` and `cacheflush`. Generic 64-bit syscalls should still decode through the included table.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/syscallent1.h -->
# sources/test-tools/strace/src/linux/tile/syscallent1.h

## Purpose
Defines Tile secondary personality syscall entries for 32-bit/compat tracing.

## Important APIs, Types, and Functions
Defines `sys_ARCH_mmap sys_mmap_4koff` and `ARCH_WANT_SYNC_FILE_RANGE2 1` before including `../32/syscallent.h`. It appends the same Tile-specific `[244] cmpxchg_badaddr` and `[245] cacheflush` `printargs` entries.

## Control Flow and Integration
All behavior is compile-time table construction. The pre-include macros tune the generic 32-bit table for Tile ABI differences, then local rows fill the architecture-specific range.

## State and Persistence
No mutable state. Produces static metadata for personality 1.

## Dependencies
Depends on generic 32-bit syscall table macro hooks and Tile personality selection.

## Risks
Forgetting the macro overrides would decode Tile compat `mmap` or `sync_file_range2` incorrectly. The local arch-specific rows must remain aligned with the native table's Tile-specific range.

## Test Signals
Compat Tile traces should verify `mmap`, `sync_file_range2`, syscall 244, and syscall 245 decoding. Compile tests should ensure macro redefinitions do not leak beyond intended include context.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/syscallent1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/userent.h -->
# sources/test-tools/strace/src/linux/tile/userent.h

## Purpose
Defines Tile ptrace user-register offset names for `PTRACE_PEEKUSER` and related decoding.

## Important APIs, Types, and Functions
Provides table rows mapping `PTREGS_OFFSET_REG(0)` through `PTREGS_OFFSET_REG(52)` to `r0` through `r52`, plus named offsets for `tp`, `sp`, `lr`, `pc`, `ex1`, `faultnum`, `orig_r0`, and `flags`.

## Control Flow and Integration
No runtime control flow. Included by `ptrace.c` table machinery so numeric user-area offsets can be printed as Tile register names.

## State and Persistence
No state. The compiled offset table is static metadata.

## Dependencies
Depends on Tile `PTREGS_OFFSET_*` macros from kernel headers or generated architecture definitions and on the including xlat/table context.

## Risks
Register offset macros must match the kernel `pt_regs` layout. Incorrect mappings affect ptrace offset display and can mislead users debugging register access.

## Test Signals
Ptrace decoder tests should verify representative offsets for argument registers, stack pointer, program counter, original return register, and flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/tile/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_defs_.h -->
# sources/test-tools/strace/src/linux/x32/arch_defs_.h

## Purpose
Defines x32 build personality and ABI feature metadata. This strace target supports x32 as personality 0 and i386 as personality 1, not the full x86_64 three-personality arrangement.

## Important APIs, Types, and Functions
Sets `ARCH_NEEDS_NON_SHUFFLED_SCNO_CHECK 1`, structure and legacy syscall feature macros, `SUPPORTED_PERSONALITIES 2`, designators `{ "x32", "32" }`, names `{ "x32", "32 bit" }`, `PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_X86_64, __X32_SYSCALL_BIT }`, and `PERSONALITY1_AUDIT_ARCH { AUDIT_ARCH_I386, 0 }`.

## Control Flow and Integration
Compile-time definitions feed syscall table creation, filtering, seccomp audit-arch handling, and syscall-number shuffle/check logic. The non-shuffled syscall check is important because x32 syscall numbers carry `__X32_SYSCALL_BIT`.

## State and Persistence
No runtime state. Defines static build personality behavior.

## Dependencies
Depends on audit arch constants, `__X32_SYSCALL_BIT`, and generic defaults in `arch_defs.h`.

## Risks
Feature macros affect old stat, mmap, select, uid16, and time64 syscall availability. Incorrect personality audit masks can break seccomp filtering or classify x86_64 syscalls as x32.

## Test Signals
Build x32 strace and verify `-e trace=...@x32` and `@32` filters, seccomp filter generation, and syscall name lookup for x32-bit-marked syscall numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/x32/arch_fpregset.c

## Purpose
Reuses the x86_64 floating-point register-set decoder for the x32 target.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_fpregset.c`, which defines `arch_decode_fpregset` for non-`MPERS_IS_m32` builds and delegates to i386 for m32 builds.

## Control Flow and Integration
The inherited decoder validates size alignment, fetches up to `sizeof(struct_fpregset)` from tracee memory with `umoven_or_printaddr`, prints x87/SSE control fields and arrays progressively by fetched size, and indicates extra data when the kernel-provided size is larger than known layout.

## State and Persistence
No persistent state. It reads tracee memory and writes formatted output.

## Dependencies
Depends on x86_64 `arch_fpregset.h`, `struct_fpregset`, generic regset decoding, and i386 mpers support when compiled for m32.

## Risks
The x32 ABI shares x86_64 kernel register layouts even though user long size is 32-bit. The include indirection is correct only if x32 regset layout remains x86_64-compatible.

## Test Signals
Regset tests for `NT_FPREGSET` on x32 should decode control words, `st_space`, `xmm_space`, padding, malformed sizes, and oversized buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/x32/arch_fpregset.h

## Purpose
Reuses the x86_64 floating-point register-set type definition for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_fpregset.h`, which defines `struct_fpregset` with x87 control fields, 64-bit instruction/data pointers, MXCSR fields, `st_space`, `xmm_space`, and padding, and defines `HAVE_ARCH_FPREGSET`.

## Control Flow and Integration
No runtime flow. This header provides the type consumed by `regset.c` and `arch_fpregset.c`.

## State and Persistence
No state; static type metadata only.

## Dependencies
Depends on x86_64 register-set layout and fixed-width integer types.

## Risks
If x32-specific kernel headers ever diverge from x86_64 fpregset layout, the reused type would decode fields incorrectly. Include guards live in the included header.

## Test Signals
Build x32 regset decoding and compare decoded fpregset field offsets against kernel `elf_fpregset_t`/ptrace output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/x32/arch_get_personality.c

## Purpose
Reuses x86_64 syscall-info personality detection for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_get_personality.c`, which implements `get_personality_from_syscall_info`. In an x32 build with `X32` defined, the included code returns `1` for `AUDIT_ARCH_I386` and `0` otherwise, because the x86_64-only x32-bit discrimination block is disabled.

## Control Flow and Integration
Called by generic personality selection when `PTRACE_GET_SYSCALL_INFO` is available. For x32, audit arch `AUDIT_ARCH_X86_64` corresponds to personality 0 and `AUDIT_ARCH_I386` to personality 1.

## State and Persistence
No local state. The generic layer records the selected personality on the tracee control block.

## Dependencies
Depends on x86_64 implementation, `AUDIT_ARCH_I386`, and x32 build defines matching `arch_defs_.h` personality order.

## Risks
If the x32 build environment does not define `X32` as expected, the inherited x86_64 code could return personality 2 for x32-bit-marked syscalls, which is out of range for this two-personality target.

## Test Signals
Trace x32 and i386 processes with syscall-info enabled and verify personality indexes remain 0 and 1 only.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_get_personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_kvm.c -->
# sources/test-tools/strace/src/linux/x32/arch_kvm.c

## Purpose
Reuses x86_64 KVM register and segment decoding for the x32 target.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_kvm.c`, which conditionally defines `arch_print_kvm_regs`, segment/dtable helpers, and `arch_print_kvm_sregs` when the relevant KVM structs are available.

## Control Flow and Integration
The inherited code prints KVM general registers, special registers, segment descriptors, descriptor tables, control registers, EFER, APIC base, and interrupt bitmap. It respects `abbrev(tcp)` by shortening output.

## State and Persistence
No persistence. It reads already-fetched KVM ioctl structures and writes decoded output.

## Dependencies
Depends on Linux KVM structure definitions and generic ioctl/KVM decoding. x32 uses x86 KVM ABI layouts, so the x86_64 implementation is shared.

## Risks
KVM ioctl structure sizes differ between 32-bit and 64-bit contexts for some commands. This include is appropriate for x32's x86_64 kernel-facing KVM structs but must be checked when KVM headers change.

## Test Signals
KVM ioctl tests on x32 should verify `KVM_GET_REGS`, `KVM_SET_REGS`, `KVM_GET_SREGS`, and abbreviated output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.c

## Purpose
Reuses x86_64 PRSTATUS register-set decoding for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_prstatus_regset.c`, which defines `arch_decode_prstatus_regset` for non-m32 builds and delegates to i386 when `MPERS_IS_m32`.

## Control Flow and Integration
The inherited decoder rejects zero or unaligned sizes by printing the address, otherwise fetches a bounded prefix of `struct_prstatus_regset` and prints registers in kernel order, including general registers, `orig_rax`, `rip`, segment selectors, flags, stack pointer, and bases.

## State and Persistence
No state. It reads tracee memory for regset data and emits formatted output.

## Dependencies
Depends on x86_64 PRSTATUS type definition and generic regset code. For m32 mpers builds it depends on the i386 implementation.

## Risks
Partial-size logic prints only fields covered by the fetched size. Any layout mismatch between x32 and x86_64 PRSTATUS would skew all following fields.

## Test Signals
Regset decoding tests should cover full, partial, unaligned, and oversized `NT_PRSTATUS` buffers for x32.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.h

## Purpose
Reuses x86_64 PRSTATUS register-set structure definitions for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_prstatus_regset.h`, which defines `struct_prstatus_regset` with x86_64 register order and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Control Flow and Integration
No runtime flow. The header supplies the type for `regset.c` and the architecture decoder.

## State and Persistence
No state.

## Dependencies
Depends on `kernel_ulong_t` sizing and x86_64 register order. The included header delegates to i386 definitions for m32 builds.

## Risks
x32's userspace ABI is ILP32, but ptrace PRSTATUS register layout follows x86_64 register naming/order. Any assumption that `kernel_ulong_t` should be user-long-sized rather than kernel-register-sized is a risk area.

## Test Signals
Compile x32 regset support and compare decoded PRSTATUS offsets against kernel core-note or ptrace regset data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_regs.c -->
# sources/test-tools/strace/src/linux/x32/arch_regs.c

## Purpose
Reuses x86_64 register-cache setup for x32 syscall tracing.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_regs.c`, which defines a union of `struct user_regs_struct` and an i386 register struct, an `iovec` for `PTRACE_GETREGSET`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_IOVEC_FOR_GETREGSET`, and PC/SP macros that switch on returned iovec length.

## Control Flow and Integration
Generic register helpers fetch registers into the shared union. PC and SP references evaluate to i386 or x86_64 fields depending on the fetched size. The included code disables `ARCH_MIGHT_USE_SET_REGS`.

## State and Persistence
Uses static `x86_regs_union` and `x86_io` caches inside the strace process. They are transient and refreshed per tracee stop.

## Dependencies
Depends on x86_64 ptrace register structures, generic `GETREGSET` support, and x32 syscall helpers that read x86_64 register names.

## Risks
The shared union must be large enough for both layouts, and `iov_len` must accurately reflect current personality. Stale or mismatched `iov_len` causes wrong PC/SP selection.

## Test Signals
Trace x32 and i386 processes and verify PC/SP reporting, syscall arguments, and return values across personality switches.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_regs.h -->
# sources/test-tools/strace/src/linux/x32/arch_regs.h

## Purpose
Reuses x86_64 register index constants for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_regs.h`, which defines indices such as `R15`, `RAX`, `ORIG_RAX`, `RIP`, `RSP`, `FS_BASE`, and `GS` for register-array based ptrace access.

## Control Flow and Integration
No runtime flow. Included by `regs.h` and syscall/register helpers that need portable symbolic offsets.

## State and Persistence
No state.

## Dependencies
Depends on x86_64 kernel ptrace register ordering.

## Risks
Wrong register indices would affect raw register access and syscall mutation. The x32 target depends on x86_64 register order despite ILP32 userspace.

## Test Signals
Register access tests should verify `ORIG_RAX`, `RAX`, `RIP`, and `RSP` indices under x32.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/x32/arch_rt_sigframe.c

## Purpose
Reuses x86_64 real-time signal-frame address calculation for x32, which itself includes the i386 implementation.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_rt_sigframe.c`; that file includes `../i386/arch_rt_sigframe.c`, providing `get_rt_sigframe_addr` logic.

## Control Flow and Integration
Used by generic `rt_sigreturn.c` to locate the signal frame on the tracee stack before reading `struct_rt_sigframe` fields. The actual control flow is inherited from i386-compatible code.

## State and Persistence
No persistent state; reads current tracee stack/register state.

## Dependencies
Depends on x86/i386 signal-frame conventions and generic rt-sigreturn decoder.

## Risks
x32 signal-frame layout is a compatibility edge case. Reusing i386 logic through x86_64 must match kernel behavior for x32 rt signal frames.

## Test Signals
x32 signal-return tests should verify `rt_sigreturn` prints restored signal masks and handles bad frame addresses cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/x32/arch_sigreturn.c

## Purpose
Reuses x86_64 old-sigreturn handling for x32. The included x86_64 file states that only the x86 personality has the old `sigreturn` syscall and includes the i386 implementation.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_sigreturn.c`, which in turn includes `../i386/arch_sigreturn.c` to provide `arch_sigreturn`.

## Control Flow and Integration
Generic `sigreturn.c` calls `arch_sigreturn` when decoding old signal return. In x32 builds, this path is relevant to the 32-bit personality rather than native x32 syscalls.

## State and Persistence
No persistent state. It reads tracee stack memory and emits decoded signal mask data through inherited logic.

## Dependencies
Depends on i386 signal frame layout and personality routing so old `sigreturn` is not applied to unsupported x32/native paths.

## Risks
Incorrect personality routing could try to decode an old i386 sigframe for a native x32 context. The include chain hides the actual implementation, so regressions in i386 signal code affect x32.

## Test Signals
Exercise old `sigreturn` from an i386 personality under x32 strace and confirm native x32 does not misreport unsupported old signal return behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/asm_stat.h -->
# sources/test-tools/strace/src/linux/x32/asm_stat.h

## Purpose
Reuses the x86_64 `asm_stat.h` replacement logic for x32 stat structure decoding.

## Important APIs, Types, and Functions
Includes `../x86_64/asm_stat.h`. In x86_64 ILP32 builds, that header temporarily redirects `stat`, includes generic stat definitions, then defines a replacement `struct stat` because older x32 kernel headers were wrong.

## Control Flow and Integration
No runtime flow in this wrapper. The included type definitions are used by `fetch_struct_stat.c`, `fetch_struct_stat64.c`, and old stat decoders.

## State and Persistence
No state; ABI type definitions only.

## Dependencies
Depends on x86_64 stat compatibility logic, `kernel_ulong_t`, and generic asm stat definitions.

## Risks
Stat layouts are ABI-critical. Wrong padding, field width, or header redirection will misdecode `stat`, `lstat`, `fstat`, and related structures for x32.

## Test Signals
x32 stat-family tests should compare decoded fields for device, inode, mode, uid/gid, size, blocks, and timestamps against known fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/asm_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/check_scno.c -->
# sources/test-tools/strace/src/linux/x32/check_scno.c

## Purpose
Rejects unsupported 64-bit syscall mode when running an x32 strace target.

## Important APIs, Types, and Functions
Defines `arch_check_scno(struct tcb *tcp)`. It reads `ptrace_sci.entry.nr`, and if current personality is x32 (`currpers == 0`) but the syscall number lacks `__X32_SYSCALL_BIT`, it prints an error and returns `0` to ignore the syscall.

## Control Flow and Integration
Generic `get_scno` calls this when syscall-info data is valid and `ARCH_NEEDS_NON_SHUFFLED_SCNO_CHECK` is set. Valid x32 or i386 syscalls return `1`; unsupported 64-bit syscalls return ignore.

## State and Persistence
No persistent state. It reads `tcp->currpers`, syscall-info global data, and emits an error message.

## Dependencies
Depends on `ptrace_sci`, `__X32_SYSCALL_BIT`, `PRI_klu`, and personality numbering from `arch_defs_.h`.

## Risks
This is a protective gate: without it, an x32-only build could try to decode regular x86_64 syscalls with the x32 table. False positives would hide valid syscalls; false negatives would produce wrong decoding.

## Test Signals
Tests should simulate or trace a syscall-info entry with `AUDIT_ARCH_X86_64` and no x32 bit in personality 0 and assert the unsupported-mode error and ignored return. Valid x32-bit-marked syscalls should pass.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/check_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/get_error.c -->
# sources/test-tools/strace/src/linux/x32/get_error.c

## Purpose
Reuses x86_64 syscall return and errno decoding for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/get_error.c`, which reads the x86 register cache, detects negated errno according to syscall-table flags, and populates `tcp->u_rval`/`tcp->u_error`.

## Control Flow and Integration
Generic syscall-exit handling calls the inherited `arch_get_error`. x32 returns values in the x86_64 `rax` register, so sharing x86_64 logic is expected.

## State and Persistence
Mutates only per-tracee syscall result fields. Reads transient x86 register cache state.

## Dependencies
Depends on included x86_64 register definitions and generic error handling.

## Risks
Return-value width is subtle for x32 because user longs are 32-bit while registers are 64-bit. The inherited code must preserve strace's kernel-long handling for x32.

## Test Signals
Trace x32 syscalls with success, negative errno, and large unsigned returns. Fault injection should verify printed errno and return values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/get_scno.c -->
# sources/test-tools/strace/src/linux/x32/get_scno.c

## Purpose
Reuses x86_64 syscall-number extraction for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/get_scno.c`, which reads `orig_rax`/syscall-info data, uses `__X32_SYSCALL_BIT` to distinguish x32 where applicable, updates personality, and assigns `tcp->scno`.

## Control Flow and Integration
The inherited logic runs inside generic `get_scno`. For x32 builds it must coordinate with `check_scno.c` and syscall-number shuffling so table indexes use the untagged number while validation sees the original x32 bit.

## State and Persistence
Mutates `tcp->scno` and current personality. Reads transient register/syscall-info state.

## Dependencies
Depends on x86_64 register cache, `__X32_SYSCALL_BIT`, and x32 two-personality definitions.

## Risks
The main risk is mishandling the x32 syscall bit, either stripping it too early for validation or leaving it in when indexing the syscall table. That would cause unsupported-mode errors or out-of-range table lookups.

## Test Signals
Trace x32 syscalls and confirm displayed syscall numbers/names match untagged x32 table entries. Also test i386 personality switching.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/x32/get_syscall_args.c

## Purpose
Reuses x86_64 syscall argument extraction for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/get_syscall_args.c`, which copies arguments from x86 syscall argument registers into `tcp->u_arg[]`, with i386 handling for compat personalities.

## Control Flow and Integration
Called by generic `get_syscall_args` after syscall number/personality resolution. x32 native syscalls use x86_64 register calling convention with ILP32 argument interpretation.

## State and Persistence
Mutates `tcp->u_arg[]` for the current syscall only.

## Dependencies
Depends on x86_64 register cache, personality-aware argument extraction, and x32 word-size handling in downstream decoders.

## Risks
Argument register order must be x86_64 order for x32 native and i386 order for personality 1. Width-sensitive decoders must interpret `u_arg` using the current personality, not host C long size.

## Test Signals
Trace x32 syscalls with six arguments, pointer arguments, and 64-bit offset pairs. Compare against i386 personality traces to verify switching.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/x32/ioctls_arch0.h

## Purpose
Routes x32 personality 0 architecture-specific ioctl decoding to the x86_64 generated ioctl table.

## Important APIs, Types, and Functions
Includes `../x86_64/ioctls_arch0.h`, which contains x86 architecture ioctl rows such as machine-check, MSR, MTRR, SGX, and KVM request metadata with 64-bit-oriented sizes.

## Control Flow and Integration
Compile-time inclusion contributes x86_64 arch-specific ioctl rows before generic include rows in the ioctl decoder.

## State and Persistence
No local state. The included rows become static ioctl metadata.

## Dependencies
Depends on x86_64 generated ioctl table and x32 ioctl ABI compatibility for native x32 processes.

## Risks
x32 ioctl sizes can differ from both pure 32-bit and 64-bit ABIs. Reusing x86_64 rows is correct only for commands whose kernel-facing structure sizes match x32 expectations.

## Test Signals
x32 ioctl tests should cover x86-specific commands, especially KVM and MSR/MTRR requests with encoded sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/x32/ioctls_arch1.h

## Purpose
Routes x32 personality 1 architecture-specific ioctl decoding to the i386 generated ioctl table.

## Important APIs, Types, and Functions
Includes `../i386/ioctls_arch0.h`, which supplies x86 arch-specific ioctl rows with 32-bit encoded sizes for the i386 personality.

## Control Flow and Integration
Compile-time inclusion populates the secondary ioctl table used when tracing 32-bit i386 processes from an x32 build.

## State and Persistence
No local state; contributes static metadata through the include.

## Dependencies
Depends on the i386 generated ioctl table and correct personality selection.

## Risks
Using this table for native x32 would decode size-sensitive ioctls incorrectly; it must remain tied to personality 1 only.

## Test Signals
Trace i386-personality ioctl calls under x32 strace and verify request names and encoded sizes match i386, especially KVM and x86 arch-specific commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/ioctls_arch1.h -->

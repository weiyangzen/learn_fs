# subset-b-009335 Research

Grouped research for strace Linux architecture backend files covering IA-64, LoongArch64, m68k, Meta, MicroBlaze, MIPS, Nios II, OpenRISC, and PowerPC syscall tables, register hooks, raw syscall helpers, ioctl/user tables, and signal/regset decoders. Each source file section preserves the exact source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/syscallent.h -->
# sources/test-tools/strace/src/linux/ia64/syscallent.h

## Purpose
Defines the `ia64` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 334 decoder entries; first entries include printargs, exit, read, write, open, close; final entries include perf_event_open, seccomp, pkey_mprotect, pkey_alloc, pkey_free, rseq.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `ia64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `ia64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/ia64/syscallent.h`: 359 lines; 21422 bytes; includes `#include "syscallent-common.h"`; defines `# define BASE_NR 0`, `# define BASE_NR 1024`, `#undef BASE_NR`; 334 `SEN(...)` syscall decoder references; first printargs, exit, read, write; last pkey_mprotect, pkey_alloc, pkey_free, rseq. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h -->
# sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h

## Purpose
Defines the architecture syscall table base offset used by the IA-64 backend.

## Important APIs, Types, and Functions
- `SYSCALLENT_BASE_NR` is set to `(1U << 10)`, matching IA-64's shifted syscall numbering convention used by `shuffle_scno.c` and `arch_defs_.h`.

## Control Flow
- No executable control flow; the macro is consumed at compile time when normalizing IA-64 syscall numbers and audit personality metadata.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `ia64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- A wrong base value would desynchronize syscall table lookup from kernel syscall numbers, causing broad mis-decoding rather than isolated failures.

## Test Signals
- Build strace for `ia64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h`: 1 lines; 38 bytes; defines `#define SYSCALLENT_BASE_NR (1U << 10)`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/userent.h -->
# sources/test-tools/strace/src/linux/ia64/userent.h

## Purpose
Provides the ptrace user-area offset to register-name table for strace's `ia64` register printers.

## Important APIs, Types, and Functions
- The file contributes initializer rows of `{ offset, name }` pairs and may include `userent0.h` for common trailing entries.
- Rows cover architecture-visible register offsets; source facts show 65 explicit offset/name entries.

## Control Flow
- There is no runtime branch logic; generic user-area decoding iterates the compiled table when printing PTRACE_PEEKUSER-style offsets.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `ia64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Offsets must match kernel UAPI headers for the exact architecture ABI; stale offsets produce plausible-looking but wrong register names.

## Test Signals
- Build strace for `ia64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/ia64/userent.h`: 80 lines; 3861 bytes; includes `#include "userent0.h"`; 65 ptrace user offset/name rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/loongarch64/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `loongarch64` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_LOONGARCH64.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `loongarch64` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/arch_defs_.h`: 8 lines; 193 bytes; defines `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_LOONGARCH64, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.c

## Purpose
Decodes and prints a `loongarch64` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.c`: 36 lines; 904 bytes; functions `arch_decode_fpregset`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.h

## Purpose
Declares the `loongarch64` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.h`: 15 lines; 310 bytes; defines `# define STRACE_ARCH_FPREGSET_H`, `# define HAVE_ARCH_FPREGSET 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.c

## Purpose
Decodes and prints a `loongarch64` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.c`: 49 lines; 1375 bytes; functions `arch_decode_prstatus_regset`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.h

## Purpose
Declares the `loongarch64` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.h`: 15 lines; 344 bytes; defines `# define STRACE_ARCH_PRSTATUS_REGSET_H`, `# define HAVE_ARCH_PRSTATUS_REGSET 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_regs.c -->
# sources/test-tools/strace/src/linux/loongarch64/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `loongarch64` backend.

## Important APIs, Types, and Functions
- user_pt_regs loongarch_regs; syscall number regs[11]/a7, return regs[4]/a0, orig_a0 as argument 0, stack regs[3], PC csr_era
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/arch_regs.c`: 11 lines; 307 bytes; defines `#define ARCH_REGS_FOR_GETREGSET loongarch_regs`, `#define ARCH_PC_REG loongarch_regs.csr_era`, `#define ARCH_SP_REG loongarch_regs.regs[3]`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/get_error.c -->
# sources/test-tools/strace/src/linux/loongarch64/get_error.c

## Purpose
Maps the `loongarch64` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- user_pt_regs loongarch_regs; syscall number regs[11]/a7, return regs[4]/a0, orig_a0 as argument 0, stack regs[3], PC csr_era
- The helper decodes the architecture's result register and uses `is_negated_errno` when this ABI reports failures as negative return values.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `loongarch64` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/get_error.c`: 19 lines; 410 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/get_scno.c -->
# sources/test-tools/strace/src/linux/loongarch64/get_scno.c

## Purpose
Extracts the current `loongarch64` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- user_pt_regs loongarch_regs; syscall number regs[11]/a7, return regs[4]/a0, orig_a0 as argument 0, stack regs[3], PC csr_era
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `loongarch64` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/get_scno.c`: 14 lines; 281 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/loongarch64/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `loongarch64` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- orig_a0 plus regs[5] through regs[9] populate tcp->u_arg[0..5]
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `loongarch64`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/get_syscall_args.c`: 19 lines; 495 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/loongarch64/ioctls_arch0.h

## Purpose
Adds `loongarch64`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 0 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `loongarch64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `loongarch64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/ioctls_arch0.h`: 1 lines; 96 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `loongarch64` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `loongarch64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `loongarch64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../64/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/loongarch64/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `loongarch64`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- syscall 0 with a7 carrying the number and a0 carrying the result
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `loongarch64` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/raw_syscall.h`: 29 lines; 611 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/set_error.c -->
# sources/test-tools/strace/src/linux/loongarch64/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `loongarch64` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- user_pt_regs loongarch_regs; syscall number regs[11]/a7, return regs[4]/a0, orig_a0 as argument 0, stack regs[3], PC csr_era

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/set_error.c`: 20 lines; 364 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/set_scno.c -->
# sources/test-tools/strace/src/linux/loongarch64/set_scno.c

## Purpose
Implements syscall-number rewriting for `loongarch64` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- user_pt_regs loongarch_regs; syscall number regs[11]/a7, return regs[4]/a0, orig_a0 as argument 0, stack regs[3], PC csr_era

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/set_scno.c`: 15 lines; 330 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/syscallent.h -->
# sources/test-tools/strace/src/linux/loongarch64/syscallent.h

## Purpose
Defines the `loongarch64` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 0 decoder entries; first entries include none; final entries include none.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `loongarch64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `loongarch64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/syscallent.h`: 8 lines; 161 bytes; includes `#include "../64/syscallent.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_defs_.h -->
# sources/test-tools/strace/src/linux/m68k/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `m68k` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_M68K.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `m68k` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/arch_defs_.h`: 12 lines; 313 bytes; defines `#define HAVE_ARCH_OLD_MMAP 1`, `#define HAVE_ARCH_OLD_SELECT 1`, `#define HAVE_ARCH_UID16_SYSCALLS 1`, `#define HAVE_ARCH_SA_RESTORER 1`, `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_M68K, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_regs.c -->
# sources/test-tools/strace/src/linux/m68k/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `m68k` backend.

## Important APIs, Types, and Functions
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/arch_regs.c`: 11 lines; 280 bytes; defines `#define ARCH_REGS_FOR_GETREGS m68k_regs`, `#define ARCH_PC_REG m68k_regs.pc`, `#define ARCH_SP_REG m68k_regs.usp`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/m68k/arch_rt_sigframe.c

## Purpose
Implements or selects the `m68k` helper for locating an rt-signal frame on the tracee stack.

## Important APIs, Types, and Functions
- Provides `FUNC_GET_RT_SIGFRAME_ADDR` directly or includes another architecture's compatible implementation.

## Control Flow
- The helper reads the current stack pointer, applies the architecture frame offset, and returns zero if stack-pointer acquisition fails.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `m68k`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/arch_rt_sigframe.c`: 1 lines; 38 bytes; includes `#include "../i386/arch_rt_sigframe.c"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/m68k/arch_sigreturn.c

## Purpose
Decodes legacy `m68k` sigreturn frames to print the signal mask restored by the kernel.

## Important APIs, Types, and Functions
- `arch_sigreturn(struct tcb *tcp)` reads the stack pointer and signal-context data with `umove_or_printaddr`/`umoven_or_printaddr`, then calls `tprintsigmask_addr`.

## Control Flow
- Fetch stack pointer, locate the architecture sigcontext, read the saved signal-mask words, and print them if all required reads succeed.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `m68k`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/arch_sigreturn.c`: 29 lines; 728 bytes; functions `arch_sigreturn`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_error.c -->
# sources/test-tools/strace/src/linux/m68k/get_error.c

## Purpose
Maps the `m68k` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc
- The helper decodes the architecture's result register and uses `is_negated_errno` when this ABI reports failures as negative return values.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `m68k` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/get_error.c`: 19 lines; 380 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_scno.c -->
# sources/test-tools/strace/src/linux/m68k/get_scno.c

## Purpose
Extracts the current `m68k` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `m68k` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/get_scno.c`: 14 lines; 275 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/m68k/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `m68k` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- six arguments are copied from d1, d2, d3, d4, d5, and a0
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `m68k`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/get_syscall_args.c`: 19 lines; 435 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/m68k/ioctls_arch0.h

## Purpose
Adds `m68k`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 23 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `m68k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `m68k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/ioctls_arch0.h`: 24 lines; 1476 bytes; 23 ioctl table rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/m68k/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `m68k` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `m68k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `m68k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/raw_syscall.h -->
# sources/test-tools/strace/src/linux/m68k/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `m68k`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- trap #0 with d0 containing both syscall number and return value
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `m68k` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/raw_syscall.h`: 28 lines; 567 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/m68k/rt_sigframe.h

## Purpose
Defines the `m68k` real-time signal-frame layout metadata used to locate saved signal masks.

## Important APIs, Types, and Functions
- Declares `struct_rt_sigframe` or `RT_SIGFRAME_UC_UCONTEXT_OFFSET`/`RT_SIGFRAME_UC_SIGMASK_OFFSET` constants for shared signal-frame code.

## Control Flow
- No runtime control flow; architecture signal-frame readers use these offsets when walking tracee stack memory.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `m68k`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/rt_sigframe.h`: 23 lines; 410 bytes; includes `# include <signal.h>`; defines `# define STRACE_RT_SIGFRAME_H`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_error.c -->
# sources/test-tools/strace/src/linux/m68k/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `m68k` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/set_error.c`: 20 lines; 344 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_scno.c -->
# sources/test-tools/strace/src/linux/m68k/set_scno.c

## Purpose
Implements syscall-number rewriting for `m68k` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- user_regs_struct m68k_regs; syscall number orig_d0, return d0, args d1/d2/d3/d4/d5/a0, stack usp, PC pc

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/set_scno.c`: 15 lines; 324 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/syscallent.h -->
# sources/test-tools/strace/src/linux/m68k/syscallent.h

## Purpose
Defines the `m68k` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 393 decoder entries; first entries include restart_syscall, exit, fork, read, write, open; final entries include shmat, shmdt, msgget, msgsnd, msgrcv, msgctl.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `m68k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `m68k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/syscallent.h`: 409 lines; 20822 bytes; includes `#include "../32/syscallent-common-32.h"`, `#include "syscallent-common.h"`, `#include "../32/subcallent.h"`; defines `#define SYS_socket_subcall	500`; 393 `SEN(...)` syscall decoder references; first restart_syscall, exit, fork, read; last msgget, msgsnd, msgrcv, msgctl. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/userent.h -->
# sources/test-tools/strace/src/linux/m68k/userent.h

## Purpose
Provides the ptrace user-area offset to register-name table for strace's `m68k` register printers.

## Important APIs, Types, and Functions
- The file contributes initializer rows of `{ offset, name }` pairs and may include `userent0.h` for common trailing entries.
- Rows cover architecture-visible register offsets; source facts show 0 explicit offset/name entries.

## Control Flow
- There is no runtime branch logic; generic user-area decoding iterates the compiled table when printing PTRACE_PEEKUSER-style offsets.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `m68k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Offsets must match kernel UAPI headers for the exact architecture ABI; stale offsets produce plausible-looking but wrong register names.

## Test Signals
- Build strace for `m68k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/userent.h`: 41 lines; 745 bytes; includes `#include "userent0.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_defs_.h -->
# sources/test-tools/strace/src/linux/metag/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `metag` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to EM_METAG|__AUDIT_ARCH_LE.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `metag` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/arch_defs_.h`: 1 lines; 64 bytes; defines `#define PERSONALITY0_AUDIT_ARCH { EM_METAG|__AUDIT_ARCH_LE, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_regs.c -->
# sources/test-tools/strace/src/linux/metag/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `metag` backend.

## Important APIs, Types, and Functions
- user_gp_regs metag_regs; syscall number dx[0][1], result dx[0][0], stack ax[0][0], PC pc
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/arch_regs.c`: 11 lines; 287 bytes; defines `#define ARCH_REGS_FOR_GETREGSET metag_regs`, `#define ARCH_PC_REG metag_regs.pc`, `#define ARCH_SP_REG metag_regs.ax[0][0]`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c

## Purpose
Implements or selects the `metag` helper for locating an rt-signal frame on the tracee stack.

## Important APIs, Types, and Functions
- Provides `FUNC_GET_RT_SIGFRAME_ADDR` directly or includes another architecture's compatible implementation.

## Control Flow
- The helper reads the current stack pointer, applies the architecture frame offset, and returns zero if stack-pointer acquisition fails.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `metag`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c`: 15 lines; 293 bytes; includes `#include "rt_sigframe.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/get_error.c -->
# sources/test-tools/strace/src/linux/metag/get_error.c

## Purpose
Maps the `metag` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- user_gp_regs metag_regs; syscall number dx[0][1], result dx[0][0], stack ax[0][0], PC pc
- The helper decodes the architecture's result register and uses `is_negated_errno` when this ABI reports failures as negative return values.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `metag` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/get_error.c`: 20 lines; 439 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/get_scno.c -->
# sources/test-tools/strace/src/linux/metag/get_scno.c

## Purpose
Extracts the current `metag` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- user_gp_regs metag_regs; syscall number dx[0][1], result dx[0][0], stack ax[0][0], PC pc
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `metag` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/get_scno.c`: 14 lines; 315 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/metag/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `metag` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- arguments are taken from dx[0][1], dx[0][2], dx[0][3], dx[1][0], dx[1][1], and dx[1][2]
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `metag`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/get_syscall_args.c`: 17 lines; 394 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/metag/ioctls_arch0.h

## Purpose
Adds `metag`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 0 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `metag`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `metag` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/ioctls_arch0.h`: 1 lines; 92 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/metag/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `metag` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `metag`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `metag` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/raw_syscall.h -->
# sources/test-tools/strace/src/linux/metag/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `metag`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- SWITCH #0x440001 with D1Ar1 carrying the syscall number and D0Re0 receiving the result
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `metag` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/raw_syscall.h`: 29 lines; 629 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/set_error.c -->
# sources/test-tools/strace/src/linux/metag/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `metag` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- user_gp_regs metag_regs; syscall number dx[0][1], result dx[0][0], stack ax[0][0], PC pc

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/set_error.c`: 20 lines; 358 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/set_scno.c -->
# sources/test-tools/strace/src/linux/metag/set_scno.c

## Purpose
Implements syscall-number rewriting for `metag` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- user_gp_regs metag_regs; syscall number dx[0][1], result dx[0][0], stack ax[0][0], PC pc

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/set_scno.c`: 15 lines; 326 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/syscallent.h -->
# sources/test-tools/strace/src/linux/metag/syscallent.h

## Purpose
Defines the `metag` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 4 decoder entries; first entries include printargs, printargs, printargs, printargs; final entries include printargs, printargs, printargs, printargs.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `metag`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `metag` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/syscallent.h`: 13 lines; 420 bytes; includes `#include "../32/syscallent.h"`; 4 `SEN(...)` syscall decoder references; first printargs, printargs, printargs, printargs; last printargs, printargs, printargs, printargs. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/arch_defs_.h -->
# sources/test-tools/strace/src/linux/microblaze/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `microblaze` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_MICROBLAZE.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `microblaze` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/arch_defs_.h`: 10 lines; 258 bytes; defines `#define HAVE_ARCH_OLD_SELECT 1`, `#define HAVE_ARCH_UID16_SYSCALLS 1`, `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_MICROBLAZE, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/arch_regs.c -->
# sources/test-tools/strace/src/linux/microblaze/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `microblaze` backend.

## Important APIs, Types, and Functions
- ptrace offsets are used; syscall number is PT_GPR(0), result r3, stack PT_GPR(1), PC PT_PC
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/arch_regs.c`: 10 lines; 235 bytes; defines `#define ARCH_PC_PEEK_ADDR PT_PC`, `#define ARCH_SP_PEEK_ADDR PT_GPR(1)`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/microblaze/arch_sigreturn.c

## Purpose
Decodes legacy `microblaze` sigreturn frames to print the signal mask restored by the kernel.

## Important APIs, Types, and Functions
- `arch_sigreturn(struct tcb *tcp)` reads the stack pointer and signal-context data with `umove_or_printaddr`/`umoven_or_printaddr`, then calls `tprintsigmask_addr`.

## Control Flow
- Fetch stack pointer, locate the architecture sigcontext, read the saved signal-mask words, and print them if all required reads succeed.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `microblaze`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/arch_sigreturn.c`: 21 lines; 407 bytes; functions `arch_sigreturn`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_error.c -->
# sources/test-tools/strace/src/linux/microblaze/get_error.c

## Purpose
Maps the `microblaze` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- ptrace offsets are used; syscall number is PT_GPR(0), result r3, stack PT_GPR(1), PC PT_PC
- The helper decodes the architecture's result register and uses `is_negated_errno` when this ABI reports failures as negative return values.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `microblaze` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/get_error.c`: 19 lines; 383 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_scno.c -->
# sources/test-tools/strace/src/linux/microblaze/get_scno.c

## Purpose
Extracts the current `microblaze` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- ptrace offsets are used; syscall number is PT_GPR(0), result r3, stack PT_GPR(1), PC PT_PC
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `microblaze` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/get_scno.c`: 13 lines; 280 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/microblaze/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `microblaze` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- arguments are fetched from PT_GPR(5) through PT_GPR(10), with r3 cached for result decoding
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `microblaze`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/get_syscall_args.c`: 16 lines; 362 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c -->
# sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c

## Purpose
Fetches MicroBlaze result registers before syscall-exit decoding.

## Important APIs, Types, and Functions
- `get_syscall_result_regs(struct tcb *tcp)` reads `PT_GPR(3)` into the static `microblaze_r3` cache with `upeek`.

## Control Flow
- On syscall exit, the helper peeks the result register and returns the ptrace read status.

## State and Persistence Behavior
- Updates only the local cached result register used by `get_error.c`.

## Dependencies and Integration Points
- Called by the generic syscall-result path before MicroBlaze error decoding.

## Risks and Edge Cases
- If the peek fails or uses the wrong offset, later success/error decoding reads stale or invalid data.

## Test Signals
- Trace success and failure syscalls while checking that `microblaze_r3`-based return decoding matches kernel results.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c`: 12 lines; 243 bytes; functions `get_syscall_result_regs`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/get_syscall_result.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/microblaze/ioctls_arch0.h

## Purpose
Adds `microblaze`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 0 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `microblaze`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `microblaze` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/ioctls_arch0.h`: 1 lines; 97 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/microblaze/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `microblaze` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `microblaze`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `microblaze` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/raw_syscall.h -->
# sources/test-tools/strace/src/linux/microblaze/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `microblaze`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- brki r14, 0x8 with r12 carrying the syscall number and r3 receiving the result
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `microblaze` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/raw_syscall.h`: 30 lines; 676 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/set_error.c -->
# sources/test-tools/strace/src/linux/microblaze/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `microblaze` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- ptrace offsets are used; syscall number is PT_GPR(0), result r3, stack PT_GPR(1), PC PT_PC

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/set_error.c`: 20 lines; 374 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/set_scno.c -->
# sources/test-tools/strace/src/linux/microblaze/set_scno.c

## Purpose
Implements syscall-number rewriting for `microblaze` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- ptrace offsets are used; syscall number is PT_GPR(0), result r3, stack PT_GPR(1), PC PT_PC

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/set_scno.c`: 12 lines; 227 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/syscallent.h -->
# sources/test-tools/strace/src/linux/microblaze/syscallent.h

## Purpose
Defines the `microblaze` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 397 decoder entries; first entries include restart_syscall, exit, fork, read, write, open; final entries include pkey_mprotect, pkey_alloc, pkey_free, statx, io_pgetevents_time32, rseq.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `microblaze`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `microblaze` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/syscallent.h`: 412 lines; 20944 bytes; includes `#include "../32/syscallent-common-32.h"`, `#include "syscallent-common.h"`; 397 `SEN(...)` syscall decoder references; first restart_syscall, exit, fork, read; last pkey_free, statx, io_pgetevents_time32, rseq. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/userent.h -->
# sources/test-tools/strace/src/linux/microblaze/userent.h

## Purpose
Provides the ptrace user-area offset to register-name table for strace's `microblaze` register printers.

## Important APIs, Types, and Functions
- The file contributes initializer rows of `{ offset, name }` pairs and may include `userent0.h` for common trailing entries.
- Rows cover architecture-visible register offsets; source facts show 38 explicit offset/name entries.

## Control Flow
- There is no runtime branch logic; generic user-area decoding iterates the compiled table when printing PTRACE_PEEKUSER-style offsets.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `microblaze`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Offsets must match kernel UAPI headers for the exact architecture ABI; stale offsets produce plausible-looking but wrong register names.

## Test Signals
- Build strace for `microblaze` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/microblaze/userent.h`: 47 lines; 1075 bytes; includes `#include "userent0.h"`; 38 ptrace user offset/name rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/microblaze/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_defs_.h -->
# sources/test-tools/strace/src/linux/mips/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `mips` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to MIPS o32/n32/n64 audit personalities selected by ABI/endian macros.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `mips` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_defs_.h`: 28 lines; 851 bytes; defines `#define HAVE_ARCH_GETRVAL2 1`, `#define HAVE_ARCH_DEDICATED_ERR_REG 1`, `#define CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_getrval2.c -->
# sources/test-tools/strace/src/linux/mips/arch_getrval2.c

## Purpose
Returns the architecture-specific second syscall return value for `mips` when the ABI exposes one.

## Important APIs, Types, and Functions
- `getrval2(struct tcb *tcp)` refreshes registers if ptrace syscall-info requires it and returns the second result register (`gr[9]` on IA-64 or `uregs[3]`/`v1` on MIPS).

## Control Flow
- Fetch registers if necessary, then return the ABI second-result register as a `long`.

## State and Persistence Behavior
- No persistence; it reads the current cached register snapshot.

## Dependencies and Integration Points
- Used when syscall decoders request `RVAL2` handling through `HAVE_ARCH_GETRVAL2`.

## Risks and Edge Cases
- Register freshness and ABI selection matter; a stale snapshot returns the previous syscall's secondary value.

## Test Signals
- Trace syscalls with two return values, especially `pipe` on ABIs that report file descriptors in two registers.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_getrval2.c`: 14 lines; 265 bytes; functions `getrval2`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_getrval2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.c

## Purpose
Decodes and prints a `mips` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.c`: 56 lines; 1611 bytes; functions `arch_decode_prstatus_regset`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.h

## Purpose
Declares the `mips` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.h`: 26 lines; 555 bytes; defines `# define STRACE_ARCH_PRSTATUS_REGSET_H`, `# define HAVE_ARCH_PRSTATUS_REGSET 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_pt_regs.c -->
# sources/test-tools/strace/src/linux/mips/arch_pt_regs.c

## Purpose
Decodes and prints a `mips` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_pt_regs.c`: 40 lines; 749 bytes; includes `#include "ptrace.h"`; functions `arch_decode_pt_regs`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_pt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_regs.c -->
# sources/test-tools/strace/src/linux/mips/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `mips` backend.

## Important APIs, Types, and Functions
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_regs.c`: 28 lines; 799 bytes; defines `#define REG_V0 2`, `#define REG_A0 4`, `#define mips_REG_V0 mips_regs.uregs[REG_V0]`, `#define mips_REG_A0 mips_regs.uregs[REG_A0 + 0]`, `#define mips_REG_A1 mips_regs.uregs[REG_A0 + 1]`, `#define mips_REG_A2 mips_regs.uregs[REG_A0 + 2]`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/mips/arch_sigreturn.c

## Purpose
Decodes legacy `mips` sigreturn frames to print the signal mask restored by the kernel.

## Important APIs, Types, and Functions
- `arch_sigreturn(struct tcb *tcp)` reads the stack pointer and signal-context data with `umove_or_printaddr`/`umoven_or_printaddr`, then calls `tprintsigmask_addr`.

## Control Flow
- Fetch stack pointer, locate the architecture sigcontext, read the saved signal-mask words, and print them if all required reads succeed.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `mips`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_sigreturn.c`: 24 lines; 513 bytes; functions `arch_sigreturn`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/errnoent.h -->
# sources/test-tools/strace/src/linux/mips/errnoent.h

## Purpose
Defines architecture errno name ordering for `mips` when it differs from the generic strace errno table.

## Important APIs, Types, and Functions
- The header is a data initializer consumed by strace errno/xlat infrastructure; PowerPC delegates to `../generic/errnoent.h`, while MIPS carries a full ABI-specific list.

## Control Flow
- No runtime control flow in the file; lookup is table-driven by the core errno decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- The numeric position of each string is the ABI contract. Insertions, deletions, or accidental generic substitution can make every later errno decode wrong.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/errnoent.h`: 158 lines; 3133 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/genstub.sh -->
# sources/test-tools/strace/src/linux/mips/genstub.sh

## Purpose
Generates placeholder MIPS syscall-table rows for unsupported or compatibility syscall ranges.

## Important APIs, Types, and Functions
- The shell script emits bracketed syscall table rows that map a numeric range to `SEN(printargs)` with generated `syscall_<nr>` names.
- It is a maintenance tool for table generation, not a runtime strace component.

## Control Flow
- The script iterates over numeric arguments/ranges supplied by the maintainer and prints C initializer rows.
- Generated rows can then be pasted or redirected into syscall table headers.

## State and Persistence Behavior
- No runtime tracer state; output is generated text that may become source-table state if checked in.

## Dependencies and Integration Points
- Used by maintainers alongside MIPS syscall table headers.
- Depends on POSIX shell arithmetic and the table macro format expected by strace.

## Risks and Edge Cases
- Generated placeholders are intentionally low-information; leaving them in active ranges means strace will print raw arguments instead of semantic decoders.
- Range mistakes can overwrite real syscall metadata.

## Test Signals
- Run the script on small sample ranges and diff output against expected C initializer syntax.
- After using generated rows, build strace and trace a syscall in the affected range.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/genstub.sh`: 15 lines; 434 bytes; 1 `SEN(...)` syscall decoder references; first printargs; last printargs. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/genstub.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_error.c -->
# sources/test-tools/strace/src/linux/mips/get_error.c

## Purpose
Maps the `mips` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34
- MIPS uses dedicated error register semantics: `mips_REG_A3` indicates failure and `mips_REG_V0` carries the positive errno or success result.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `mips` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/get_error.c`: 17 lines; 315 bytes; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_scno.c -->
# sources/test-tools/strace/src/linux/mips/get_scno.c

## Purpose
Extracts the current `mips` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34
- MIPS additionally ignores non-entry ptrace syscall-info stops and filters stray exits when `v0` is not a valid syscall number and `a3` looks like an exit error flag.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `mips` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/get_scno.c`: 27 lines; 629 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/mips/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `mips` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- n32/n64 use a0..a5, while o32 uses a0..a3 plus stack slots for arguments 5 and 6 and has subcall shuffling
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `mips`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/get_syscall_args.c`: 90 lines; 2380 bytes; functions `arch_get_syscall_args`, `arch_get_syscall_args_extra`, `decode_syscall_subcall`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/mips/ioctls_arch0.h

## Purpose
Adds `mips`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 149 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/ioctls_arch0.h`: 150 lines; 8778 bytes; 149 ioctl table rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/mips/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `mips` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/ioctls_inc0.h`: 12 lines; 227 bytes; includes `# include "../64/ioctls_inc.h"`, `# include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/raw_syscall.h -->
# sources/test-tools/strace/src/linux/mips/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `mips`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- syscall with v0 receiving the result and a3 carrying the kernel error indicator
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `mips` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/raw_syscall.h`: 45 lines; 1092 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/mips/rt_sigframe.h

## Purpose
Defines the `mips` real-time signal-frame layout metadata used to locate saved signal masks.

## Important APIs, Types, and Functions
- Declares `struct_rt_sigframe` or `RT_SIGFRAME_UC_UCONTEXT_OFFSET`/`RT_SIGFRAME_UC_SIGMASK_OFFSET` constants for shared signal-frame code.

## Control Flow
- No runtime control flow; architecture signal-frame readers use these offsets when walking tracee stack memory.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `mips`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/rt_sigframe.h`: 19 lines; 348 bytes; includes `# include <signal.h>`; defines `# define STRACE_RT_SIGFRAME_H`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/rt_sigframe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/set_error.c -->
# sources/test-tools/strace/src/linux/mips/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `mips` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/set_error.c`: 22 lines; 378 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/set_scno.c -->
# sources/test-tools/strace/src/linux/mips/set_scno.c

## Purpose
Implements syscall-number rewriting for `mips` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/set_scno.c`: 15 lines; 318 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/signalent.h -->
# sources/test-tools/strace/src/linux/mips/signalent.h

## Purpose
Defines the MIPS signal-number to signal-name table used by signal decoders.

## Important APIs, Types, and Functions
- The file is a string initializer array with Linux/MIPS signal names including architecture-specific real-time signal numbering conventions.

## Control Flow
- No executable control flow; consumers index the table by signal number.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Off-by-one table edits or generic signal table reuse would make signal traces misleading, especially for SIGRT ranges and architecture-specific aliases.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/signalent.h`: 40 lines; 801 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/signalent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-compat.h -->
# sources/test-tools/strace/src/linux/mips/syscallent-compat.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 674 decoder entries; first entries include printargs, printargs, printargs, printargs, printargs, printargs; final entries include printargs, printargs, printargs, printargs, printargs, printargs.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent-compat.h`: 707 lines; 36284 bytes; 674 `SEN(...)` syscall decoder references; first printargs, printargs, printargs, printargs; last printargs, printargs, printargs, printargs. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-n32.h -->
# sources/test-tools/strace/src/linux/mips/syscallent-n32.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 332 decoder entries; first entries include read, write, open, close, stat64, fstat64; final entries include pkey_mprotect, pkey_alloc, pkey_free, statx, rseq, io_pgetevents_time32.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent-n32.h`: 359 lines; 21238 bytes; includes `# include "../32/syscallent-common-32.h"`, `# include "syscallent-common.h"`, `# include "../32/subcallent.h"`, `# include "syscallent-n32-stub.h"`, `# include "syscallent-common-32-stub.h"`; defines `#define BASE_NR 6000`, `# define SYS_socket_subcall      6500`, `# define SYSCALL_NAME_PREFIX "n32:"`, `#undef BASE_NR`; 332 `SEN(...)` syscall decoder references; first read, write, open, close; last pkey_free, statx, rseq, io_pgetevents_time32. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-n32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-n64.h -->
# sources/test-tools/strace/src/linux/mips/syscallent-n64.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 328 decoder entries; first entries include read, write, open, close, stat, fstat; final entries include pkey_mprotect, pkey_alloc, pkey_free, statx, rseq, io_pgetevents_time64.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent-n64.h`: 353 lines; 20884 bytes; includes `# include "syscallent-common.h"`, `# include "../64/subcallent.h"`, `# include "syscallent-n64-stub.h"`, `# include "syscallent-common-stub.h"`; defines `#define BASE_NR 5000`, `# define SYS_socket_subcall      5500`, `# define SYSCALL_NAME_PREFIX "n64:"`, `#undef BASE_NR`; 328 `SEN(...)` syscall decoder references; first read, write, open, close; last pkey_free, statx, rseq, io_pgetevents_time64. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-n64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-o32.h -->
# sources/test-tools/strace/src/linux/mips/syscallent-o32.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 378 decoder entries; first entries include syscall, exit, fork, read, write, open; final entries include shmat, shmdt, msgget, msgsnd, msgrcv, msgctl.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent-o32.h`: 407 lines; 23981 bytes; includes `# include "../32/syscallent-common-32.h"`, `# include "syscallent-common.h"`, `# include "../32/subcallent.h"`, `# include "syscallent-o32-stub.h"`, `# include "syscallent-common-32-stub.h"`; defines `#define BASE_NR 4000`, `# define SYS_syscall_subcall	4000`, `# define SYS_socket_subcall      4500`, `# define SYSCALL_NAME_PREFIX "o32:"`, `#undef BASE_NR`; 378 `SEN(...)` syscall decoder references; first syscall, exit, fork, read; last msgget, msgsnd, msgrcv, msgctl. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-o32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent.h -->
# sources/test-tools/strace/src/linux/mips/syscallent.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- This wrapper composes one or more shared or ABI-specific syscall tables using `#include` directives rather than listing all rows inline.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent.h`: 4 lines; 115 bytes; includes `#include "syscallent-compat.h"`, `#include "syscallent-o32.h"`, `#include "syscallent-n64.h"`, `#include "syscallent-n32.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/userent.h -->
# sources/test-tools/strace/src/linux/mips/userent.h

## Purpose
Provides the ptrace user-area offset to register-name table for strace's `mips` register printers.

## Important APIs, Types, and Functions
- The file contributes initializer rows of `{ offset, name }` pairs and may include `userent0.h` for common trailing entries.
- Rows cover architecture-visible register offsets; source facts show 71 explicit offset/name entries.

## Control Flow
- There is no runtime branch logic; generic user-area decoding iterates the compiled table when printing PTRACE_PEEKUSER-style offsets.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Offsets must match kernel UAPI headers for the exact architecture ABI; stale offsets produce plausible-looking but wrong register names.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/userent.h`: 90 lines; 1582 bytes; includes `#include "userent0.h"`; 71 ptrace user offset/name rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/arch_defs_.h -->
# sources/test-tools/strace/src/linux/nios2/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `nios2` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_NIOS2.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `nios2` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/arch_defs_.h`: 9 lines; 225 bytes; defines `#define HAVE_ARCH_DEDICATED_ERR_REG 1`, `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_NIOS2, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/arch_regs.c -->
# sources/test-tools/strace/src/linux/nios2/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `nios2` backend.

## Important APIs, Types, and Functions
- user_pt_regs nios2_regs; syscall number regs[2], success/error flag regs[7], return regs[2], stack PTR_SP, PC PTR_EA
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/arch_regs.c`: 11 lines; 301 bytes; defines `#define ARCH_REGS_FOR_GETREGSET nios2_regs`, `#define ARCH_PC_REG nios2_regs.regs[PTR_EA]`, `#define ARCH_SP_REG nios2_regs.regs[PTR_SP]`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_error.c -->
# sources/test-tools/strace/src/linux/nios2/get_error.c

## Purpose
Maps the `nios2` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- user_pt_regs nios2_regs; syscall number regs[2], success/error flag regs[7], return regs[2], stack PTR_SP, PC PTR_EA
- Nios II treats `regs[7]` as the success/error flag and `regs[2]` as either return value or positive errno.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `nios2` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/get_error.c`: 24 lines; 651 bytes; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_scno.c -->
# sources/test-tools/strace/src/linux/nios2/get_scno.c

## Purpose
Extracts the current `nios2` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- user_pt_regs nios2_regs; syscall number regs[2], success/error flag regs[7], return regs[2], stack PTR_SP, PC PTR_EA
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `nios2` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/get_scno.c`: 14 lines; 276 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/nios2/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `nios2` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- arguments come from regs[4] through regs[9]
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `nios2`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/get_syscall_args.c`: 19 lines; 471 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/nios2/ioctls_arch0.h

## Purpose
Adds `nios2`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 0 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `nios2`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `nios2` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/ioctls_arch0.h`: 1 lines; 92 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/nios2/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `nios2` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `nios2`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `nios2` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/raw_syscall.h -->
# sources/test-tools/strace/src/linux/nios2/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `nios2`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- trap with r2 carrying the syscall number/result and r7 carrying the error flag
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `nios2` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/raw_syscall.h`: 29 lines; 609 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/set_error.c -->
# sources/test-tools/strace/src/linux/nios2/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `nios2` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- user_pt_regs nios2_regs; syscall number regs[2], success/error flag regs[7], return regs[2], stack PTR_SP, PC PTR_EA

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/set_error.c`: 22 lines; 406 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/set_scno.c -->
# sources/test-tools/strace/src/linux/nios2/set_scno.c

## Purpose
Implements syscall-number rewriting for `nios2` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- user_pt_regs nios2_regs; syscall number regs[2], success/error flag regs[7], return regs[2], stack PTR_SP, PC PTR_EA

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/set_scno.c`: 15 lines; 325 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/syscallent.h -->
# sources/test-tools/strace/src/linux/nios2/syscallent.h

## Purpose
Defines the `nios2` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 1 decoder entries; first entries include cacheflush; final entries include cacheflush.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `nios2`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `nios2` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/nios2/syscallent.h`: 11 lines; 286 bytes; includes `#include "../32/syscallent.h"`; defines `#define sys_ARCH_mmap sys_mmap_pgoff`; 1 `SEN(...)` syscall decoder references; first cacheflush; last cacheflush. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/nios2/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/arch_defs_.h -->
# sources/test-tools/strace/src/linux/or1k/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `or1k` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_OPENRISC.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `or1k` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/arch_defs_.h`: 1 lines; 59 bytes; defines `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_OPENRISC, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/arch_regs.c -->
# sources/test-tools/strace/src/linux/or1k/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `or1k` backend.

## Important APIs, Types, and Functions
- user_regs_struct or1k_regs; syscall number gpr[11], return gpr[11], stack gpr[1], PC pc
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/arch_regs.c`: 11 lines; 285 bytes; defines `#define ARCH_REGS_FOR_GETREGSET or1k_regs`, `#define ARCH_PC_REG or1k_regs.pc`, `#define ARCH_SP_REG or1k_regs.gpr[1]`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_error.c -->
# sources/test-tools/strace/src/linux/or1k/get_error.c

## Purpose
Maps the `or1k` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- user_regs_struct or1k_regs; syscall number gpr[11], return gpr[11], stack gpr[1], PC pc
- The helper decodes the architecture's result register and uses `is_negated_errno` when this ABI reports failures as negative return values.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `or1k` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/get_error.c`: 19 lines; 395 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_scno.c -->
# sources/test-tools/strace/src/linux/or1k/get_scno.c

## Purpose
Extracts the current `or1k` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- user_regs_struct or1k_regs; syscall number gpr[11], return gpr[11], stack gpr[1], PC pc
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `or1k` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/get_scno.c`: 14 lines; 275 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/or1k/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `or1k` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- arguments come from gpr[3] through gpr[8]
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `or1k`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/get_syscall_args.c`: 19 lines; 483 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/or1k/ioctls_arch0.h

## Purpose
Adds `or1k`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 0 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `or1k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `or1k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/ioctls_arch0.h`: 1 lines; 95 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/or1k/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `or1k` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `or1k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `or1k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/raw_syscall.h -->
# sources/test-tools/strace/src/linux/or1k/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `or1k`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- l.sys 1 with r11 carrying the syscall number/result
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `or1k` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/raw_syscall.h`: 30 lines; 695 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/set_error.c -->
# sources/test-tools/strace/src/linux/or1k/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `or1k` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- user_regs_struct or1k_regs; syscall number gpr[11], return gpr[11], stack gpr[1], PC pc

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/set_error.c`: 20 lines; 354 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/set_scno.c -->
# sources/test-tools/strace/src/linux/or1k/set_scno.c

## Purpose
Implements syscall-number rewriting for `or1k` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- user_regs_struct or1k_regs; syscall number gpr[11], return gpr[11], stack gpr[1], PC pc

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/set_scno.c`: 15 lines; 324 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/set_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/syscallent.h -->
# sources/test-tools/strace/src/linux/or1k/syscallent.h

## Purpose
Defines the `or1k` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 1 decoder entries; first entries include or1k_atomic; final entries include or1k_atomic.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `or1k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `or1k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/syscallent.h`: 11 lines; 288 bytes; includes `#include "../32/syscallent.h"`; defines `#define sys_ARCH_mmap sys_mmap_pgoff`; 1 `SEN(...)` syscall decoder references; first or1k_atomic; last or1k_atomic. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/syscallent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/userent.h -->
# sources/test-tools/strace/src/linux/or1k/userent.h

## Purpose
Provides the ptrace user-area offset to register-name table for strace's `or1k` register printers.

## Important APIs, Types, and Functions
- The file contributes initializer rows of `{ offset, name }` pairs and may include `userent0.h` for common trailing entries.
- Rows cover architecture-visible register offsets; source facts show 34 explicit offset/name entries.

## Control Flow
- There is no runtime branch logic; generic user-area decoding iterates the compiled table when printing PTRACE_PEEKUSER-style offsets.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `or1k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Offsets must match kernel UAPI headers for the exact architecture ABI; stale offsets produce plausible-looking but wrong register names.

## Test Signals
- Build strace for `or1k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/userent.h`: 41 lines; 697 bytes; 34 ptrace user offset/name rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/userent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_defs_.h -->
# sources/test-tools/strace/src/linux/powerpc/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `powerpc` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_PPC, with 64-bit kernels also able to trace compat personalities.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `powerpc` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_defs_.h`: 10 lines; 261 bytes; defines `#define HAVE_ARCH_OLD_SELECT 1`, `#define CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL 1`, `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_PPC, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_defs_.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_fpregset.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_fpregset.c

## Purpose
Decodes and prints a `powerpc` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_fpregset.c`: 32 lines; 790 bytes; functions `arch_decode_fpregset`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_fpregset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/powerpc/arch_fpregset.h

## Purpose
Declares the `powerpc` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_fpregset.h`: 18 lines; 331 bytes; defines `# define STRACE_ARCH_FPREGSET_H`, `# define HAVE_ARCH_FPREGSET 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_fpregset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c

## Purpose
Decodes and prints a `powerpc` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c`: 91 lines; 2460 bytes; defines `# define TRACEE_KLONGSIZE 4`, `# define TRACEE_KLONGSIZE SIZEOF_KERNEL_LONG_T`, `#undef TRACEE_KLONGSIZE`; functions `arch_decode_prstatus_regset`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h

## Purpose
Declares the `powerpc` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h`: 15 lines; 334 bytes; defines `# define STRACE_ARCH_PRSTATUS_REGSET_H`, `# define HAVE_ARCH_PRSTATUS_REGSET 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.c

## Purpose
Decodes and prints a `powerpc` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.c`: 58 lines; 1052 bytes; includes `#include "arch_pt_regs64.h"`; functions `decode_pt_regs64`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.h -->
# sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.h

## Purpose
Declares the `powerpc` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.h`: 27 lines; 612 bytes; defines `# define STRACE_ARCH_PT_REGS64_H`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_pt_regs64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_regs.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `powerpc` backend.

## Important APIs, Types, and Functions
- pt_regs ppc_regs; syscall number gpr[0], result gpr[3], orig_gpr3 as argument 0, stack gpr[1], PC nip, trap distinguishing sc/scv
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_regs.c`: 14 lines; 333 bytes; defines `#define ARCH_REGS_FOR_GETREGS ppc_regs`, `#define ARCH_PC_REG ppc_regs.nip`, `#define ARCH_SP_REG ppc_regs.gpr[1]`, `#define PPC_TRAP_IS_SCV(trap)	(((trap) & 0xfff0) == 0x3000)`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_rt_sigframe.c

## Purpose
Implements or selects the `powerpc` helper for locating an rt-signal frame on the tracee stack.

## Important APIs, Types, and Functions
- Provides `FUNC_GET_RT_SIGFRAME_ADDR` directly or includes another architecture's compatible implementation.

## Control Flow
- The helper reads the current stack pointer, applies the architecture frame offset, and returns zero if stack-pointer acquisition fails.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `powerpc`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_rt_sigframe.c`: 14 lines; 293 bytes; defines `#define SIGNAL_FRAMESIZE32	64`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_rt_sigframe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_sigreturn.c

## Purpose
Decodes legacy `powerpc` sigreturn frames to print the signal mask restored by the kernel.

## Important APIs, Types, and Functions
- `arch_sigreturn(struct tcb *tcp)` reads the stack pointer and signal-context data with `umove_or_printaddr`/`umoven_or_printaddr`, then calls `tprintsigmask_addr`.

## Control Flow
- Fetch stack pointer, locate the architecture sigcontext, read the saved signal-mask words, and print them if all required reads succeed.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `powerpc`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_sigreturn.c`: 41 lines; 788 bytes; functions `arch_sigreturn`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/errnoent.h -->
# sources/test-tools/strace/src/linux/powerpc/errnoent.h

## Purpose
Defines architecture errno name ordering for `powerpc` when it differs from the generic strace errno table.

## Important APIs, Types, and Functions
- The header is a data initializer consumed by strace errno/xlat infrastructure; PowerPC delegates to `../generic/errnoent.h`, while MIPS carries a full ABI-specific list.

## Control Flow
- No runtime control flow in the file; lookup is table-driven by the core errno decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `powerpc`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- The numeric position of each string is the ABI contract. Insertions, deletions, or accidental generic substitution can make every later errno decode wrong.

## Test Signals
- Build strace for `powerpc` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/errnoent.h`: 9 lines; 185 bytes; includes `#include "../generic/errnoent.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/errnoent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/get_error.c -->
# sources/test-tools/strace/src/linux/powerpc/get_error.c

## Purpose
Maps the `powerpc` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- pt_regs ppc_regs; syscall number gpr[0], result gpr[3], orig_gpr3 as argument 0, stack gpr[1], PC nip, trap distinguishing sc/scv
- PowerPC distinguishes `scv` traps, where negative errno is returned in `gpr[3]`, from classic `sc`, where CCR bit 28 indicates an error and `gpr[3]` is positive errno.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `powerpc` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/get_error.c`: 28 lines; 587 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/get_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/get_scno.c -->
# sources/test-tools/strace/src/linux/powerpc/get_scno.c

## Purpose
Extracts the current `powerpc` syscall number from the cached register set into `tcp->scno`.

## Important APIs, Types, and Functions
- `arch_get_scno(struct tcb *tcp)` is the architecture syscall-number hook.
- pt_regs ppc_regs; syscall number gpr[0], result gpr[3], orig_gpr3 as argument 0, stack gpr[1], PC nip, trap distinguishing sc/scv
- The function returns `1` on a usable syscall number.

## Control Flow
- The generic entry path has already fetched registers; this hook copies the ABI syscall-number register into `tcp->scno`.
- The return code tells the caller whether to decode, ignore the stop, or treat it as an error.

## State and Persistence Behavior
- Updates only the current `struct tcb` syscall-number field; no persistence or allocation is involved.

## Dependencies and Integration Points
- Called before syscall-table lookup and argument decoding.
- Depends on sibling register snapshot definitions and core helpers such as `scno_in_range` on MIPS.

## Risks and Edge Cases
- A wrong source register indexes the wrong syscall table row for every syscall.
- Entry/exit stop confusion is a risk on architectures where result registers overlap syscall-number registers.

## Test Signals
- Trace several known syscalls on `powerpc` and verify names match the invoked calls.
- Include invalid syscall and restart cases where the architecture has special filtering.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/get_scno.c`: 14 lines; 273 bytes; functions `arch_get_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/get_scno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/powerpc/get_syscall_args.c

## Purpose
Populates `tcp->u_arg[]` with decoded syscall arguments for the `powerpc` ABI.

## Important APIs, Types, and Functions
- `arch_get_syscall_args(struct tcb *tcp)` is the primary architecture argument hook.
- orig_gpr3 plus gpr[4] through gpr[8], zero-extended for compat personality
- MIPS o32 includes extra helpers for stack arguments and syscall subcall rewriting; IA-64 recovers out registers from the register backing store.

## Control Flow
- After syscall number extraction, the hook copies register arguments into `tcp->u_arg` in decoder order.
- When the ABI stores extra arguments on the tracee stack, the helper uses `umoven` or `get_stack_pointer` and falls back to zero-filled arguments on recoverable fetch failures.
- Subcall handlers may rewrite `tcp->scno`, `tcp->true_scno`, `tcp->qual_flg`, `tcp->s_ent`, and shift `u_arg` entries to match the real syscall.

## State and Persistence Behavior
- Mutates transient `struct tcb` argument and syscall identity fields only.
- Tracee memory is read for stack/register-backing-store arguments but not persisted.

## Dependencies and Integration Points
- Called by the generic syscall-entry decoder before dispatching the selected `SEN(...)` syscall printer.
- Depends on register snapshot macros, `n_args(tcp)`, `umove/umoven`, stack-pointer helpers, and syscall qualification tables.

## Risks and Edge Cases
- Argument order, sign/zero extension, and stack slot offsets are ABI-sensitive.
- Partial memory-read fallback keeps tracing alive but can hide argument-fetch failures unless tests check error messages and zeroed tail arguments.

## Test Signals
- Trace syscalls with 0 through 6 arguments on `powerpc`.
- For MIPS o32 and IA-64, include calls requiring stack/register-backing-store arguments and subcall decoding.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/get_syscall_args.c`: 34 lines; 964 bytes; functions `arch_get_syscall_args`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/get_syscall_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/powerpc/ioctls_arch0.h

## Purpose
Adds `powerpc`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 182 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `powerpc`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `powerpc` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/ioctls_arch0.h`: 183 lines; 11529 bytes; 182 ioctl table rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/ioctls_arch0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/powerpc/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `powerpc` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `powerpc`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `powerpc` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../32/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/ioctls_inc0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/raw_syscall.h -->
# sources/test-tools/strace/src/linux/powerpc/raw_syscall.h

## Purpose
Provides the inline raw syscall helper used by strace test/support code on `powerpc`.

## Important APIs, Types, and Functions
- `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` invokes a zero-argument syscall directly using inline assembly.
- sc with r0 carrying the syscall number, r3 the return value, and ccr bit 28 the traditional error indicator
- The helper returns the raw result register and stores an ABI-specific error indicator in `*err` when the architecture exposes one.

## Control Flow
- Initialize syscall-number and result/error registers, execute the architecture syscall instruction, copy the error flag, and return the result register.
- The clobber list documents registers the kernel ABI may overwrite.

## State and Persistence Behavior
- No persistent state; only CPU registers and the caller-provided `err` storage are affected.

## Dependencies and Integration Points
- Included by strace low-level tests and helper code needing direct syscalls without libc wrappers.
- Depends on compiler support for architecture register variables and exact kernel syscall ABI conventions.

## Risks and Edge Cases
- Inline assembly constraints are brittle across compiler versions and ISA revisions.
- Wrong clobbers can create miscompiled tests that fail nondeterministically rather than at compile time.

## Test Signals
- Compile native `powerpc` test binaries with optimization enabled.
- Run raw syscall probes for a guaranteed-success syscall and a guaranteed-failing syscall, checking both return and error flag.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/raw_syscall.h`: 32 lines; 743 bytes; includes `# include "kernel_types.h"`; defines `# define STRACE_RAW_SYSCALL_H`, `# define raw_syscall_0 raw_syscall_0`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/raw_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/set_error.c -->
# sources/test-tools/strace/src/linux/powerpc/set_error.c

## Purpose
Implements syscall tampering hooks that write normalized strace success or error results back into `powerpc` tracee registers.

## Important APIs, Types, and Functions
- `arch_set_error(struct tcb *tcp)` writes `tcp->u_error` using the architecture's failure convention.
- `arch_set_success(struct tcb *tcp)` writes `tcp->u_rval` using the architecture's success convention.
- pt_regs ppc_regs; syscall number gpr[0], result gpr[3], orig_gpr3 as argument 0, stack gpr[1], PC nip, trap distinguishing sc/scv

## Control Flow
- The helper edits the cached register snapshot, adjusts any dedicated error flag or condition-code bit required by the ABI, then calls `set_regs(tcp->pid)` or an equivalent ptrace write helper.
- PowerPC handles `scv` and classic `sc` differently; Nios II clears or sets the dedicated `regs[7]` flag; negative-errno architectures write the negated error into the result register.

## State and Persistence Behavior
- State is external: the function changes live tracee registers through ptrace and updates no persistent files or tables.

## Dependencies and Integration Points
- Used by strace injection/tampering paths that force syscall return values.
- Depends on the same register object used by get-error decoding and on common ptrace register write helpers.

## Risks and Edge Cases
- Error sign and dedicated flag handling must mirror `get_error.c`; asymmetry causes injected results to be reported differently from kernel results.
- Register writes can fail if the tracee has disappeared or if ptrace state is not at a writable syscall stop.

## Test Signals
- Use strace fault/result injection tests to force both success and failure returns.
- Verify that a subsequent syscall-exit decode prints the injected value and errno consistently.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/set_error.c`: 27 lines; 536 bytes; functions `arch_set_error`, `arch_set_success`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/set_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/set_scno.c -->
# sources/test-tools/strace/src/linux/powerpc/set_scno.c

## Purpose
Implements syscall-number rewriting for `powerpc` syscall injection and tampering support.

## Important APIs, Types, and Functions
- `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)` writes a replacement syscall number.
- pt_regs ppc_regs; syscall number gpr[0], result gpr[3], orig_gpr3 as argument 0, stack gpr[1], PC nip, trap distinguishing sc/scv

## Control Flow
- When ptrace syscall-info does not already provide a fresh register snapshot, the helper fetches registers as needed.
- It writes the architecture syscall-number register or ptrace user offset and commits the change with `set_regs`/`upoke`.

## State and Persistence Behavior
- The only state change is the live tracee register update; no repo or tracer-persistent data is written.

## Dependencies and Integration Points
- Used by syscall injection paths before resuming the tracee.
- Depends on architecture register layout and ptrace write semantics.

## Risks and Edge Cases
- Writing the wrong register can turn syscall injection into argument corruption.
- Some architectures need a fresh register fetch before modifying the cached object; skipping that can overwrite unrelated registers with stale values.

## Test Signals
- Use strace syscall injection tests that replace one syscall with another and verify the kernel executes the replacement.
- Check both ptrace syscall-info and legacy ptrace paths where available.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/set_scno.c`: 12 lines; 246 bytes; functions `arch_set_scno`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/set_scno.c -->

## `sources/distributed-fs/ceph-client/arch/x86/events/utils.c`

Purpose: decodes x86 control-flow instructions around LBR/perf branch samples and maps x86-internal branch classifications to generic perf branch types.

Important APIs and functions: `branch_type()`, `branch_type_fused()`, and `common_branch_type()` are exported through `perf_event.h`. Internally, `decode_branch_type()` classifies decoded opcodes, and `get_branch_type()` safely fetches instruction bytes from user or kernel text, handles transaction aborts, optional fused-branch scanning, privilege-level tagging, and IRQ/fault inference.

Control flow: for user addresses the code uses `copy_from_user_nmi()` and requires a current mm; for kernel addresses it checks `kernel_text_address()` and rejects gate areas. It initializes the x86 instruction decoder with ABI mode, decodes one instruction, optionally scans forward up to `MAX_INSN_SIZE` for fused branches, then combines branch kind with target user/kernel bits.

State and persistence: no persistent state. It reads current task/register mode and text mappings at classification time.

Dependencies and integration points: `asm/insn.h`, NMI-safe user copying, kernel text validation, perf branch enum values, and branch constants from `perf_event.h`. Intel and AMD LBR/BRS paths use these helpers to enrich branch stack samples.

Risks: instruction fetch occurs in perf/NMI-sensitive paths, so it must avoid unsafe kernel reads from attacker-controlled addresses. Misclassification affects profiling quality rather than normal execution, but unsafe fetches would be serious. Fused scanning must not run past the copied byte window.

Test signals: perf LBR branch stack samples for syscalls, returns, indirect calls, conditional branches, interrupts, and fused branches; fault-injection with unmapped user text; KASAN/lockdep/NMI safety coverage.

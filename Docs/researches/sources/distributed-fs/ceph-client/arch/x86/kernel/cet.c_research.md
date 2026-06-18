# sources/distributed-fs/ceph-client/arch/x86/kernel/cet.c

## Purpose
This file handles x86 Control-flow Enforcement Technology control-protection exceptions (`#CP`) for user shadow stack and kernel IBT.

## Important APIs, Types, and Functions
`enum cp_error_code` names architectural #CP subcodes. `cp_err_string()` formats error codes. User faults are handled by `do_user_cp_fault()`, kernel faults by `do_kernel_cp_fault()`, unexpected cases by `do_unexpected_cp()`, and the IDT entry is `exc_control_protection`. The `ibt=` boot parameter can disable IBT or change missing-ENDBR behavior from fatal to warning.

## Control Flow
The exception entry checks user mode first. User faults require `X86_FEATURE_USER_SHSTK`; the handler reads `MSR_IA32_PL3_SSP`, enables interrupts conditionally, records trap metadata, rate-limits diagnostics, sends `SIGSEGV` with `SEGV_CPERR`, and disables interrupts before return. Kernel faults require `X86_FEATURE_IBT`; ENDBR faults at the IBT selftest site are allowed to continue, other missing ENDBR faults either warn and continue when `ibt=warn` or call `BUG()`.

## State and Persistence
Persistent state is minimal: `ibt_fatal` after init and the ratelimit state. Fault handling mutates the current task's trap metadata and may clear FRED WFE state in `pt_regs`.

## Dependencies and Integration Points
The file depends on trap/IDT infrastructure, CET feature bits, MSR access, signal delivery, ratelimit logging, FRED-aware `pt_regs`, IBT selftests, and global CPU capability setup from boot parameters.

## Risks and Test Signals
Risks include mishandling interrupt state, failing to clear FRED WFE during deliberate or warning-mode ENDBR faults, over-reporting user faults, or treating unsupported #CP causes as normal. Test signals include CET selftests, user shadow-stack SIGSEGV behavior, kernel IBT no-ENDBR test, `ibt=off` and `ibt=warn` boot behavior, and ratelimited fault logs.

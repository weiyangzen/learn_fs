# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_system.h

## Purpose
This header provides kernel/system integration for the wm-FPU-emu: LDT descriptor access, segment descriptor helpers, per-task soft-FPU state macros, and user memory access wrappers.

## Important APIs, Types, and Functions
Important helpers include `FPU_get_ldt_descriptor()`, `seg_get_base()`, `seg_get_limit()`, `seg_get_granularity()`, `seg_expands_down()`, `seg_execute_only()`, and `seg_writable()`. State macros expose `I387`, `FPU_info`, segment/register fields, `FPU_lookahead`, `no_ip_update`, `FPU_rm`, `access_limit`, `partial_status`, `control_word`, `fpu_tag_word`, `registers`, `top`, `instruction_address`, and `operand_address`. Uaccess macros include `FPU_access_ok()`, `FPU_code_access_ok()`, `FPU_get_user()`, and `FPU_put_user()`.

## Control Flow
Descriptor helpers decode base, limit, granularity, and permissions from x86 descriptors. `FPU_get_ldt_descriptor()` conditionally locks the current mm LDT context and returns a descriptor or zero descriptor. Uaccess macros abort math emulation with SIGSEGV when access checks or get/put operations fail.

## State and Persistence
The header maps persistent current-task FPU emulator state but stores no state itself. `FPU_get_ldt_descriptor()` transiently locks the current mm context.

## Dependencies and Integration Points
It depends on scheduler/current task state, mm/LDT context, x86 descriptor definitions, uaccess, and signal abort behavior. It is included throughout the emulator for access to task state and memory.

## Risks and Test Signals
Risks include incorrect descriptor permission/limit logic, user memory aborts from the wrong EIP, and macro side effects. Test signals include segmented addressing tests, LDT-enabled workloads, VM86 paths, user fault injection, and regset consistency.

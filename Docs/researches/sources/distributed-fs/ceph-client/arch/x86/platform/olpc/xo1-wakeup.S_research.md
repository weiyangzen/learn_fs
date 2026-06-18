<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/xo1-wakeup.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/xo1-wakeup.S

## Purpose
Provides low-level 32-bit XO-1 suspend/resume assembly around the OpenFirmware sleep call.

## Important APIs, Types, And Functions
Exports `do_olpc_suspend_lowlevel`. Internal labels save/restore GDT, IDT, LDT, CR0/CR4, callee-saved registers, EFLAGS, and ESP; `wakeup_start` reestablishes page tables and jumps back after firmware wake.

## Control Flow
Suspend calls `save_processor_state`, saves assembly context, stores ESP, calls `xo1_do_sleep(3)`, and on wake enters `wakeup_start`. Wake code clears flags, restores CR3/CR4/CR0, segment registers, descriptor tables, flushes caches/TLB context, restores saved stack/registers, calls `restore_processor_state`, and returns to C.

## State And Persistence
Stores CPU descriptor/control/register state in `.data` symbols across the firmware sleep transition. POST codes are written to CMOS ports for diagnostics.

## Dependencies And Integration Points
Depends on `olpc-xo1-pm.c`, generic x86 `save_processor_state()`/`restore_processor_state()`, initial page tables, and 32-bit segment definitions.

## Risks And Edge Cases
Extremely sensitive to CPU mode, descriptor, and page-table expectations. Any mismatch with firmware resume state can crash before C code runs. It is not generic x86 suspend code.

## Test Signals
Reliable XO-1 suspend/resume with preserved CPU state, diagnostic POST values, and no descriptor/page faults during resume validate the assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/xo1-wakeup.S -->

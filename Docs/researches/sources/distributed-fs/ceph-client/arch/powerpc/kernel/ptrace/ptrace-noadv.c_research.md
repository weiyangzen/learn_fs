# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-noadv.c

## Purpose
`ptrace-noadv.c` provides stepping and data-breakpoint support for PowerPC systems without advanced debug registers.

## Important APIs, Types, And Functions
It exports the same API as `ptrace-adv.c`: stepping helpers, `ppc_gethwdinfo()`, debugreg get/set, `ppc_set_hwdebug()`, and `ppc_del_hwdebug()`. It uses generic hardware breakpoint facilities when `CONFIG_HAVE_HW_BREAKPOINT` is enabled and direct `thread.hw_brk[]` state otherwise.

## Control Flow
Single step and block step toggle `MSR_SE` and `MSR_BE`. Hardware-info reports available watchpoint slots and DAWR/ARCH_31 capabilities. `ptrace_set_debugreg()` maintains the legacy one-DABR interface, translating DABR flags into `arch_hw_breakpoint` state and registering/modifying/unregistering a single perf hardware breakpoint when supported. `ppc_set_hwdebug()` validates a read/write-only breakpoint, translates exact or inclusive range mode into a perf breakpoint length, finds a free slot, registers it, and returns a one-based handle. Without generic breakpoints it stores an exact hardware breakpoint in a free `hw_brk` slot. `ppc_del_hwdebug()` unregisters by handle or clears raw slot state.

## State And Persistence
Persistent task state is in `thread.hw_brk[]` and optionally `thread.ptrace_bps[]` perf events. Stepping state is in `regs->msr` and `TIF_SINGLESTEP`.

## Dependencies And Integration Points
The file integrates with `linux/hw_breakpoint.h`, arch breakpoint translation helpers, `ptrace_triggered`, `ppc_breakpoint_available()`, DAWR feature detection, and the generic ptrace command dispatcher.

## Risks
The legacy DABR ABI accepts low bits as flags and requires the translation bit when nonzero. Range length calculation for inclusive ranges depends on addr ordering and perf semantics. Mixed perf-event and raw `hw_brk` state must stay consistent for deletion and GET_DEBUGREG compatibility.

## Test Signals
Exercise legacy DABR set/clear/get, exact watchpoints, inclusive range watchpoints under perf hardware breakpoint support, unsupported range mode without perf support, slot exhaustion, deletion of empty slots, and stepping behavior.

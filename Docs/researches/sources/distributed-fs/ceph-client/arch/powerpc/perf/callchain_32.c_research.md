
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_32.c

## Purpose

This file implements 32-bit PowerPC user-space perf callchain unwinding, including native 32-bit and compat-on-64-bit signal frame handling.

## Important APIs, Types, And Functions

- Compatibility typedefs map 32-bit signal frame structures when not building `CONFIG_PPC64`.
- `read_user_stack_32()` wraps `__read_user_stack()` for 32-bit words.
- `struct signal_frame_32` and `struct rt_signal_frame_32` describe non-RT and RT signal frame layouts.
- `is_sigreturn_32_address()` and `is_rt_sigreturn_32_address()` detect trampoline addresses either inside the frame or in the VDSO.
- `sane_signal_32_frame()` and `sane_rt_signal_32_frame()` verify saved register pointers in signal frames.
- `signal_frame_32_regs()` identifies a valid signal frame and returns its saved GPR array.
- `perf_callchain_user_32()` walks user frames, handles signal frame restarts, and stores callchain IPs.

## Control Flow

The unwinder starts from `regs->gpr[1]`, `regs->link`, and `perf_arch_instruction_pointer()`. For each frame, it reads the next stack pointer and, after the first level, the saved return address. It checks whether the current frame is a signal frame using `next_ip` or early LR fallback. On signal frames, it reloads NIP/LR/R1 from saved user registers, resets level, emits a user context marker, and continues. Otherwise it stores LR for level zero or the frame return address for later levels.

## State And Persistence

State is local to a sample: stack pointer, LR, next IP, level, and perf callchain entry cursor. It reads user stack and signal frame memory with nofault copies.

## Dependencies And Integration Points

It depends on 32-bit PowerPC signal frame layout, VDSO symbols `sigtramp32` and `sigtramp_rt32`, `PT_NIP`/`PT_LNK`/`PT_R1`, perf callchain storage, and helpers from `callchain.h`.

## Risks And Edge Cases

Signal frame size checks intentionally allow `next_sp < sp` for alternate signal stack transitions. Incorrect VDSO or frame layout assumptions can break unwinding through signal handlers. User memory reads can fail at any point and terminate the unwind safely.

## Test Signals

Use 32-bit user processes, compat tasks on PPC64, signal handlers, RT and non-RT signals, alternate signal stacks, and corrupted stack tests under `perf record -g`.

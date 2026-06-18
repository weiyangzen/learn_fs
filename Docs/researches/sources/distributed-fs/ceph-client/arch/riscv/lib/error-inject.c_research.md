<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/error-inject.c

## Purpose
`error-inject.c` supports function error injection on RISC-V by skipping the probed function body and returning immediately.

## Important APIs, Types, And Functions
`override_function_with_return()` sets the instruction pointer in `pt_regs` to the return address register. It is marked `NOKPROBE_SYMBOL`.

## Control Flow
When error injection triggers at function entry, the helper changes `regs->epc`/instruction pointer to `regs->ra`, causing execution to resume at the caller return site.

## State And Persistence
It mutates only the live trap/register frame. No persistent state is stored.

## Dependencies And Integration Points
It depends on kprobes, Linux error-injection framework, and RISC-V `pt_regs` layout.

## Risks
This must not itself be probed. It assumes the return address register contains a valid call return address and is only safe for functions approved by the error injection framework.

## Test Signals
Function error injection selftests and kprobe tests on RISC-V validate the behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/error-inject.c -->

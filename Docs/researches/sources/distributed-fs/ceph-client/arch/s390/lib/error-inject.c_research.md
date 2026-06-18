# sources/distributed-fs/ceph-client/arch/s390/lib/error-inject.c

## Purpose
Provides the s390 architecture hook used by Linux function error injection to force a probed function to return immediately.

## Important APIs, Types, And Functions
`override_function_with_return(struct pt_regs *regs)` emulates `br 14` by setting the captured PSW address to GPR14, the s390 return address register. It is marked `NOKPROBE_SYMBOL` so kprobes cannot instrument this helper.

## Control Flow And State
The helper mutates only the saved register frame passed by kprobe/error-injection infrastructure. It does not inspect target function state or stack; control flow resumes at the return address when the modified frame is restored.

## Dependencies And Integration
Depends on s390 `pt_regs`, kprobes, and generic `linux/error-injection.h`. It is built only when `CONFIG_FUNCTION_ERROR_INJECTION` is enabled.

## Risks And Test Signals
Risks include wrong return-register assumptions, unsafe probing of the override helper itself, and interactions with nonstandard calling sequences. Signals include function error injection tests, kprobe registration behavior, and fault-injection users that expect immediate function return.

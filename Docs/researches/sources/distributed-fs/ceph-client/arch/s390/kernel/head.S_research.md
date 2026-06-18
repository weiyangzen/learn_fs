# sources/distributed-fs/ceph-client/arch/s390/kernel/head.S

## Purpose
Provides the post-decompressor s390 kernel entry continuation. It sets up the initial task and kernel stack in lowcore, enables early SCLP address adjustment, runs s390 early initialization, and enters the generic kernel.

## Important APIs, Types, And Functions
Defines `startup_continue` in the `__HEAD` section and local data `dw_psw`, a disabled-wait PSW used if `start_kernel()` ever returns.

## Control Flow
`startup_continue` obtains lowcore, stores `init_task` as current, stores the initial stack pointer from `init_thread_union + STACK_INIT_OFFSET`, calls `sclp_early_adjust_va`, calls `startup_init`, then calls `start_kernel`. If control returns, it loads `dw_psw` to enter disabled wait.

## State And Persistence
Initializes lowcore `current_task` and `kernel_stack` fields. No file persistence. The disabled-wait PSW is static boot data.

## Dependencies And Integration Points
Depends on lowcore offsets, init task symbols, SCLP early setup, `startup_init()` from `early.c`, and generic `start_kernel()`. It is the bridge from architecture boot code to common kernel init.

## Risks And Edge Cases
Wrong lowcore offsets or stack pointer setup prevents boot immediately. Returning from `start_kernel()` is treated as fatal. This code must remain free of unsafe instrumentation.

## Test Signals
Signals include successful early boot, initial stack/current task correctness, early SCLP output availability, and disabled-wait behavior only on catastrophic return from `start_kernel()`.

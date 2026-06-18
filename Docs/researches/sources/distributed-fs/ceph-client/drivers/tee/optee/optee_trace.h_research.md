# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_trace.h

## Purpose
`optee_trace.h` defines tracepoints for the raw OP-TEE SMC invocation boundary, allowing developers to observe register arguments before and return registers after calls into secure world.

## Important APIs, Types, And Functions
`TRACE_EVENT(optee_invoke_fn_begin)` records the `optee_rpc_param` pointer and eight 32-bit argument registers. `TRACE_EVENT(optee_invoke_fn_end)` records the same parameter pointer and four return registers from `struct arm_smccc_res`. The trace include path/file footer lets Linux tracepoint generation include this header correctly from `smc_abi.c`.

## Control Flow And State
Tracepoints are passive instrumentation. `smc_abi.c` emits begin/end events around `optee->smc.invoke_fn()` in `optee_smc_do_call_with_arg()`.

## Dependencies And Integration Points
The header depends on Linux tracepoint infrastructure, ARM SMCCC result types, and `optee_private.h` for `struct optee_rpc_param`. The Makefile adds `-I$(src)` for `smc_abi.o` so the trace generator can resolve it.

## Risks
The tracepoint copies raw register values and a kernel pointer into trace buffers; enabling it can expose sensitive call metadata to privileged tracing users. The `BUILD_BUG_ON` checks depend on source structures remaining at least as large as the copied arrays.

## Test Signals
Build with tracing enabled, enable both trace events, run TEE open/invoke calls, and confirm begin/end events pair around secure calls without breaking normal execution.

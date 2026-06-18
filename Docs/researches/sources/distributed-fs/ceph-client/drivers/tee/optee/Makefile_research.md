# sources/distributed-fs/ceph-client/drivers/tee/optee/Makefile

## Purpose
The OP-TEE Makefile defines the module object composition and a compile include path needed by trace generation.

## Important APIs, Types, And Functions
`obj-$(CONFIG_OPTEE) += optee.o` builds the composite OP-TEE object. `optee-objs` includes common core/session code (`core.o`, `call.o`), notification/RPC/supplicant/device support (`notif.o`, `rpc.o`, `supp.o`, `device.o`), protected memory (`protmem.o`), and both transport backends (`smc_abi.o`, `ffa_abi.o`). `CFLAGS_smc_abi.o := -I$(src)` lets the tracing framework find `optee_trace.h` when compiling `smc_abi.o`.

## Control Flow And State
There is no runtime state in this file. It guarantees both SMC and FF-A backend code are linked into the same OP-TEE driver object, with runtime probing deciding which ABI registers successfully.

## Dependencies And Integration Points
The file integrates with Kbuild composite object rules and the Linux trace event header-generation convention used by `CREATE_TRACE_POINTS` in `smc_abi.c`.

## Risks
Backend files are always part of `optee.o`; compile-time dependencies must therefore be guarded internally where optional subsystems are not reachable. Removing the trace include flag can break trace header discovery.

## Test Signals
Run kernel build targets with `CONFIG_OPTEE=m` and `CONFIG_OPTEE=y`, and include a build with tracing enabled to confirm `optee_trace.h` remains discoverable for `smc_abi.o`.

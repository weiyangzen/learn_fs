# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.c

## Purpose
`iris_core.c` initializes and deinitializes the global Iris hardware core. It owns the ordered boot pipeline for shared HFI queues, VPU power, firmware loading/booting, hardware mode switch, system HFI initialization, and response wait.

## Important APIs, Types, And Functions
`iris_core_init()` is the public boot entry point. `iris_core_deinit()` tears down firmware, VPU power, and HFI queues. `iris_wait_for_system_response()` waits on `core->core_init_done` using the platform `hw_response_timeout` and transitions to `IRIS_CORE_ERROR` on timeout.

## Control Flow
Initialization is serialized by `core->lock`. If the core is already initialized, the function exits successfully; if the core is in error, it returns `-EINVAL`. Otherwise it sets `IRIS_CORE_INIT`, initializes HFI queues, powers on the VPU, loads and authenticates firmware, boots firmware, switches hardware mode, sends HFI core init commands, unlocks, and waits for the system response completion. Error labels unwind in reverse order and return the core to `IRIS_CORE_DEINIT`. Deinit resumes runtime PM, locks the core, unloads firmware, powers off VPU, frees queues, marks deinit, unlocks, and drops PM.

## State And Persistence Behavior
Core state moves among `IRIS_CORE_DEINIT`, `IRIS_CORE_INIT`, and `IRIS_CORE_ERROR`. HFI queue memory, SFR memory, firmware PAS state, VPU power state, and the core-init completion are the persistent resources affected. The init path sets `IRIS_CORE_INIT` before the response arrives, so timeout handling is critical.

## Dependencies And Integration Points
The file depends on runtime PM, `iris_firmware`, VPU common functions, HFI queues, HFI common init, and state definitions. HFI response handlers complete `core_init_done`, making this file tightly coupled to Gen1/Gen2 response parsing.

## Risks And Test Signals
Risks include partial init unwind leaks, response timeout races, and incorrect state after failed firmware boot. Test signals include boot success on each supported platform generation, forced failure at each init step, timeout behavior when firmware does not respond, repeated init/deinit cycles, and runtime-PM reference balance.

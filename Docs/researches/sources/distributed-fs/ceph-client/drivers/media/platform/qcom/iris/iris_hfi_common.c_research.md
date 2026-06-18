# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.c

## Purpose
`iris_hfi_common.c` provides generation-independent HFI support: HFI-to-V4L2 color metadata conversion, system HFI initialization sequencing, IRQ handling, and runtime PM suspend/resume around firmware power collapse.

## Important APIs, Types, And Functions
Color helpers translate HFI color primaries, transfer characteristics, and matrix coefficients into V4L2 colorspace/xfer/ycbcr values. `iris_hfi_core_init()` sends system init, image-version query, and interframe power-collapse setup through `core->hfi_ops`. `iris_hfi_isr()` disables IRQ and wakes the threaded handler. `iris_hfi_isr_handler()` clears VPU interrupt state, dispatches `hfi_response_ops->hfi_response_handler()`, and reenables IRQ if the watchdog does not indicate failure. `iris_hfi_pm_suspend()` prepares power collapse, sets remote state false, and powers off; `iris_hfi_pm_resume()` powers on, sets remote state true, boots firmware, switches hwmode, and re-enables IFPC.

## Control Flow
The top-half IRQ is minimal and always returns `IRQ_WAKE_THREAD`. The threaded handler locks the core only for interrupt clear/runtime-PM marking, then unlocks before response parsing. Suspend first asks firmware/VPU to prepare PC; failure returns `-EAGAIN` after marking PM busy. Resume unwinds by suspending hardware state and powering off on failures.

## State And Persistence Behavior
Core state can be affected indirectly by response handlers and watchdog paths. Runtime PM timestamps, hardware remote-state, VPU power, firmware boot state, and IFPC configuration are mutated. Color helpers are pure mapping functions.

## Dependencies And Integration Points
It depends on runtime PM, firmware state calls, VPU common operations, HFI command/response ops, queue response processing, and V4L2 color enums. Both Gen1 and Gen2 install command/response ops consumed here.

## Risks And Test Signals
Risks include IRQ reenable omissions after watchdog/system error, suspend races while queues contain pending work, and color metadata mismaps. Tests should include interrupt-driven response handling, debug queue draining, watchdog/system-error paths, runtime suspend/resume under active and idle sessions, and color metadata round-trips for common HDR/SDR streams.

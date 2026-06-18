# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu3x.c

## Purpose
Implements VPU3/VPU33/VPU35 generation-specific power sequencing and operation tables.

## Important APIs And Functions
- `iris_vpu3x_hw_power_collapsed()` checks wrapper core power status.
- `iris_vpu3_power_off_hardware()` waits for idle VPP pipes, toggles NoC reset request/ack, resets the AHB bridge, and powers off hardware.
- `iris_vpu33_power_off_hardware()` uses an LPI handshake loop before bridge reset and hardware power-off.
- `iris_vpu33_power_off_controller()` sequences controller NoC LPI, debug bridge, clock halt, resets, AON MVP NoC reset, XO reset assertion/deassertion, clock disable, and PM-domain shutdown.
- `iris_vpu35_power_on_hw()` enables hardware power domain and AXI/HW freerun/HW clocks.
- `iris_vpu35_power_off_hw()` reuses VPU33 hardware shutdown plus freerun/AXI clock disable.
- `iris_vpu3_ops`, `iris_vpu33_ops`, and `iris_vpu35_ops` export generation-specific power and frequency function tables.

## Control Flow And Integration Points
Gen2 platform data selects these ops: SM8550/QCS8300 use VPU3, SM8650 uses VPU33, SM8750 uses VPU35. Core init/deinit and runtime PM call the ops through common VPU code. Resource helpers perform clock and PM-domain actions based on platform clock/domain tables.

## State And Persistence Behavior
Mutates hardware registers, reset lines, clocks, PM-domain states, and controller power state. It does not store software state beyond using `iris_core` resource handles.

## Dependencies
Linux iopoll/reset helpers, Iris VPU common helpers, register defines, resource clock/domain helpers, and platform `num_vpp_pipe`/reset/clock/domain tables.

## Risks
- Poll timeouts fall through to disable paths and often return 0 from controller power-off, so hardware handshake failures may be logged but not propagated.
- VPU33 controller shutdown assumes controller reset table and clock reset table are present and ordered for platform.
- LPI handshake loops retry 1000 times; incorrect register behavior can add latency.
- VPU35 clock sequencing requires freerun clocks that only SM8750 tables provide.

## Test Signals
- Runtime PM suspend/resume and open/close loops on SM8550, SM8650, and SM8750.
- Fault injection for readl poll timeouts and reset-control failures.
- Register tracing should show NoC LPI/reset/bridge reset sequences per generation.

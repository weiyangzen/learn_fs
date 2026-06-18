# sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_reg.h

## Purpose
Defines the Allwinner A31 ISP register offsets, bit fields, and packed value helpers used by the sun6i ISP driver. It is a hardware ABI header for the kernel driver, not a userspace ABI.

## Important APIs, Types, And Functions
`SUN6I_ISP_ADDR_VALUE()` converts DMA addresses to the hardware word-address representation. Frontend macros cover source mode, enable/control, interrupts, register load/save addresses, SRAM access, and table/stat buffers. Module and mode macros enable AE, OBC, DPC, BDNF, AWB/WB, LSC, histogram, scaler/output paths, and source inputs. Format constants encode YUV420/YUV422 and RAW Bayer orders. Later blocks define AE window registers, optical black geometry, BDNF thresholds/coefficients, Bayer offsets/gains, WB gains/clipping, main/sub-channel sizes, scaling ratios, output formats, strides, and plane addresses.

## Control Flow
The header has no executable flow. Runtime code composes register writes from these macros during probe/table setup, params configuration, capture configuration, interrupt handling, and buffer address programming.

## State And Persistence
The macros describe volatile MMIO state. Persistent driver state lives elsewhere; register state is reinitialized on runtime resume, stream start, and parameter updates.

## Dependencies And Integration Points
Depends on Linux `BIT()` and `GENMASK()`. Used by sun6i ISP core, params, capture, and proc code to keep field packing consistent across modules.

## Risks And Test Signals
Incorrect masks or shifts can silently corrupt adjacent hardware fields. Address helpers are sensitive to DMA alignment. Test signals are successful stream start/stop, correct image dimensions/stride/plane addresses, parameter buffer updates affecting Bayer/BDNF/WB behavior, interrupt status clearing, and suspend/resume reconfiguration.

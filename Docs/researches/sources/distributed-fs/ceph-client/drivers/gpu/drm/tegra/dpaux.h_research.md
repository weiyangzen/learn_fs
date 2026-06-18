# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.h

## Purpose
`dpaux.h` defines the Tegra DPAUX hardware register offsets and bitfields used by `dpaux.c`. It is a compact register map for AUX transactions, HPD interrupts, pad control, scratch registers, and hybrid AUX/I2C pad modes.

## Important APIs, Types, and Definitions
The header contains no structs or functions. Key definitions include interrupt registers and bits (`DPAUX_INTR_EN_AUX`, `DPAUX_INTR_AUX_DONE`, plug/unplug/IRQ events), data FIFO windows (`DPAUX_DP_AUXDATA_WRITE()` and `DPAUX_DP_AUXDATA_READ()`), address/control/status registers, AUX command encodings for native and I2C requests, address-only and command-length fields, status error and reply masks, HPD timing registers, AUX configuration, hybrid pad control drive/input/mode fields, pad power-down bit, and scratch registers.

## Control Flow Role
`dpaux.c` uses these constants to encode each transaction: write FIFO data, set address and command, trigger the transaction, decode completion status, map reply types, and switch pads between AUX, I2C, and powered-down states. The IRQ handler uses the interrupt bits to distinguish transaction completion from HPD events.

## State and Persistence
The header describes volatile hardware state only. Transaction status, reply type, HPD status, and pad power/mode persist in registers until changed or cleared by the driver.

## Dependencies and Integration Points
It is consumed by the DPAUX platform driver. The command definitions map DRM AUX request types to Tegra-specific control bits, while HPD and pad definitions integrate with DRM connector detection and Linux pinctrl.

## Risks
Incorrect command encoding can turn native AUX reads into I2C operations or mis-handle MOT/address-only transactions. Error mask definitions directly affect whether transactions retry, timeout, or fail with I/O errors. Pad control bit mistakes can break both DP AUX and HDMI DDC because the same hybrid pads are shared.

## Test Signals
Register-level validation comes from successful DPCD reads, EDID I2C-over-AUX reads, HPD status changes, and pad mux transitions. Trace output from `tegra_dpaux_readl/writel` should show status bits being cleared after each transaction and expected hybrid pad mode values.

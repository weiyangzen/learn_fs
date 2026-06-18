# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/smiapp-reg-defs.h

## Purpose
This header is a register and bit-definition catalog for SMIA/SMIA++/MIPI CCS compliant camera sensors. It does not implement behavior; it standardizes typed CCI register identifiers used by the CCS camera driver stack. The macros encode register width through `CCI_REG8`, `CCI_REG16`, and `CCI_REG32`, with a few floating-point capability registers carrying `CCS_FL_FLOAT_IREAL`.

## Important APIs, Types, And Constants
The primary API is the `SMIAPP_REG_*` macro namespace. Names encode width and semantic purpose, such as model identity, frame format descriptors, gain controls, streaming mode, CSI-2 format/lane setup, integration timing, PLL dividers, crop/scaler geometry, binning, data-transfer interfaces, defect correction, EDOF, flash, actuator, and bracketing LUT capability registers. Important bit definitions include image orientation flip bits, data-transfer interface control/status bits, reset, flash capability bits, CSI signaling modes, DPHY modes, compression modes, stream/standby mode values, scaler/crop/binning capability values, Bayer pixel-order constants, and frame-format descriptor masks/shifts.

## Control Flow
There is no executable control flow. The only dependency behavior is compile-time substitution of register constants into code that performs CCI reads and writes. Parameterized macros such as `SMIAPP_REG_U16_FRAME_FORMAT_DESCRIPTOR_2(n)` and `SMIAPP_REG_U8_BINNING_TYPE_n(n)` derive contiguous table addresses from an index.

## State And Persistence
The file holds no runtime state. Persistent effects occur only when users of these macros write sensor registers, for example switching `SMIAPP_MODE_SELECT_STREAMING`, changing crop/scaler values, or issuing `SMIAPP_SOFTWARE_RESET`.

## Dependencies And Integration Points
It depends on `<linux/bits.h>` for `BIT()` and `<media/v4l2-cci.h>` for typed CCI register encoding. Integration is with the CCS/SMIA camera sensor driver and any helper code that interprets MIPI CCS capability/register layouts.

## Risks
Risks are specification drift and address/width mismatch: a wrong width macro can make CCI access corrupt adjacent registers or fail reads. Indexed macros rely on callers honoring the documented ranges. The long flat list is hard to audit manually, especially for adjacent table/register ranges.

## Test Signals
Useful validation is compile coverage from CCS drivers, sensor probe tests that read identity and capability registers, runtime streaming tests that program mode/crop/CSI registers, and static checks comparing macro addresses to the CCS specification.

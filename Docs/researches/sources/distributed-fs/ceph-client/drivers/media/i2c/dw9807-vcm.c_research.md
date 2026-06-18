# sources/distributed-fs/ceph-client/drivers/media/i2c/dw9807-vcm.c

## Purpose
`dw9807-vcm.c` is a V4L2 lens actuator driver for the Dongwoon DW9807 VCM. It exposes absolute focus control, polls actuator busy status before DAC writes, and ramps lens movement during runtime/system PM transitions.

## Important APIs, Types, and Functions
`struct dw9807_device` stores the V4L2 control handler, subdevice, and cached current focus. `dw9807_i2c_check()` reads the status register. `dw9807_set_dac()` polls status with `readx_poll_timeout()` until the device is not busy, then writes MSB/LSB focus bytes starting at `DW9807_MSB_ADDR`. `dw9807_set_ctrl()` caches and writes focus. PM callbacks write control register power-down/power-on values and ramp the DAC in 16-step increments.

## Control Flow
Probe allocates state, initializes the V4L2 I2C subdev and focus control, creates a zero-pad `MEDIA_ENT_F_LENS` entity, registers the async subdevice, and enables runtime PM. Open resumes the device and close releases it. Focus changes synchronously poll the status register before I2C write. Suspend ramps focus down to zero and writes CTL powerdown; resume writes CTL power-on and ramps back toward the cached focus.

## State and Persistence
`current_val` is the only remembered target across PM transitions. There are no regulators in this driver; power is controlled by the chip CTL register and any board-level dependencies outside this file. Hardware position is rebuilt by ramping after resume.

## Dependencies and Integration Points
The driver depends on raw I2C transfer helpers, `readx_poll_timeout()`, runtime PM, V4L2 controls/subdev/media entity support, and OF compatibles `dongwoon,dw9807-vcm` plus legacy `dongwoon,dw9807`.

## Risks and Edge Cases
The status poll treats `val <= 0` as ready; negative I2C errors are handled after polling, but the condition is unusual and should be tested under bus failure. There is no regulator or GPIO sequencing, so platform firmware must guarantee electrical power. The legacy compatible is retained only for old firmware and should not be used in new DTs.

## Test Signals
Check busy-poll behavior, focus range 0-1023, three-byte DAC write encoding, open/close runtime PM, suspend powerdown register write after ramp-to-zero, resume power-on register write before ramp-to-target, behavior with simulated I2C errors, and matching of both current and legacy OF compatibles.

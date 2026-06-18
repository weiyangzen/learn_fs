# sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-core.c

## Purpose
This is the shared MFD core for the Cirrus Logic CS40L50 haptic device. It owns common register access policy, regulator/reset sequencing, DSP firmware bring-up, DSP command queue helpers, IRQ demultiplexing, runtime hibernate control, and creation of the `cs40l50-codec` and `cs40l50-vibra` child devices. I2C and SPI wrappers allocate the `struct cs40l50` and then delegate here.

## Important APIs, types, and functions
`cs40l50_regmap` is exported for bus drivers and configures 32-bit big-endian register/value access with 4-byte register stride. `cs40l50_probe()` and `cs40l50_remove()` are exported entry points for the transport drivers. `cs40l50_dsp_write()` is exported as the common DSP queue command helper; it retries writes that may fail while the device is hibernating, then polls the queue register until the firmware clears it as an ACK. `cs40l50_pm_ops` exposes runtime suspend/resume hooks to bus drivers.

The internal flow is centered on `cs40l50_dsp_init()`, `cs40l50_reset_dsp()`, `cs40l50_request_firmware()`, and `cs40l50_dsp_bringup()`. The DSP is configured as a Halo core with packed PM/XM/YM and unpacked 24-bit memory regions. `cs40l50_wseq_init()` locates firmware controls for standby, active, and power-on write sequences. `cs40l50_dsp_config()` writes internal VAMP and IRQ mask overrides to both hardware and the power-on write sequence so settings survive firmware-managed power transitions. `cs40l50_dsp_post_run()` performs post-firmware configuration and adds the MFD children.

IRQ handling uses `cs40l50_irq_chip`, `cs40l50_reg_irqs`, and `cs40l50_irqs`. `cs40l50_irq_init()` creates a regmap IRQ chip and requests one threaded handler per virtual IRQ. The DSP queue IRQ uses `cs40l50_dsp_queue()`; all hardware error IRQs share `cs40l50_hw_err()`.

## Control flow
Probe initializes the mutex, obtains an optional reset GPIO, enables `vdd-io`, satisfies reset and control-port timing delays, releases reset, verifies device/revision, initializes the DSP object, configures runtime PM, installs IRQ handling, asynchronously requests `cs40l50.wmfw`, and drops the runtime PM reference for autosuspend. Firmware loading is two-stage: the WMFW callback stores the firmware pointer and requests optional wavetable `cs40l50.bin`; the wavetable callback stores the optional pointer, resets/powers/runs the DSP, reads `CS40L50_NUM_WAVES`, registers devm DSP stop/power-down cleanup, and releases both firmware objects.

DSP reset is serialized by `cs40l50->lock`: stop running firmware, power down booted firmware, send shutdown, power up with firmware/bin blobs, send system reset, prevent hibernation, and run the DSP. Hardware error interrupts also take the same mutex before logging the matching error name and writing the global error release set/clear sequence. The DSP queue handler loops until read and write pointers match, logs each payload, wraps the read pointer at queue end, and writes the new read pointer back.

## State and persistence behavior
Persistent driver state lives in `struct cs40l50`: regmap, IRQ, reset GPIO, firmware pointers during async bring-up, DSP object, write sequences, IRQ data, device/revision, and a mutex. Hardware state is restored partly through firmware write sequences: internal VAMP config and IRQ mask overrides are written into the power-on sequence as well as current registers. Runtime suspend writes `CS40L50_ALLOW_HIBER`; runtime resume uses the ACK-polled DSP helper to send `CS40L50_PREVENT_HIBER`. Remove simply asserts reset; devm actions unwind DSP and IRQ resources.

## Dependencies and integration points
The file depends on Linux MFD, regmap IRQ, regulator, GPIO, runtime PM, firmware loading, and the Cirrus `cs_dsp`/WMFW framework. It exports common symbols to `cs40l50-i2c.c`, `cs40l50-spi.c`, and child drivers under the input/sound stacks. Firmware names are `cs40l50.wmfw` and optional `cs40l50.bin`; the child devices rely on successful `cs_dsp` post-run.

## Risks and edge cases
Firmware bring-up is asynchronous; child devices are unavailable until DSP post-run succeeds. If `request_firmware_nowait()` succeeds but firmware contents are missing or invalid, probe can still return success while later bring-up logs errors. `cs40l50_dsp_bringup()` assigns `cs40l50->bin` to a possibly NULL optional wavetable and always releases it, which is valid for `release_firmware(NULL)` but important for audit. DSP queue handling trusts firmware-provided read pointers and only wraps after incrementing past `CS40L50_DSP_QUEUE_END`; bad firmware pointers would turn into arbitrary regmap reads. The static `cs40l50_irqs` table stores virq values globally, so multiple device instances would share the last registered virq values for error-name lookup. Runtime suspend writes the queue directly rather than through `cs40l50_dsp_write()`, so failures caused by an already hibernating device are propagated without retry.

## Test signals
Useful tests include probe deferral for missing regulators/GPIO/IRQ, invalid device ID and pre-B0 revision rejection, asynchronous firmware absence and optional wavetable absence, successful child-device creation after DSP post-run, IRQ handler behavior for DSP queue wrap and hardware error release, runtime suspend/resume hibernate commands, and remove/reset cleanup. KUnit or fault-injection tests around regmap failures in `cs40l50_reset_dsp()` and IRQ setup would exercise most error exits.

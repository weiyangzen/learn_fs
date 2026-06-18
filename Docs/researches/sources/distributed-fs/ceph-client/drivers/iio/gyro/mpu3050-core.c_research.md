# sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-core.c

## Purpose
Common IIO core for the InvenSense MPU-3050 gyroscope, providing raw temp/axis reads, calibration bias, scale, sample frequency, mount matrix, triggered buffers, FIFO-backed hardware IRQ trigger, regulators, OTP identity readout, and runtime PM.

## Important APIs, Types, And Functions
Uses `struct mpu3050` from `mpu3050.h`. Key functions include frequency and sampling setup, 8 kHz samplerate helper, raw read/write handlers, trigger handler with FIFO drain, buffer setup ops, mount matrix extension, `mpu3050_read_mem`, hardware init, power up/down, IRQ top/thread handlers, trigger state/probe, common probe/remove, and runtime PM callbacks.

## Control Flow
Common probe initializes defaults, reads mount matrix, gets regulators, powers up, validates chip and product IDs, reads OTP memory into randomness/logs, sets up triggered buffer, optionally registers IRQ trigger, enables runtime PM autosuspend, and registers IIO. Hardware trigger enable powers the device, resets/enables FIFO, starts sampling, clears IRQ, and enables raw-ready interrupts.

## State And Persistence
Software caches fullscale, low-pass filter, divisor, calibration offsets, trigger flags, IRQ polarity/latch/open-drain, FIFO footer state, hardware timestamp, regulators, and optional I2C mux pointer. Hardware state includes power, PLL, offset registers, DLPF/fullscale/sync, sample divider, FIFO, interrupt config, OTP memory, and sleep bit.

## Dependencies And Integration Points
Depends on regmap from transport, regulators `vdd`/`vlogic`, IIO triggered buffers/triggers, runtime PM, IRQ trigger properties, firmware mount matrix, and the I2C transport/mux layer.

## Risks
FIFO handling is complex and timestamp semantics intentionally fall back to zero for drained FIFO entries. Runtime PM and trigger enable paths must balance power references. Calibration and scale writes update cached state and are applied on next sampling start, not immediately. The source contains duplicated string/write_raw lines in read/info paths, worth build-checking.

## Test Signals
Probe chip/product IDs, verify OTP log, read/write calibration, scale, and sample frequency, raw-read temp/axes, enable external-trigger and hardware IRQ-trigger buffers, induce FIFO overflow, test IRQ polarity modes, and run runtime suspend/resume/remove.

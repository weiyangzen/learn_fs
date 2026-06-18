# sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxfast.c

## Purpose
This COMEDI USB driver supports USB-DUX-FAST devices, a high-speed analog-input-only board. It programs FX2/GPIF waveform descriptors for selected channel patterns and streams samples from a bulk IN endpoint to the COMEDI async buffer.

## Important APIs, Types, And Functions
`struct usbduxfast_private` holds one bulk URB, the command descriptor buffer `duxbuf`, input buffer `inbuf`, an async running flag, an initial packet ignore counter, and a mutex. `usbduxfast_send_cmd()` sends the descriptor buffer to endpoint 4. `usbduxfast_cmd_data()` fills one GPIF state descriptor. Streaming is implemented by `usbduxfast_ai_cmdtest()`, `usbduxfast_ai_check_chanlist()`, `usbduxfast_ai_cmd()`, `usbduxfast_ai_inttrig()`, `usbduxfast_ai_cancel()`, `usbduxfast_submit_urb()`, `usbduxfast_ai_interrupt()`, and `usbduxfast_ai_handle_urb()`. Single reads are handled by `usbduxfast_ai_insn_read()`. Firmware upload uses `usbduxfast_upload_firmware()`.

## Control Flow
Attach requires USB high speed, switches to alternate setting 1, allocates the URB and buffers, loads `usbduxfast_firmware.bin`, and registers one AI subdevice. `cmdtest` accepts `TRIG_NOW`, `TRIG_EXT`, or `TRIG_INT` starts, `TRIG_FOLLOW` scan begin, timer-based convert timing, and count/none stop. It restricts channel lists to 1, 2, 3, or 16 consecutive channels and requires matching gains for lists longer than three channels.

`usbduxfast_ai_cmd()` converts `convert_arg` into 30 MHz GPIF steps, fills waveform descriptors according to channel count and trigger mode, sends them to firmware, then starts the bulk URB immediately for `TRIG_NOW`/`TRIG_EXT` or installs `inttrig`. The completion path ignores the first four packets to flush stale quad-buffered device data, writes the remaining samples to COMEDI, checks stop count, resubmits, and reports events. Single reads program a fixed descriptor sequence, discard initial packets, then collect the requested channel from 16-channel-aligned packets.

## State And Persistence
`ai_cmd_running` protects async streaming from single reads and repeated starts. `ignore` is reset for each command and decremented in completions. Hardware state consists mainly of GPIF command descriptors in firmware. There is no readback or persistent calibration state in the driver.

## Dependencies And Integration Points
The driver depends on COMEDI USB support, firmware loading, Linux USB bulk URBs, and USB IDs `0x13d8:0x0010`/`0x13d8:0x0011`. It exposes one `COMEDI_SUBD_AI` with 16 channels, two bipolar ranges, 12-bit-plus-overflow maxdata, async command support, and single instruction reads.

## Risks And Edge Cases
The channel list restrictions are strict and hardware-specific. `usbduxfast_ai_inttrig()` returns `1` on successful trigger rather than `0`, which is unusual but existing behavior. Timing conversion rounds through integer `steps`; `cmdtest` adjusts invalid values but can be sensitive to nanosecond-to-step rounding. Bulk transfer errors and corrupted packet lengths abort with COMEDI error events or `-EINVAL`. Allocation failures after partial attach need normal driver-core cleanup coverage.

## Test Signals
Signals include attach rejection on non-high-speed USB, successful firmware load and alternate setting switch, `cmdtest` acceptance only for legal channel lists and timing, initial packet discard before samples are reported, no bulk URB resubmit errors, and correct single-read channel extraction from 16-channel packets.

# sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxsigma.c

## Purpose
This COMEDI USB driver supports USB-DUX-SIGMA devices. It exposes 24-bit analog input, 8-bit analog output, 24-bit digital I/O, and high-speed-only PWM. It is similar to `usbdux.c` but uses different firmware commands, larger AI samples, sigma ADC configuration bytes, and a startup status/health read.

## Important APIs, Types, And Functions
`struct usbduxsigma_private` tracks AI/AO URB arrays, a PWM URB, command/response buffers, high-speed mode, running flags, timers, intervals, and a mutex. AI operations are implemented by `usbduxsigma_ai_cmdtest()`, `usbduxsigma_ai_cmd()`, `usbduxsigma_ai_inttrig()`, `usbduxsigma_ai_cancel()`, `usbduxsigma_ai_insn_read()`, `usbduxsigma_ai_urb_complete()`, and `usbduxsigma_ai_handle_urb()`. AO operations are implemented by matching `usbduxsigma_ao_*` routines. `usbduxsigma_dio_insn_bits()` and `usbduxsigma_dio_insn_config()` manage 24 DIO lines. PWM operations are implemented by `usbduxsigma_pwm_*`. `usbduxsigma_getstatusinfo()` reads ADC system channels for health/status. Attach, firmware upload, and detach are handled by `usbduxsigma_auto_attach()`, `usbduxsigma_firmware_upload()`, and `usbduxsigma_detach()`.

## Control Flow
Attach determines full/high-speed mode, allocates buffers and URBs, selects alternate setting 3, loads `usbduxsigma_firmware.bin`, registers three or four subdevices, sets default PWM period when present, and reads ADC zero status to confirm communication. AI `cmdtest` chooses an interval from channel count, enforces USB frame or microframe minimum scan periods, and rounds scan timing down to supported units. AI command builds ADC mux bitmasks for selected channels, sends an AD command to firmware, computes a timer, and submits URBs now or later via internal trigger. Completions copy big-endian 32-bit samples, strip status byte, offset-munge 24-bit values, write samples to COMEDI, and resubmit.

AO command mode uses one millisecond scan timing, fills isochronous output packets from the COMEDI async buffer, and updates readback. Single AO writes send one channel/value command at a time. DIO writes pack direction and state across three bytes and reads state back from firmware. PWM uses a high-speed bulk URB pattern buffer and command-controlled firmware mode.

## State And Persistence
The private running flags gate concurrent operations. AI and AO timer/counter fields downsample URB completions to requested scan periods. DIO direction and state live in the COMEDI subdevice and are synchronized on `insn_bits`. AO readback persists last written values. PWM pattern bytes persist in the URB transfer buffer until overwritten or stopped.

## Dependencies And Integration Points
The driver depends on COMEDI USB helpers, Linux USB isochronous/bulk/control APIs, unaligned big-endian loads, and firmware `usbduxsigma_firmware.bin`. USB IDs are `0x13d8:0x0020`, `0x13d8:0x0021`, and `0x13d8:0x0022`. It integrates with COMEDI through AI/AO/DIO/PWM subdevice callbacks and firmware loading through `MODULE_FIRMWARE`.

## Risks And Edge Cases
The file contains a misspelled helper name `usbbuxsigma_send_cmd()`, which is harmless internally but easy to misread. `usbduxsigma_ao_cmdtest()` calls `mutex_unlock(&devpriv->mut)` on an early validation error despite not locking the mutex in that function; this is a high-risk bug signal if that path is reachable. Several partial allocation paths return errors without local unwind. USB sample format handling depends on a leading DIO/status word and 24-bit ADC values inside 32-bit big-endian fields. PWM control lacks explicit mutex use in several paths compared with AI/AO.

## Test Signals
Key signals include successful firmware upload, successful ADC zero status read, valid `cmdtest` timing rounding, correct 24-bit sample offset munging, DIO state round trips across three bytes, AO readback updates, PWM start/stop status, and no URB resubmit failures during disconnect/cancel stress.

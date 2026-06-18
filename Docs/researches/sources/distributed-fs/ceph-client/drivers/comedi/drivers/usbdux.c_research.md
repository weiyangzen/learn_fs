# sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbdux.c

## Purpose
This is the COMEDI USB low-level driver for Stirling/ITL USB-DUX devices. It exposes analog input, analog output, digital I/O, counter, and, on high-speed devices, PWM subdevices. Streaming AI/AO uses isochronous URBs, while single-shot instructions, DIO, counters, firmware upload, and PWM control use bulk or control transfers to device firmware.

## Important APIs, Types, And Functions
`struct usbdux_private` stores URB arrays, firmware command buffers, single-instruction buffers, high-speed capability, running flags for AI/AO/PWM, scan timers/counters, and a mutex serializing command paths. Range tables define 12-bit AI and AO voltage ranges. AI entry points are `usbdux_ai_cmdtest()`, `usbdux_ai_cmd()`, `usbdux_ai_inttrig()`, `usbdux_ai_cancel()`, and `usbdux_ai_insn_read()`. AO equivalents are `usbdux_ao_cmdtest()`, `usbdux_ao_cmd()`, `usbdux_ao_inttrig()`, `usbdux_ao_cancel()`, `usbdux_ao_insn_write()`, and readback via `usbdux_ao_insn_read()`.

`send_dux_commands()` and `receive_dux_commands()` are the firmware command channel helpers. `usbdux_dio_insn_bits()` and `usbdux_dio_insn_config()` handle 8-bit DIO. `usbdux_counter_read()`, `usbdux_counter_write()`, and `usbdux_counter_config()` expose firmware timers. PWM support is handled by `usbdux_pwm_period()`, `usbdux_pwm_start()`, `usbdux_pwm_cancel()`, `usbdux_pwm_pattern()`, `usbdux_pwm_write()`, and `usbdux_pwm_config()`. Attachment is handled by `usbdux_auto_attach()`, USB probe by `usbdux_usb_probe()`, and cleanup by `usbdux_detach()`.

## Control Flow
Attach allocates private state, determines high-speed mode, allocates URBs and buffers, sets USB alternate setting 3, loads `usbdux_firmware.bin`, and registers four or five COMEDI subdevices. AI command validation constrains trigger sources and scan periods to USB frame or microframe rates. AI command setup writes the channel list to firmware, computes interval/timer counters, then either submits all AI URBs immediately for `TRIG_NOW` or installs `inttrig`. Completion copies ISO data, performs bipolar offset munging, writes samples to the COMEDI async buffer, checks stop count, resubmits the URB, and manually calls `comedi_event()`.

AO streaming mirrors AI: command setup computes a millisecond timer, completion pulls samples from the COMEDI buffer, formats channel/value triplets, updates readback, resubmits, and reports underflow or EOA events. Single AI/AO and DIO paths take the private mutex, send a command, and optionally wait for the matching response. PWM starts firmware mode, repeatedly resubmits a bulk URB containing a generated duty-cycle pattern, and stops on cancel or URB error.

## State And Persistence
State is in `usbdux_private` and COMEDI subdevice state. `ai_cmd_running`, `ao_cmd_running`, and `pwm_cmd_running` gate concurrent command starts and completion resubmission. AO readback persists last written values in `s->readback`. DIO direction/state lives in the COMEDI subdevice and is pushed to firmware during `insn_bits`, not during `insn_config`. Firmware is uploaded at attach and device memory/buffers are freed at detach.

## Dependencies And Integration Points
The driver depends on COMEDI USB helpers (`comedi_usb_auto_config`, `module_comedi_usb_driver`, `comedi_load_firmware`), COMEDI async buffer helpers, Linux USB URB APIs, and firmware file `usbdux_firmware.bin`. USB IDs are `0x13d8:0x0001` and `0x13d8:0x0002`. It integrates with the COMEDI core through subdevice callbacks and with Linux firmware loading through `MODULE_FIRMWARE`.

## Risks And Edge Cases
Streaming completion cannot call `comedi_handle_events()` because cancel would unlink the currently executing URB, so manual event/cancel handling is delicate. Several error paths during buffer allocation return without locally freeing partially allocated resources, relying on later detach or core cleanup. Command/response matching retries only a fixed number of times. High-speed timing depends on power-of-two channel intervals. PWM period limits are encoded through FX2 delay math and unsupported values return `-EAGAIN`.

## Test Signals
Behavioral signals include successful firmware load, USB alternate setting selection, valid `cmdtest` normalization of scan periods, no URB resubmit errors, correct COMEDI buffer samples with bipolar offset munging, AO readback matching writes, DIO bit reads after command round trips, and clean cancellation/unlink behavior under disconnect.

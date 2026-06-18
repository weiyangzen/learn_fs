# sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_usb.c

## Purpose
`pcwd_usb.c` drives the Berkshire USB-PC Watchdog HID device. It sends six-byte HID reports for watchdog commands, receives interrupt-in responses, and exposes watchdog and temperature miscdevices.

## Important APIs, types, and functions
`struct usb_pcwd_private` stores USB device/interface, interrupt URB/buffer, last command response, existence flag, and mutex. Important functions include `usb_pcwd_intr_done`, `usb_pcwd_send_command`, start/stop/keepalive/heartbeat/temperature/timeleft helpers, file operations, reboot notifier, `usb_pcwd_probe`, `usb_pcwd_disconnect`, and `usb_pcwd_delete`.

## Control flow
Probe accepts only the supported USB VID/PID HID interface with an interrupt-IN endpoint, allocates the private object, coherent interrupt buffer, and URB, submits the URB, marks the device existing, stops the watchdog, reads firmware and DIP switches, chooses heartbeat, registers reboot notifier, temperature miscdevice, and watchdog miscdevice, then stores interface data. Commands send HID `SET_REPORT`, wait up to 250 ms for the interrupt callback to set `cmd_received`, and copy response bytes. Open starts and keepalives; writes scan for magic `V`; release stops only after magic close. Disconnect stops unless nowayout, marks the device gone, deregisters devices/notifier, frees URB/buffer, and decrements the singleton count.

## State and persistence
Runtime state is global/single-device plus per-USB object state. Hardware stores timeout, watchdog enable, switch, firmware, and temperature state. There is no bootstatus reporting.

## Dependencies and integration points
It integrates USB core, HID report protocol constants, interrupt URBs, coherent DMA buffers, reboot notifier, miscdevice ABI, watchdog ioctl ABI, and module parameters `heartbeat` and `nowayout`.

## Risks and test signals
Risks include global `usb_pcwd_device` dereference after disconnect, races around `is_active` and disconnect despite a disconnect mutex only in disconnect path, command response matching only command byte, allocation via `kzalloc_obj`, and watchdog behavior on USB removal. Test signals include HID class/endpoint validation, URB resubmission errors, command timeout, disconnect while open, magic close, heartbeat from DIP switch, temperature/timeleft ioctls, and reboot notifier.

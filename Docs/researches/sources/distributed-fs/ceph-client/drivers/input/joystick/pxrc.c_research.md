# sources/distributed-fs/ceph-client/drivers/input/joystick/pxrc.c

Purpose: USB input driver for PhoenixRC Flight Controller Adapter, exposing adapter channel data as ABS axes and one button.

Important APIs/types/functions: `struct pxrc` stores input, USB interface, interrupt URB, PM mutex, open flag, and phys path. `pxrc_probe()` finds the interrupt endpoint, allocates state, buffer, URB, input device, fills the URB, and registers input. `pxrc_usb_irq()` decodes 8-byte interrupt reports. `pxrc_open()` submits the URB; `pxrc_close()` kills it. Suspend/resume/reset callbacks coordinate URB lifetime under `pm_mutex`.

Control flow: Probe binds to VID/PID 1781:0898, locates the endpoint, prepares an interrupt-in URB, configures ABS ranges 0..255, and registers input. Opening the input submits the URB. Each successful URB completion reports axes/buttons and resubmits. Suspend/reset stop the URB if open and resume/post-reset resubmit.

State and persistence: Per-interface state tracks open status and URB. Buffer and input are devm-managed; URB is freed through a devm action. No persistent storage.

Dependencies and integration points: USB core, USB input ID helpers, input core, mutex guard helpers, PM/reset USB driver callbacks.

Risks: `pxrc_disconnect()` is empty because resources are devm-managed; correctness depends on input unregister/devres ordering during disconnect. Reports with `actual_length != 8` are ignored but still resubmitted. Open maps any submit failure to `-EIO`, losing specific errno.

Test signals: Correct VID/PID binding; endpoint missing path; 8-byte report mapping; short report ignore; suspend/resume/reset while open and closed; unplug during active URB.

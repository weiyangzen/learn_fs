# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-core.c

Purpose: generic USB HID transport driver. It binds USB HID interfaces to Linux HID devices, parses USB HID descriptors, manages interrupt/control URBs, queues report transfers, handles I/O errors/reset/PM, and registers the `usbhid` USB driver.

Important APIs: low-level HID driver callbacks include parse/start/stop/open/close/power/request/wait/raw_request/output_report/idle/may_wakeup. USB callbacks include probe/disconnect/suspend/resume/reset paths. Exported helpers include `hid_is_usb()` and `usbhid_find_interface()`. Module parameters tune mouse/joystick/keyboard poll intervals, LED autosuspend behavior, and boot quirks.

Control flow: probe requires an interrupt IN endpoint, allocates a HID device and `usbhid_device`, then calls `hid_add_device()`. Parse retrieves class/report descriptors and applies quirks. Start allocates coherent buffers and URBs, discovers interrupt endpoints, sets up control URB, handles always-poll and boot-keyboard LED/wakeup behavior. Open enables polling and remote wake; input URB completions feed `hid_safe_input_report()` and resubmit. Output/control reports are queued in FIFOs, submitted asynchronously with autosuspend refs, and advanced by completion callbacks. Error handling backs off, clears halts, or queues reset work.

State and persistence: `struct usbhid_device` stores URBs, buffers, queue heads/tails, lock/mutex, waitqueue, flags in `iofl`, retry timer/work, last transfer timestamps, interface and HID pointers. USB device/interface PM state is updated via autosuspend references and wakeup flags.

Dependencies and integration: depends on USB core, HID core, hidraw/hiddev, input, PID force feedback, workqueues, timers, and quirk infrastructure. It is the canonical USB transport below generic HID drivers.

Risks: concurrency is high: interrupt completions, spinlocked queues, autosuspend, reset work, timers, and disconnect paths all interact. Queue timeout recovery intentionally drops locks around URB unlink. Report descriptor changes across reset force rebind. Autosuspend rejects when LEDs/keys/queues/reset are active unless `ignoreled` permits.

Test signals: USB HID device enumeration, descriptor parse failures, continuous input, output/control report queueing, autosuspend/resume with pressed keys and LEDs, stall/reset recovery, disconnect races, hiddev/PID optional paths, and module quirk parameter parsing.

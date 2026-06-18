# sources/distributed-fs/ceph-client/drivers/input/touchscreen/usbtouchscreen.c

## Purpose
`usbtouchscreen.c` is a USB input driver supporting many legacy single-touch USB touchscreen protocols. It maps USB IDs to per-device packet parsers and initializers, then uses a common URB pipeline to report `BTN_TOUCH`, coordinates, and optional pressure.

## Important APIs, Types, And Functions
`struct usbtouch_device_info` describes coordinate ranges, report size, packet-length parser, data parser, init/exit hooks, and whether IRQ URBs run even when the input device is closed. `struct usbtouch_usb` stores DMA buffers, URB, input device, PM mutex, packet buffer, parser state, and current decoded sample. Device-specific functions decode eGalax, EasyTouch, PanJit, 3M/MicroTouch, ITM, eTurbo, Gunze, DMC, IRTOUCH, ET&T, IdealTEK, General Touch, GoTop, JASTEC, Zytronic, Nexio, Elo, and E2I protocols.

## Control Flow
Probe ignores HID-capable devices assigned to usbhid, finds interrupt or bulk IN endpoint, allocates coherent URB buffers, installs single or multipacket processing, runs optional allocation/init hooks, registers input, and optionally starts always-on URBs. `usbtouch_irq()` decodes successful URBs and resubmits. Open gets runtime PM and starts IO; close kills URBs when not always-on and drops remote wakeup. Suspend kills the URB, resume restarts when needed, and reset-resume reruns device init.

## State And Persistence
State includes input open status, runtime PM wakeup needs, multipacket buffer length, decoded X/Y/touch/pressure, and device-specific private data such as firmware revision or Nexio ACK URB. Module parameters `swap_xy` and `hwcalib_xy` alter reporting globally at runtime. No nonvolatile device storage is changed.

## Dependencies And Integration Points
It integrates USB core, input core, runtime autosuspend, USB control/bulk/interrupt messaging, optional sysfs firmware revision for 3M devices, and Kconfig-selected protocol blocks.

## Risks
Many protocol parsers trust packet sizes selected by device info; malformed devices can exercise edge cases in multipacket buffering. Always-on IRQ devices consume bandwidth and require careful disconnect/PM cleanup. Module-global axis/calibration parameters affect every bound device. Some init paths use vendor control transfers with legacy timing expectations.

## Test Signals
Test every enabled USB ID path, endpoint fallback from interrupt to bulk, multipacket framing and partial packets, open/close PM races, suspend/resume/reset-resume, disconnect during active URB, pressure reporting, axis swap/hw calibration parameters, Nexio ACK handling, and 3M firmware sysfs visibility.

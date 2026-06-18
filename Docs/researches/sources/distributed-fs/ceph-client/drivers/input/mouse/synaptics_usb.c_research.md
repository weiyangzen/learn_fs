<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_usb.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_usb.c

## Purpose
`synaptics_usb.c` supports USB Synaptics touchpads, sticks, touchscreens, cPads, and composite devices. It selects an interrupt endpoint, parses eight-byte reports, and maps them into Linux input absolute, relative, button, and pressure events.

## Important APIs, Types, and Functions
`struct synusb` holds USB device/interface pointers, an interrupt URB, coherent DMA buffer, PM mutex, open state, input device, names, and device flags. Reporting functions are `synusb_report_buttons()`, `synusb_report_stick()`, and `synusb_report_touchpad()`. Lifecycle entry points are `synusb_probe()`, `synusb_disconnect()`, `synusb_open()`, `synusb_close()`, suspend/resume/reset hooks, and the URB completion handler `synusb_irq()`.

## Control Flow
Probe switches to alternate setting 1, finds an interrupt-in endpoint, allocates an input device and URB, fills the URB with the coherent report buffer, builds a name/phys path, assigns capabilities based on device flags, optionally starts I/O for always-on devices, and registers input. Open uses USB autosuspend PM, submits the URB, and enables remote wakeup. Each successful URB completion reports either stick relative motion or touchpad absolute position/tool data, then resubmits the URB. Suspend, close, and pre-reset kill the URB; resume/post-reset resubmit when open or always-on.

## State and Persistence
State is per USB interface and lasts until disconnect. `is_open` and `needs_remote_wakeup` are protected by `pm_mutex` around open/suspend/reset races. There is no persistent configuration; input capabilities are derived from the USB ID table and interface number for composite devices.

## Dependencies and Integration Points
The driver integrates with USB core, USB autosuspend, input core, USB input ID helpers, and module USB driver registration. The ID table maps Synaptics product IDs to flags such as `SYNUSB_TOUCHPAD`, `SYNUSB_STICK`, `SYNUSB_TOUCHSCREEN`, `SYNUSB_AUXDISPLAY`, `SYNUSB_COMBO`, and `SYNUSB_IO_ALWAYS`.

## Risks and Edge Cases
Alternate setting selection uses `min(intf->num_altsetting, 1U)`, which means devices with only setting 0 remain on 0 while devices with more settings use 1. The touchpad path uses pressure hysteresis for `BTN_TOUCH` and maps pen width as a finger. Wheel events for VMware-like behavior are not relevant, but this driver reports cPad auxiliary middle button from a fourth button bit. Reset and suspend paths must avoid URB resubmission after disconnect.

## Test Signals
USB enumeration should show the correct input capabilities for touchpad, stick, touchscreen, and composite interfaces. Validate URB resubmission after runtime PM resume and USB reset, pressure hysteresis, button mapping, cPad always-on I/O, and no use-after-free on unplug during open reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_usb.c -->

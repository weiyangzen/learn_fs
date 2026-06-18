# sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-kbd.c

Fixes Holtek USB keyboard descriptors and routes LED output events from the corrected secondary interface to the boot keyboard interface.

`holtek_kbd_rdesc_fixed` reduces excessive consumer usages and adds an LED output block. `holtek_kbd_report_fixup()` returns the replacement descriptor for USB interface 1. `holtek_kbd_input_event()` finds USB interface 0, retrieves its HID input device, and forwards LED events to that boot interface. `holtek_kbd_probe()` parses/starts HID and installs the event redirect on interface 1 inputs.

The driver keeps no private state; it mutates `input->event` callbacks for interface 1 at runtime. Dependencies include USB HID, HID core, input callbacks, `usbhid`, and Holtek alternate IDs from `hid-ids.h`.

Risks include cross-interface assumptions, interface 0 not being available or bound, and callback replacement interactions. Test signals include both interfaces, descriptor parse success, consumer key range handling, caps/num/scroll LED behavior, boot-interface absence failure, and suspend/resume.

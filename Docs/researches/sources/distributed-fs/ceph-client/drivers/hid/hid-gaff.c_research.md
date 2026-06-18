# sources/distributed-fs/ceph-client/drivers/hid/hid-gaff.c

Adds force-feedback rumble support for GreenAsia USB joystick devices using product ID `0x0012`. Normal input handling stays with HID core while this file installs a memless FF callback that writes device-specific output reports.

`struct gaff_device` stores the output `hid_report`. `hid_gaff_play()` converts `FF_RUMBLE` strong/weak magnitudes to one-byte motor intensities, fills six report values, and sends two command patterns with `hid_hw_request()`. `gaff_init()` finds the first HID input and output report, validates field capacity, registers `input_ff_create_memless()`, seeds the device, and advertises `FF_RUMBLE`. `ga_probe()` parses and starts HID with default FF disabled so the custom path owns rumble.

The only driver-private state is the memless FF data pointer and report reference. There is no persistent storage. Dependencies are HID core, input FF, optional `CONFIG_GREENASIA_FF`, and IDs from `hid-ids.h`.

Risks include hard-coded protocol bytes, assumption that the first output report has at least six values, and ignored `gaff_init()` failures so input can work while FF silently disappears except for logs. Test signals include FF exposure, left/right motor scaling, absent/short output report handling, and no-FF config behavior.

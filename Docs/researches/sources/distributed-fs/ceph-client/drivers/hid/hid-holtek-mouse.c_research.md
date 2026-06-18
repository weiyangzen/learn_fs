# sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-mouse.c

Fixes malformed report descriptors for several Holtek-based gaming mice whose consumer usage and logical maxima exceed `HID_MAX_USAGES`.

`holtek_mouse_report_fixup()` checks USB interface 1 and product ID, then patches descriptor bytes representing `0x7fff` maxima down to `0x2fff` at known offsets. Products are split into two descriptor-layout groups. `holtek_mouse_probe()` validates USB transport, parses, and starts HID.

There is no private state or persistent setting; only the in-memory report descriptor is changed before parsing. Dependencies include USB HID, HID report fixup, and Holtek alternate IDs from `hid-ids.h`.

Risks are offset-specific patching and interface-number assumptions. New firmware may need new offsets or may expose the bad descriptor elsewhere. Test signals include each product ID, both offset groups, interface 0 unchanged, parse success on interface 1, sentinel mismatch fallback, and normal mouse/consumer input.

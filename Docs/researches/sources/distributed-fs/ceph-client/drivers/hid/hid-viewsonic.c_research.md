# sources/distributed-fs/ceph-client/drivers/hid/hid-viewsonic.c

Purpose: replaces the bad report descriptor of ViewSonic/signotec PD1011 signature pads with a fixed digitizer descriptor.

Important APIs, types, and functions: `PD1011_RDESC_ORIG_SIZE` guards replacement. `pd1011_rdesc_fixed[]` describes stylus X/Y, in-range, tip switch, and pressure fields with corrected logical/physical ranges. `viewsonic_report_fixup()` selects the fixed descriptor for ViewSonic and signotec PD1011 product IDs only when the original descriptor size matches.

Control flow: HID core invokes `report_fixup`; matching devices with expected descriptor size receive the static fixed descriptor and updated size, otherwise the original descriptor is returned unchanged.

State and persistence: stateless; static descriptor only.

Dependencies and integration: depends on HID report fixup and device IDs from `hid-ids.h`. Registers a `viewsonic` HID driver.

Risks: replacement is all-or-nothing by size and product. Firmware with the same ID but different descriptor size will not be fixed; firmware with same size but different semantics could be misdescribed, though the product guard narrows this.

Test signals: no automated tests. Validate HID parsing and signature input events for both ViewSonic and signotec branded PD1011 devices.

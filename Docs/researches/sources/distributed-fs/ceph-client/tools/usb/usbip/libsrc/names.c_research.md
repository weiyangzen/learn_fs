# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.c

Purpose: `names.c` parses the `usb.ids` database and provides lookup tables for vendor, product, class, subclass, and protocol names used in usbip list/port output.

Important APIs, types, and functions: hash buckets store linked `vendor`, `product`, `class`, `subclass`, and `protocol` records. Public lookups are `names_vendor()`, `names_product()`, `names_class()`, `names_subclass()`, and `names_protocol()`. `names_init()` opens a database and calls `parse()`. `names_free()` releases all allocations tracked through the custom `pool` list. Internal `new_*()` helpers deduplicate and insert records.

Control flow: `parse()` reads lines, strips CR/LF, skips comments and unsupported sections, tracks current vendor/class context, and interprets tab indentation as product/subclass/protocol entries. It ignores many usb.ids sections such as HID, HUT, languages, reports, physical descriptors, and audio terminal metadata.

State and dependencies: parsed data is held in static global hash tables and a static allocation pool. It depends on a valid usb.ids format and `usbip_common` logging. Risks include no hash-table reset after `names_free()` leaving stale static bucket pointers, duplicate entries logged but ignored, parser fragility around unusual whitespace, and fixed 512-byte line buffers truncating long names. Test signals are successful `usbip list` output with names instead of unknown strings and no parser errors for common distribution `usb.ids` files.

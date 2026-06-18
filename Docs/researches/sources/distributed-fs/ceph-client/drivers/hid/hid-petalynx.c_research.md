<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-petalynx.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-petalynx.c

## Purpose
This driver supports the Petalynx Maxter Remote by fixing a too-low consumer usage maximum, mapping vendor-specific remote buttons to Linux key codes, and forcing `HID_QUIRK_NOGET` during probe. It is a device quirk driver layered on normal HID input handling.

## Important APIs, types, and functions
`pl_report_fixup` patches descriptor maximum values when a precise descriptor pattern is present. `pl_input_mapping` maps Logitech/vendor-page usages 0x05a-0x05e to text/color keys and consumer usages 0x0f6/0x0fa to next/back. `pl_probe` sets `HID_QUIRK_NOGET`, calls `hid_parse`, then starts hardware with `HID_CONNECT_DEFAULT`.

## Control flow
On match, custom probe sets the no-get quirk before parse/start. Descriptor fixup runs during parse and changes both the usage maximum and logical maximum from `0xf9`/`0xf5` style limits to `0xfa` where the exact report bytes match. Input mapping handles selected vendor and consumer usages with `hid_map_usage_clear`, returning 1 for mapped usages and 0 for generic fallback.

## State and persistence behavior
There is no per-device allocation. The persistent runtime effects are the HID quirk bit, patched descriptor bytes, and the input mapping table installed in the input device.

## Dependencies and integration points
The file depends on HID core, Linux key codes, and `hid-ids.h`. Its output is a normal HID input device with corrected key capabilities.

## Risks and test signals
Risks include overly specific descriptor offsets and the broad `NOGET` quirk potentially hiding feature reports if future devices reuse the ID with different behavior. Tests should cover all remapped keys, descriptor parsing with the original Maxter descriptor, and probe/start behavior when GET_REPORT would otherwise fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-petalynx.c -->

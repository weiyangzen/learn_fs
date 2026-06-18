<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-penmount.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-penmount.c

## Purpose
This driver provides a minimal input mapping quirk for PenMount 6000 HID touchscreens. It remaps the first button usage to `BTN_TOUCH` and rejects additional button usages, making the touch contact semantics line up with Linux touchscreen input expectations.

## Important APIs, types, and functions
`penmount_input_mapping` is the only behavioral callback. It is registered in `penmount_driver.input_mapping`. The device table binds `USB_VENDOR_ID_PENMOUNT` and `USB_DEVICE_ID_PENMOUNT_6000`.

## Control flow
Generic HID parsing and hardware start are used. During input mapping, usages on `HID_UP_BUTTON` are inspected. Usage button 1 maps to `EV_KEY/BTN_TOUCH` via `hid_map_usage`; all other button usages return `-1`, telling HID input mapping to ignore them. Non-button usages return 0 so generic mapping can process coordinates and other fields.

## State and persistence behavior
No private state is allocated. The only lasting effect is the input device capability mapping created during probe.

## Dependencies and integration points
The file integrates with HID input mapping and Linux input event codes. Coordinate processing remains generic; this file only corrects touch button semantics.

## Risks and test signals
Risks are limited to button usage interpretation. Devices that use multiple meaningful buttons would lose them, but this is deliberate for the matched touchscreen. Tests should verify `BTN_TOUCH` press/release appears with coordinate reports and that extra button usages are not exposed as spurious keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-penmount.c -->

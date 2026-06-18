# sources/distributed-fs/ceph-client/drivers/usb/misc/apple-mfi-fastcharge.c

## Purpose
`apple-mfi-fastcharge.c` registers a USB device-level driver that exposes Apple MFi fast-charge control as a power-supply device. It matches Apple devices with product IDs in the `0x12nn` range and lets userspace switch charge type between trickle and fast.

## Important APIs, Types, And Functions
`struct mfi_device` stores the USB device, registered `power_supply`, power-supply descriptor, and current charge type. `mfi_fc_driver` is a `usb_device_driver`, not an interface driver. Matching is split between `mfi_fc_id_table` for vendor and `mfi_fc_match()` for product range. Power-supply callbacks are `apple_mfi_fc_get_property()`, `apple_mfi_fc_set_property()`, and `apple_mfi_fc_property_is_writeable()`. The hardware command is issued by `apple_mfi_fc_set_charge_type()`.

## Control Flow
Driver init calls `usb_register_device_driver()`. Probe validates the product range, allocates state and a per-device power-supply name, copies the descriptor, sets initial charge type to trickle, registers the power supply, stores the USB device pointer, and attaches driver data to `udev->dev`. Setting `POWER_SUPPLY_PROP_CHARGE_TYPE` runtime-resumes the USB device, maps requested charge type to 0 mA or 2500 mA, sends a vendor OUT control request `0x40` with current in both `wValue` and `wIndex`, updates cached state on success, then autosuspends. Disconnect unregisters the power supply and frees the descriptor name and state.

## State And Persistence
The only persistent runtime state is `charge_type` in memory and whatever charging mode the device applies after the vendor request. The power-supply descriptor name is dynamically allocated per bus/device number. State disappears on disconnect or module unload.

## Dependencies And Integration Points
The driver depends on USB device-driver APIs, runtime PM, and the power-supply class. Userspace observes and writes `POWER_SUPPLY_PROP_CHARGE_TYPE` and sees scope as `POWER_SUPPLY_SCOPE_DEVICE`.

## Risks
The match table initially matches all Apple vendor devices and relies on `.match()` and `.probe()` to narrow to `0x1200..0x12ff`. The vendor control request is based on MFi behavior and may fail or be unsupported on some devices. `usb_control_msg()` uses `USB_CTRL_GET_TIMEOUT` despite being an OUT request, which is unusual but probably only a timeout constant. Probe sets `mfi->udev` after power-supply registration, so callbacks before that assignment would dereference NULL; normal registration paths likely prevent immediate property calls, but it is a lifetime assumption.

## Test Signals
Test matching for Apple product IDs inside and outside `0x12nn`, power-supply registration naming, charge-type get/set, invalid charge types returning `-EINVAL`, runtime PM failure, control-transfer failure, disconnect after registration, and repeated set to the same charge type avoiding USB traffic.

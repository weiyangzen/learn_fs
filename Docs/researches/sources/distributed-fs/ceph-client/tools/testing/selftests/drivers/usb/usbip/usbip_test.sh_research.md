# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/usb/usbip/usbip_test.sh

## Purpose
Manual-style USB/IP integration script that exercises export, bind, unbind, attach, detach, duplicate operations, invalid detach, and module removal/reload behavior for a specified USB bus id.

## Important APIs, Types, And Functions
Parses `-b <busid>` and `-p <usbip tools path>`. Uses `modprobe usbip_host`, `modprobe vhci_hcd`, built `src/usbip` and `src/usbipd`, `lsusb -t`, `rmmod usbip_host`, and `dmesg`.

## Control Flow
The script requires root and built tools, loads modules, starts `usbipd -D`, lists exportable devices, binds/unbinds the bus id with duplicate operation checks, verifies remote listing state, tests attach failure before export, attaches after export, waits for sysfs update, detaches ports 00/01 including repeated and invalid detach, removes `usbip_host`, tries binding without the module, reloads it, and greps dmesg for match-table diagnostics.

## State And Persistence
It changes the selected USB device's bound driver, starts a daemon, attaches devices through vhci, removes kernel modules, and reads kernel log. It does not provide a trap to restore state on early failure.

## Dependencies And Integration Points
Requires a real target USB device bus id, root, usbip userspace tools built in `tools_path`, `usbip_host`, `vhci_hcd`, `lsusb`, and localhost networking.

## Risks
The script mostly prints expected outcomes rather than asserting command status, so regressions can be missed unless output is inspected. Module removal and device binding are disruptive. Hard-coded detach ports 00/01 may not match actual attachment slot.

## Test Signals
Expected signals are visible usbip list/port output transitions, already-bound/already-imported/no-device messages, successful attach/port listing, invalid port error, and dmesg line containing “is not in match_busid table”.

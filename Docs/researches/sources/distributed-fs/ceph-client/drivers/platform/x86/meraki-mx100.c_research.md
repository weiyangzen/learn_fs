<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meraki-mx100.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/meraki-mx100.c

## Purpose
This board platform driver describes Cisco Meraki MX100 GPIO LEDs and reset button using software nodes and platform devices.

## Important APIs, Types, And Functions
The file defines a `gpio_ich` software node, child software nodes for many `leds-gpio` LEDs, and a `gpio-keys-polled` reset key node. `tink_board_init()` gates on DMI vendor/product, forces GPIO60 into GPIO mode with direct I/O to `GPIO_USE_SEL2`, registers software nodes, and creates `leds-gpio` and `gpio-keys-polled` platform devices. `tink_board_exit()` unregisters devices and nodes.

## Control Flow
Module init checks for DMI vendor `Cisco` and product `MX100-HW`. On match it writes bit 28 at I/O port `0x530` so GPIO60 is usable for reset, registers the software-node graph, creates the LED platform device with the LEDs node fwnode, then creates the keys platform device with the keys node fwnode. Errors unwind in reverse order.

## State And Persistence
Persistent runtime state is limited to two platform device pointers and registered software nodes. GPIO line state is handled by downstream `gpio_ich`, `leds-gpio`, and `gpio-keys-polled` drivers.

## Dependencies And Integration Points
Dependencies include DMI, x86 I/O port access, software nodes, GPIO property descriptors, `leds-gpio`, `gpio-keys-polled`, and the ICH GPIO controller. Userspace sees labeled LEDs and a reset key event `KEY_RESTART`.

## Risks And Edge Cases
Direct port I/O is board-specific and assumes the documented PCH register layout. LED polarity varies per line and must match board wiring. The reset button is polled every 20 ms with 100 ms debounce. Loading on non-MX100 hardware is prevented only by DMI.

## Test Signals
Tests should verify DMI gating, software-node registration, all LED labels and GPIO polarities, reset key event generation, cleanup on partial platform-device failure, and GPIO60 mode after the I/O register write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meraki-mx100.c -->

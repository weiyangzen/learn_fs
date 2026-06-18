# sources/distributed-fs/ceph-client/net/bluetooth/leds.c

## Purpose
Provides optional Bluetooth LED trigger support for the kernel Bluetooth stack. It exposes a global `bluetooth-power` trigger representing whether any HCI device is powered, and per-HCI-device power triggers named from the controller device name.

## APIs, Types, and Functions
`DEFINE_LED_TRIGGER(bt_power_led_trigger)` defines the global trigger object. `struct hci_basic_led_trigger` wraps a `struct led_trigger` with the owning `struct hci_dev`; `to_hci_basic_led_trigger()` converts from trigger pointer back to that wrapper. Public functions are `hci_leds_update_powered()`, `hci_leds_init()`, `bt_leds_init()`, and `bt_leds_cleanup()`.

`hci_leds_update_powered()` updates the per-device `hdev->power_led` and then updates the global trigger. `power_activate()` initializes a newly attached LED class device to the current HCI powered state. `led_allocate_basic()` allocates and registers a per-device managed LED trigger using `devm_kzalloc()`, `devm_kasprintf()`, and `devm_led_trigger_register()`.

## Control Flow, State, and Persistence
Bluetooth core initialization calls `bt_leds_init()`, registering the simple global trigger name `bluetooth-power`; Bluetooth exit or init failure calls `bt_leds_cleanup()`. HCI device registration calls `hci_leds_init()`, which allocates a managed per-device trigger such as `hci0-power` and stores it in `hdev->power_led`.

When an HCI device powers up, `hci_leds_update_powered(hdev, true)` sets the device trigger to `LED_FULL` and sets the global trigger to `LED_FULL`. When a device powers down, the per-device trigger is set to `LED_OFF`, then the function scans `hci_dev_list` under `hci_dev_list_lock`; if any other device still has `HCI_UP`, the global trigger remains `LED_FULL`, otherwise it becomes `LED_OFF`.

State is held in LED trigger registration objects, `hdev->power_led`, and the live HCI device list/flags. Per-device trigger memory and names are device-managed and disappear with the HCI device. There is no durable persistence; LED brightness is a runtime reflection of HCI flags.

## Dependencies and Integration
Depends on Bluetooth core declarations from `bluetooth.h` and `hci_core.h`, the kernel LED trigger subsystem, device-managed allocation, and the global HCI device list. Integration points are `af_bluetooth.c` for stack-wide init/cleanup, `hci_core.c` for per-device trigger creation during `hci_register_dev()`, and `hci_sync.c` for powered-state updates during open and close.

## Risks and Test Signals
Risks include missed global-trigger updates when HCI power transitions bypass `hci_leds_update_powered()`, stale brightness if `power_activate()` races with HCI flag changes, allocation or registration failures leaving `hdev->power_led` NULL, and global LED state depending on correct locking and iteration of `hci_dev_list`.

Test signals include presence of the `bluetooth-power` trigger when Bluetooth LED support is enabled, per-controller trigger creation after HCI registration, LED brightness changing to full/off on controller up/down, global trigger staying on while at least one controller remains up, and clean unregister behavior on Bluetooth subsystem exit.

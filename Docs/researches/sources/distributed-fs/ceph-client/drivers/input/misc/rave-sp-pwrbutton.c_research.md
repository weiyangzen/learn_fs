# sources/distributed-fs/ceph-client/drivers/input/misc/rave-sp-pwrbutton.c

## Purpose
`rave-sp-pwrbutton.c` converts RAVE SP MFD event notifications into `KEY_POWER` input events. It is a small notifier-backed power-button driver for ZII RAVE SP devices.

## Important APIs, Types, and Functions
`struct rave_sp_power_button` contains an input device and notifier block. `rave_sp_power_button_event()` decodes packed RAVE SP actions through `rave_sp_action_unpack_event()` and `rave_sp_action_unpack_value()`. `rave_sp_pwrbutton_probe()` allocates/registers the input device and registers the event notifier with `devm_rave_sp_register_event_notifier()`.

## Control Flow
Probe creates an input device named after the platform device, enables `EV_KEY/KEY_POWER`, registers it, then registers a high-priority notifier. Notifier callbacks check for `RAVE_SP_EVNT_BUTTON_PRESS`, report the provided value as key state, sync, and return `NOTIFY_STOP`; unrelated events return `NOTIFY_DONE`.

## State and Persistence Behavior
The driver stores only the input-device pointer and notifier block. Button state is transient in input core. Notifier lifetime is devm-managed with the platform device.

## Dependencies and Integration Points
It depends on the RAVE SP MFD event-notifier API, OF compatible `zii,rave-sp-pwrbutton`, platform device binding, and input core. It integrates with userspace through evdev `KEY_POWER`.

## Risks and Edge Cases
The driver trusts notifier values as key states without normalization. Registering the input device before the notifier means notifier registration failure leaves a harmless input device with no event source. There is no wakeup setup here, so wake behavior depends on parent MFD/event infrastructure.

## Test Signals
Test notifier delivery of press/release values, unrelated events, notifier registration failure, OF matching, module unload/device removal, and userspace key events from the input node.

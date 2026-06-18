
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_usbpd_notify.h

## Purpose
This small header exposes the ChromeOS USB Power Delivery notification registration API. It lets kernel consumers subscribe to USB-PD events through a notifier block without depending on a concrete driver internals header.

## Important APIs And Types
The public API is `cros_usbpd_register_notify(struct notifier_block *nb)` and `cros_usbpd_unregister_notify(struct notifier_block *nb)`. The only type dependency is Linux `struct notifier_block`.

## Control Flow, State, And Persistence
The header declares notifier registration only; the state lives in the provider driver's notifier chain. Registered callbacks are called when the USB-PD provider emits events, and unregister removes the callback from that chain. No persistent state or storage is described here.

## Dependencies And Integration Points
It depends on `linux/notifier.h` and integrates ChromeOS PD notification producers with consumers such as Type-C, power-supply, charger, or policy drivers.

## Risks And Test Signals
Risks are normal notifier-chain risks: unregister must happen before callback storage disappears, callbacks must tolerate provider teardown, and event meanings must match provider documentation. Test signals include successful registration/unregistration, event callback delivery, module unload without use-after-free, and behavior when no notifier provider is present.

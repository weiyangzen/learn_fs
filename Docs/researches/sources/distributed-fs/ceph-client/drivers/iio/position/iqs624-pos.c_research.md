# sources/distributed-fs/ceph-client/drivers/iio/position/iqs624-pos.c

## Purpose
Platform IIO driver for Azoteq IQS624/IQS625 angular position sensing through the IQS62x MFD core.

## Important APIs, Types, And Functions
`struct iqs624_pos_private` stores the MFD core pointer, IIO device, notifier block, mutex, event-enable flag, and cached angle. `iqs624_pos_angle_get()` reads the IQS624 degree output or IQS625 interval register. `iqs624_pos_angle_en()` unmasks the correct MFD event type depending on product. `iqs624_pos_notifier()` handles reset reinitialization and emits IIO change events on angle changes. IIO callbacks provide raw angle, scale, and event enable control.

## Control Flow
Probe gets the parent `iqs62x_core`, allocates IIO state, registers a notifier with the MFD event chain, installs a devm unregister action, and registers the IIO device. Event enable writes snapshot the current angle, update event masks, and cache enabled state. Notifier callbacks compare incoming angle/interval values and push IIO change events.

## State And Persistence
Driver state is RAM-only. Hardware event mask is changed when events are enabled/disabled and is restored after system reset events from the MFD notifier.

## Dependencies And Integration Points
Uses `linux/mfd/iqs62x.h`, regmap, blocking notifier chains, and IIO event APIs. Registers as platform driver `iqs624-pos`.

## Risks And Test Signals
Concurrency around event enable and notifier is protected by a mutex. Test IQS624 vs IQS625 product paths, scale derived from interval divisor, event enable/disable, reset notifier reinitialization, and notifier unregister devm action.

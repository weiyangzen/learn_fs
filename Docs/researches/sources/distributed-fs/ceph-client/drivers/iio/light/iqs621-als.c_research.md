# sources/distributed-fs/ceph-client/drivers/iio/light/iqs621-als.c

## Purpose

`iqs621-als.c` is an IIO child driver for Azoteq IQS621 and IQS622 ambient light/proximity functions exposed by the IQS62x MFD core. IQS621 exposes ALS range and light threshold events; IQS622 exposes visible/IR intensity plus proximity threshold events. The driver uses the parent regmap and notifier chain.

## Important APIs, Types, And Functions

`struct iqs621_als_private` stores the parent `iqs62x_core`, IIO device, notifier block, mutex, event enable booleans, cached flags, selected IR flag mask, and cached thresholds. `iqs621_als_init()` rewrites thresholds and unmasks parent events after reset. `iqs621_als_notifier()` handles parent events and pushes IIO events. Raw/event callbacks are `iqs621_als_read_raw()`, `iqs621_als_read_event_config()`, `iqs621_als_write_event_config()`, `iqs621_als_read_event_value()`, and `iqs621_als_write_event_value()`. Probe selects channel tables based on product number and registers the notifier.

## Control Flow

Probe gets `iqs62x_core` from the parent device, allocates IIO state, reads initial thresholds, selects IQS621 or IQS622 channel definitions, initializes the mutex, registers a blocking notifier with the parent, arranges devm notifier cleanup, and registers IIO. Event-enable writes read current flags first, update the global event mask in the parent register, and cache enable booleans. Parent notifications compare new and old light/range/proximity flags, emit rising or falling IIO events, update cached flags, and reinitialize thresholds/masks after system reset events.

## State And Persistence

Threshold values are cached in driver state and written to the parent regmap. Event enable state is kept as booleans; parent event mask bits are the hardware-facing state. `als_flags` and `ir_flags` cache previous notifier state to detect transitions. After a parent reset, `iqs621_als_init()` restores thresholds and unmasks enabled events.

## Dependencies And Integration Points

The driver depends on the IQS62x MFD core, parent regmap, parent notifier chain, IIO events, and platform device alias `iqs621-als`. It has no direct bus binding; the MFD creates the platform child.

## Risks And Test Signals

The proximity event threshold selection changes `ir_flags_mask` based on value range, so switching between touch and prox thresholds should be tested with enabled events. Parent reset handling must restore all cached thresholds and event masks. Tests should cover IQS621 and IQS622 channel layouts, raw reads from flags/UI output registers, event enable combinations for light and range sharing the ALS mask, proximity enable on IQS622, threshold read/write scaling, notifier transition detection, and unregister failure logging.

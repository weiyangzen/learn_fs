# sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys_polled.c

## Purpose

`gpio_keys_polled.c` is the polling variant of the GPIO keys driver for GPIO lines without usable interrupts. It reads button GPIOs at a configured interval, debounces them, and reports key, relative-axis, or absolute-axis events.

## Important APIs, Types, and Functions

- `struct gpio_keys_button_data` stores each GPIO descriptor, last state, debounce count, and threshold.
- `struct gpio_keys_polled_dev` stores input, device, platform data, seen-axis bitmaps, and per-button data.
- `gpio_keys_polled_get_devtree_pdata()` builds platform data from firmware child nodes.
- `gpio_keys_polled_poll()` handles debounce, reports events, resets unseen axes to zero, and syncs input.
- `gpio_keys_polled_probe()` parses platform/fwnode data, obtains GPIOs, sets capabilities, installs polling, registers input, and reports initial state.

## Control Flow

Probe requires `poll_interval`, allocates state/input, iterates configured buttons to reject wakeup requests, obtain GPIOs, derive debounce thresholds, set input capabilities and ABS ranges, installs the poll callback, registers the input device, and emits initial state. Each poll repeats previous state while debounce threshold is being reached; after that it reads GPIO state, reports changes or axis values, zeroes relative/absolute axes not seen in this poll, and syncs.

## State and Persistence Behavior

Per-button `last_state` and `count` persist across polls for debounce. `rel_axis_seen` and `abs_axis_seen` are transient per poll. Optional platform enable/disable hooks run on input open/close. No wake or nonvolatile state is supported.

## Dependencies and Integration Points

It uses platform bus, GPIO descriptor and legacy GPIO APIs, input polling, fwnode/OF compatible `gpio-keys-polled`, `linux/gpio_keys.h`, and properties such as `poll-interval`, `autorepeat`, `linux,code`, `linux,input-type`, `linux,input-value`, `debounce-interval`, and `label`.

## Risks and Edge Cases

Wakeup is explicitly unsupported and causes probe failure if requested. Missing `poll_interval` fails probe. Relative/absolute events are emitted only while active and reset to zero when not observed, so button value semantics must match the target input consumer. Debounce is poll-count based and can be coarse at long intervals.

## Test Signals

Test key, relative, and absolute button definitions; debounce intervals versus poll intervals; initial state reporting; missing/invalid GPIOs; wakeup rejection; platform enable/disable hooks; axis reset behavior; autorepeat; and fwnode plus legacy platform-data paths.

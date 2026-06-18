# sources/distributed-fs/ceph-client/drivers/leds/led-core.c

## Purpose
Provides shared LED runtime mechanics: brightness dispatch, asynchronous fallback for sleeping callbacks, software blinking timers, multicolor trigger brightness, fwnode property parsing, LED name composition, default pattern reading, sysfs disable flags, and color/default-state helpers.

## Important APIs, Types, And Functions
Exports include `led_init_core`, `led_blink_set`, `led_blink_set_oneshot`, `led_blink_set_nosleep`, `led_stop_software_blink`, `led_set_brightness`, `led_set_brightness_nopm`, `led_set_brightness_nosleep`, `led_set_brightness_sync`, `led_mc_set_brightness`, `led_update_brightness`, `led_get_default_pattern`, `led_sysfs_disable`, `led_sysfs_enable`, `led_compose_name`, `led_get_color_name`, and `led_init_default_state_get`.

Global `leds_list` and `leds_list_lock` are exported for trigger registration and default-trigger matching.

## Control Flow
`led_init_core` initializes each classdev work item and blink timer. Brightness updates prefer non-sleeping `brightness_set`; if unavailable they queue work for `brightness_set_blocking`. Software blink toggles brightness from a timer and respects oneshot, inverted oneshot, and brightness-change flags. `led_blink_set` tries hardware `blink_set` first and falls back to software blinking, defaulting unspecified delays to 500 ms.

Name composition parses `label`, `color`, `function`, `function-enumerator`, fallback labels, OF node names, or software node names. Default state parsing maps fwnode `default-state` values to off/on/keep.

## State And Persistence
Per-classdev persistent state includes `brightness`, `blink_brightness`, blink delays, delayed brightness/work values, and atomic work flags. Timer and workqueue state mediate asynchronous changes. Fwnode-derived names, patterns, and default state are read from firmware descriptions but not stored globally beyond classdev fields.

## Dependencies And Integration Points
Depends on timers, workqueues, mutexes/rwsems, fwnode/OF/property APIs, multicolor support, and the base LED headers. It is used by all LED class drivers and trigger code.

## Risks
The ordering of `LED_SET_BRIGHTNESS_OFF`, `LED_SET_BRIGHTNESS`, and `LED_SET_BLINK` is important to avoid off/on reordering when triggers issue rapid changes. Software blink timer callbacks can run in atomic context, so paths must use nosleep dispatch. `led_set_brightness_sync` rejects active blinking, which callers must handle. Name parsing preserves legacy `label` behavior, so changes can break user ABI.

## Test Signals
Exercise immediate and blocking brightness callbacks, rapid off/on trigger sequences, software and hardware blink fallback, oneshot blink behavior, suspend flag behavior, multicolor trigger updates, name composition from firmware properties, and default-pattern/default-state parsing.

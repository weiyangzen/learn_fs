<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs269a.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/iqs269a.c

## Purpose
`iqs269a.c` is an I2C input driver for the Azoteq IQS269A capacitive/inductive touch controller. It can register a keypad device for channel events and Hall switches, plus up to two slider devices that either emit gesture keycodes or raw `BTN_TOUCH`/`ABS_X` events.

## Important APIs, Types, and Functions
`struct iqs269_private` stores regmap, lock, switch descriptors, version info, cached system/channel register image, ATI completion, input devices, keycode maps, OTP option, selected channel, Hall mode, and ATI freshness. `iqs269_parse_prop()` and `iqs269_parse_chan()` translate device and child-node firmware properties into the cached `struct iqs269_sys_reg`. ATI sysfs helpers adjust channel tuning fields. `iqs269_dev_init()` writes the full configuration and triggers ATI. `iqs269_report()` reads flags, handles unexpected reset reinitialization, reports slider/keypad events, and completes ATI. `iqs269_irq()` wraps report handling and waits for RDY deassertion.

## Control Flow
Probe allocates state, initializes regmap/mutex/completion, reads OTP option from OF match data, validates product number, parses properties and child channels, writes device configuration, creates input devices, requests a threaded IRQ, waits up to two seconds for ATI completion and initial reports, then registers the keypad. Slider inputs are registered earlier during input init if enabled. Sysfs attributes allow reading counts and Hall bin values, toggling Hall enable, selecting a channel, editing RX/ATI fields, and triggering ATI reinitialization.

## State and Persistence Behavior
The driver maintains a cached big-endian image of IQS269 system/channel registers and marks ATI stale when tuning state changes. `ati_done` synchronizes probe and manual ATI triggers. Suspend/resume write the general settings register to enter/leave configured low-power modes while disabling the IRQ around unsolicited I2C accesses. Unexpected device reset in runtime reports causes the cached configuration to be rewritten.

## Dependencies and Integration Points
It binds to OF compatibles `azoteq,iqs269a`, `azoteq,iqs269a-00`, and `azoteq,iqs269a-d0`; uses I2C regmap with 8-bit registers and 16-bit values; consumes firmware properties and child nodes; exposes sysfs groups; and integrates with input key, switch, and absolute reporting plus PM sleep hooks.

## Risks and Test Signals
Risks include broad property surface with many bounds, endian-sensitive raw register images, IRQ disable windows for sysfs reads, raw slider versus gesture mode selection, Hall channel repurposing, and input reports for `KEY_RESERVED` entries if mappings are absent in some paths. Tests should cover product validation, each property bound failure, channel parsing, Hall-enabled and Hall-disabled reporting, slider raw/gesture behavior, ATI timeout, reset reinitialization, sysfs tuning invalidation, and suspend/resume register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs269a.c -->

# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f30.c

## Purpose

`rmi_f30.c` implements RMI4 Function 30, GPIO/LED/control support, focusing on GPIO-backed button reporting. It maps valid input GPIOs to Linux button keycodes and can route trackstick button GPIOs through F03 PS/2 out-of-band button overrides.

## Important APIs, Types, and Functions

`struct rmi_f30_ctrl_data` describes a parsed control-register block. `struct f30_data` stores query capabilities, control block layout, shadow control bytes, data bytes, keymap, shared input device, and optional F03 link. Key functions include `rmi_f30_initialize()`, `rmi_f30_set_ctrl_data()`, `rmi_f30_map_gpios()`, `rmi_f30_config()`, `rmi_f30_attention()`, and `rmi_f30_report_button()`.

## Control Flow

Probe exits early if platform GPIO data disables F30, requires the shared input device, allocates state, reads F30 queries, computes present control-register blocks, reads the control shadow, maps valid GPIO inputs to keycodes, and stores driver data. Config re-finds F03 when trackstick buttons are enabled, writes the control shadow back unless disabled, and enables or clears the IRQ mask. Attention consumes transport data or reads data registers, reports each mapped active-low GPIO button, and commits F03 OOB buttons when trackstick routing is active.

## State and Persistence Behavior

F30 persists query flags, register counts, control shadow bytes, keymap, and optional F03 linkage. The control shadow is written back on config, preserving or reapplying hardware GPIO/LED configuration. Button state is sampled per attention and not otherwise retained.

## Dependencies and Integration Points

The file depends on RMI core reads/writes, platform `gpio_data`, the shared input device, RMI IRQ masks, and F03 helper functions for trackstick passthrough. It also uses Linux input properties to mark buttonpads.

## Risks and Edge Cases

The keymap allocation uses `min(gpioled_count, TRACKSTICK_RANGE_END)` but later sets `keycodemax` to `gpioled_count` and loops to `gpioled_count`, which can index past the allocated map when more than six GPIO/LEDs exist. Control-block offset computation must match the query flags exactly. Trackstick routing only establishes if F03 is present by config time. Active-low interpretation may not match every board wiring.

## Test Signals

Tests should include GPIO-only, LED-only, combined GPIO/LED, haptic, mappable, and mechanical-button capability combinations; devices with more than six GPIOs; buttonpad and non-buttonpad mappings; trackstick-with-F03 and trackstick-without-F03 paths; control writeback failures; and attention packets from both transport and register reads.

# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f3a.c

## Purpose

`rmi_f3a.c` implements RMI4 Function 3A GPIO button reporting. It reads GPIO existence and direction data, maps valid input GPIOs to button keycodes, reports active-low button states, and optionally routes trackstick buttons through F03 PS/2 out-of-band button emulation.

## Important APIs, Types, and Functions

`struct f3a_data` stores GPIO count, register count, data bytes, key map, shared input device, optional F03 pointer, and trackstick state. Important functions include `rmi_f3a_initialize()`, `rmi_f3a_map_gpios()`, `rmi_f3a_is_valid_button()`, `rmi_f3a_config()`, `rmi_f3a_attention()`, and `rmi_f3a_report_button()`.

## Control Flow

Probe requires the shared input device, allocates state, reads the general query byte, computes register count, reads Query1 GPIO-existence bits and Control1 direction bits, maps valid input GPIOs to `BTN_LEFT` and subsequent buttons, and stores driver data. Config optionally finds Function 03 for trackstick routing and enables the IRQ mask. Attention consumes transport attention data or reads the data registers, reports every mapped button, and commits F03 OOB button state if trackstick mode is active.

## State and Persistence Behavior

The function stores query-derived GPIO/register counts, key mapping, latest data-register bytes, and optional F03 linkage. It does not change hardware GPIO configuration. Input keymap and buttonpad property persist on the shared input device.

## Dependencies and Integration Points

The file depends on RMI reads, platform `gpio_data`, shared RMI attention data, Linux input, RMI IRQ masks, and F03 helper functions for trackstick button routing.

## Risks and Edge Cases

The keymap allocation is capped at `TRACKSTICK_RANGE_END`, while `gpio_count` and the reporting loop may be larger, creating possible out-of-bounds accesses on devices with more than six GPIOs. `rmi_f3a_report_button()` reads only `data_regs[0]`, so buttons beyond the first eight GPIOs are not decoded correctly. Trackstick F03 linkage may be absent at config time. Active-low assumptions may not fit all boards.

## Test Signals

Coverage should include different GPIO counts, GPIOs configured as outputs versus inputs, more-than-six and more-than-eight GPIO cases, buttonpad mapping, trackstick routing with and without F03, transport attention and direct-read paths, and active-low press/release event validation.

# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-th1520.c

## Purpose
`pinctrl-th1520.c` is the T-Head TH1520 SoC pinctrl driver. It supports three pad groups, per-pin mux selection, generic pin configuration for padcfg-capable pins, GPIO mux requests, and GPIO input-enable direction control over MMIO registers.

## Important APIs, Types, and Functions
`struct th1520_pad_group` describes one compatible pad bank with a name and static pin descriptor table. `struct th1520_pinctrl` owns the pinctrl descriptor, mutex for dynamically adding functions, raw spinlock for register read/modify/write, base MMIO address, and pinctrl device. Pin descriptors encode possible mux functions and flags in `drv_data` through `TH1520_PAD()`, with `TH1520_PAD_NO_PADCFG` marking pads that cannot be configured.

DT mapping is handled by `th1520_pinctrl_dt_node_to_map()`, which parses child `pins`, optional `function`, and generic pinconf properties. Pinconf is implemented by `th1520_pinconf_get()`, `th1520_pinconf_set()`, and group variants. Muxing is implemented by `th1520_pinmux_set()`, `th1520_pinmux_set_mux()`, and `th1520_gpio_request_enable()`.

## Control Flow
Probe maps MMIO, enables the clock, reads `thead,pad-group`, chooses one of the three static pin groups, initializes the pinctrl descriptor and locks, registers pinctrl, and enables it. For each pinctrl DT state, the map callback counts selected pins, allocates maps, parses generic configs once per child node, validates pin names against the selected pad group, optionally creates per-pin config maps, and, if a function is present, dynamically registers a unique function named from the parent and child node and maps each selected pin group to it.

When a mux is selected, the stored function data is the desired `enum th1520_muxtype`; `th1520_pinmux_set()` scans the pin's encoded mux alternatives to find the selector value and writes four bits in the MUXCFG register. Pinconf set accumulates a 10-bit padcfg mask/value and does one locked RMW of the halfword associated with the pin. GPIO direction only toggles the input-enable bit; output behavior is presumably handled by the separate GPIO controller.

## State and Persistence
Hardware state lives in PADCFG registers, two pins per 32-bit word, and MUXCFG registers, eight pins per 32-bit word. Register updates are serialized by `raw_spinlock_t lock`. Dynamic functions and group names are devm allocations or generic pinmux registrations protected by `mutex`. There is no suspend/resume context save; state persistence depends on SoC retention or pinctrl consumers reapplying states after resume.

## Dependencies and Integration Points
The driver depends on platform resources, clocks, OF properties, generic pinctrl/pinmux/pinconf frameworks, dynamic generic function registration, and optional debugfs hooks. Its DT integration requires `thead,pad-group` and state child nodes with `pins`, optional `function` strings from the driver's mux string table, and standard generic pinconf properties. GPIO integration uses pinmux hooks only; it does not register a gpiochip.

## Risks
`th1520_drive_strength_from_ma()` loops while `ds < TH1520_PADCFG_DS`, where `TH1520_PADCFG_DS` is a bitmask value rather than the array length; this works only because the mask is 15 and the table has 16 entries, but it is fragile. Dynamic functions are added during DT map creation and are not explicitly removed on map free, so repeated mapping of many unique child nodes could accumulate generic functions for device lifetime. Pins marked no-padcfg reject pinconf, which DT authors must handle. The code does not validate that requested generic configs are electrically meaningful together, for example strong pull-up versus regular pull-up selection beyond fixed resistance constants.

## Test Signals
Test all three `thead,pad-group` values, invalid pad group, clock failure, DT mapping with multiple child nodes and repeated pins, unknown pin and unknown function failures, mux writes for every function slot position, GPIO request selecting GPIO mux, generic pinconf for bias, drive strength, input enable, Schmitt, and slew, plus no-padcfg rejection. Debugfs output should show correct PADCFG/MUXCFG addresses and values for selected pins.

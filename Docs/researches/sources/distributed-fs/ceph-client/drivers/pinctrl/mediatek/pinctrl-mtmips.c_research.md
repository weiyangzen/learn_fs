# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.c

## Purpose
This file implements the shared pinctrl/pinmux core for older Ralink/MediaTek MIPS SoCs such as RT2880, RT305x, RT3352, RT5350, and RT3883. It consumes SoC-specific `struct mtmips_pmx_group` arrays and registers a Linux pinctrl device named `mtmips-pinctrl`. It is focused on muxing groups through Ralink system controller GPIO mode registers; it does not implement full pinconf or a gpiochip.

## Important APIs, Types, And Functions
The private state is `struct mtmips_priv`, holding generated pin descriptors, group/function indexes, GPIO-capability flags, and the source SoC group table. Pinctrl operations are `mtmips_get_group_count()`, `mtmips_get_group_name()`, and `mtmips_get_group_pins()`. Pinmux operations are `mtmips_pmx_func_count()`, `mtmips_pmx_func_name()`, `mtmips_pmx_group_get_groups()`, `mtmips_pmx_group_enable()`, and `mtmips_pmx_group_gpio_request_enable()`. The exported integration entry is `mtmips_pinctrl_init()`.

## Control Flow
Probe callers pass a sentinel-terminated SoC group table. `mtmips_pinctrl_index()` counts groups, allocates `group_names`, adds a synthetic function zero named `gpio`, and gives every hardware function a backpointer to its single owning group. `mtmips_pinctrl_pins()` allocates per-function pin arrays from `pin_first` and `pin_count`, computes `max_pins`, allocates the GPIO bitmap and pad descriptors, and names pins `io0` through `ioN`. Mux selection in `mtmips_pmx_group_enable()` selects `SYSC_REG_GPIO_MODE` or `SYSC_REG_GPIO_MODE2`, clears the group's mask, updates GPIO eligibility, and writes the selected mux value through `rt_sysc_w32()`.

## State And Persistence
Driver state is devm-managed memory tied to the platform device. The `enabled` flags in group/function structs are mutable and persist until driver removal or reboot. Hardware mux choices persist in Ralink sysc registers until changed or reset. The file does not persist state to storage and does not provide suspend/resume save/restore.

## Dependencies
This file depends on Linux pinctrl core, pinctrl utility DT parsing, Ralink sysc register helpers, and SoC-specific tables declared with `pinctrl-mtmips.h` macros. It assumes each function can be described as a contiguous pin range and each non-GPIO function belongs to one group.

## Risks
There is no locking around sysc read-modify-write or `enabled` flags, so concurrent mux changes could race. Returning success when a group is already enabled may hide conflicting pinctrl state requests. Bounds checks are limited: function selectors are assumed valid by pinctrl core paths, and `gpio_request_enable` indexes `p->gpio[pin]`. The implementation also lacks pinconf and gpiochip integration, so board expectations must be limited to mux validation and pinctrl ownership.

## Test Signals
Test by booting each SoC-specific driver, applying DT states for GPIO and alternate functions, checking sysc GPIO mode register values, attempting GPIO requests before and after mux changes, and verifying pinctrl debug output lists generated `io%d` pins and expected groups. Race-sensitive changes should be reviewed with lockdep or serialized pinctrl state application.

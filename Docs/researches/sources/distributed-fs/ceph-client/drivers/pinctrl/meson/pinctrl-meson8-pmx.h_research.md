# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8-pmx.h

## Purpose
This header defines the first-generation Meson8 pinmux group metadata and table macros used by Meson8 and Meson8b SoC description files.

## Important APIs, Types, and Macros
- `struct meson8_pmx_data` stores whether a group is GPIO plus the mux register index and bit.
- `PMX_DATA()` initializes backend-specific mux metadata.
- `GROUP()` creates a named non-GPIO `struct meson_pmx_group` using a `*_pins` array and a compound-literal `meson8_pmx_data`.
- `GPIO_GROUP()` creates a one-pin GPIO group with `is_gpio = true`.
- `extern const struct pinmux_ops meson8_pmx_ops` exports the backend operations to SoC files.

## Control Flow
No executable code is present. The macros shape static group arrays that `pinctrl-meson8-pmx.c` later scans and casts.

## State and Persistence
The macro-produced data has static storage as part of SoC group tables, while the compound-literal metadata is const table data. Hardware mux state is changed by the backend, not this header.

## Dependencies and Integration Points
The macros assume `ARRAY_SIZE()` and `struct meson_pmx_group` are available through the includer. Meson8-family SoC files include this after `pinctrl-meson.h`.

## Risks
The untyped `data` field requires correct casting in the backend. The `GROUP()` macro expects a matching `grp_pins` symbol; typos fail at compile time, but wrong register/bit values compile and misconfigure hardware. `GPIO_GROUP()` uses dummy register/bit values, so `is_gpio` must be honored everywhere.

## Test Signals
Compile all Meson8-family SoC tables and verify debugfs lists GPIO and alternate groups. Runtime mux tests should confirm that each group writes the intended register bit and GPIO groups do not write mux bits.

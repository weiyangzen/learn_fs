# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.h

## Purpose

This header defines the shared descriptor ABI between Visconti SoC-specific data files and the Visconti common pinctrl implementation. It provides declaration macros and struct layouts for pins, groups, mux register writes, functions, SoC devdata, and the common probe entry point.

## Important APIs, Types, And Data

- `VISCONTI_PINS()` creates static pin-number arrays for groups.
- `struct visconti_desc_pin` embeds a `struct pinctrl_pin_desc` and stores drive-select offset/shift plus pull-enable, pull-select, and pull-shift metadata.
- `VISCONTI_PIN()` initializes a described pin.
- `VISCONTI_GROUPS()` creates static group-name arrays for functions.
- `struct visconti_mux` stores a mux register offset, bit mask, and value.
- `struct visconti_pin_group` binds a group name, pin list, pin count, and one mux operation.
- `VISCONTI_PIN_GROUP()` derives group names with a `_grp` suffix and fills array size and mux metadata.
- `struct visconti_pin_function` maps function names to group arrays.
- `VISCONTI_PIN_FUNCTION()` creates a function descriptor.
- `struct visconti_pinctrl_devdata` packages pins, groups, functions, GPIO mux table, and optional register unlock callback.
- `visconti_pinctrl_probe()` is the common probe function called by chip drivers.

## Control Flow

SoC files use the macros to declare pin arrays, group arrays, function arrays, and `struct visconti_pinctrl_devdata`. Their probe functions call `visconti_pinctrl_probe()`, which interprets these structures to register pinctrl operations and perform MMIO writes.

The header itself has no active control flow, but its field layout controls how `pinctrl-common.c` calculates register addresses and bit positions for drive, pull, mux, and GPIO selection.

## State And Persistence

The header defines immutable descriptor structures and function pointers only. Runtime state is created in `pinctrl-common.c`; persistent hardware state is MMIO register state.

## Dependencies And Integration Points

It forward-declares `struct pinctrl_pin_desc` and expects Linux pinctrl headers to be included by users. It uses kernel macros such as `ARRAY_SIZE` and `__stringify` through the including translation units. It integrates SoC-specific files like `pinctrl-tmpv7700.c` with the common driver.

## Risks And Edge Cases

- The common driver indexes `pins` and `gpio_mux` by pin number, so descriptors created with these macros should remain dense from zero where needed.
- `VISCONTI_PIN_GROUP()` applies one mux register operation per group; groups requiring multiple discontiguous register updates would need a data model change.
- Group names are mechanically suffixed with `_grp`; function group strings must match that generated naming.
- The optional `unlock` hook must be valid for the SoC register block and run before protected registers need writes.

## Test Signals

Compile tests validate macro expansion and struct initialization. Runtime tests should verify that every function group string corresponds to a generated group name and that every GPIO pin has a matching `gpio_mux` entry.

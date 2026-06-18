# sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.h

## Purpose
Defines the private interface between pinctrl core and the pinmux implementation, including no-op stubs when pinmux or debugfs support is disabled and optional generic function helper declarations.

## Important APIs, Types, And Functions
Declares core pinmux helpers for operation validation, map validation, GPIO request/free/direction, map-to-setting conversion, setting enable/disable, debugfs display, and generic function management. Defines `struct function_desc` under `CONFIG_GENERIC_PINMUX_FUNCTIONS`.

## Control Flow
The header has no runtime flow, but preprocessor branches decide whether callers invoke real pinmux functions or inline stubs. With `CONFIG_PINMUX=n`, most operations return success or permissive defaults. With debugfs disabled, debug display hooks compile away.

## State And Persistence
No direct state is stored here. The generic `function_desc` type describes entries stored in a pinctrl device radix tree by `pinmux.c`.

## Dependencies And Integration Points
Consumed by pinctrl core and drivers that use internal generic function helpers. Depends on pinctrl core types, `struct dentry`, `struct seq_file`, and public `struct pinfunction` definitions.

## Risks
Stubbed behavior can mask missing pinmux support in builds where `CONFIG_PINMUX` is disabled. Any prototype mismatch with `pinmux.c` breaks core compilation. The generic helper declarations are only available when the corresponding Kconfig symbol is enabled.

## Test Signals
Build matrices with `CONFIG_PINMUX`, `CONFIG_DEBUG_FS`, and `CONFIG_GENERIC_PINMUX_FUNCTIONS` enabled and disabled provide the main signal, along with compile coverage of drivers using generic pinmux helpers.

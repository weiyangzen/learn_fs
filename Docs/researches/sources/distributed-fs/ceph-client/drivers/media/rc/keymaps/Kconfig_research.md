# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Kconfig

## Purpose

`drivers/media/rc/keymaps/Kconfig` declares `config RC_MAP`, the tristate build option that controls compilation of the kernel remote-controller keymap modules. It gates the large collection of small rc-core scan-code tables under `drivers/media/rc/keymaps`.

## Important APIs, Types, and Functions

- `config RC_MAP` is prompted as "Compile Remote Controller keymap modules".
- It depends on `RC_CORE`, so the maps are only buildable when the remote-controller core exists.
- It defaults to `y`, which makes in-kernel keymaps available by default.
- The help text points users who prefer userspace-loaded maps to `ir-keytable` from v4l-utils.

## Control Flow

There is no runtime control flow. Kconfig resolves `CONFIG_RC_MAP` to built-in, module, or disabled. Kbuild then evaluates the keymaps `Makefile`, building every `obj-$(CONFIG_RC_MAP)` entry as built-in objects or modules. At runtime, each built map registers itself with rc-core through its own init hook, unless it is a special rc-core-linked map such as CEC.

## State and Persistence Behavior

The only persistent state is the kernel `.config` value and the resulting build artifacts. No device state, key state, or user remap is stored here. Disabling the option removes the built-in map set, leaving userspace tooling or driver-specific defaults to supply maps.

## Dependencies and Integration Points

`RC_MAP` integrates the keymap directory with `RC_CORE`, the rc-core registry, module autoloading, and v4l-utils compatibility. It indirectly affects many receiver drivers whose default `map_name` values assume these maps are available in the kernel or loadable as modules.

## Risks and Edge Cases

Changing the default or dependency can remove expected keymaps from common media builds. If `RC_MAP=m`, drivers that request maps by name depend on module availability and aliases; if disabled, default remotes may produce raw scancodes but no key events until userspace loads a table. The help text references external tooling and can drift from current package names or URLs.

## Test Signals

Build matrix tests should cover `CONFIG_RC_MAP=y`, `=m`, and unset with `RC_CORE` enabled and disabled. Runtime signals include map lookup success for representative `RC_MAP_*` names, module autoload for map modules, and successful userspace fallback through `ir-keytable` when kernel maps are disabled.

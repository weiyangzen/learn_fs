# sources/distributed-fs/ceph-client/kernel/printk/console_cmdline.h

## Purpose

`console_cmdline.h` defines `struct console_cmdline`, the internal record used by printk to retain preferred console choices collected from kernel command-line options, platform defaults, device tree, SPCR, or subsystem prediction.

## Important type

`struct console_cmdline` contains `name[16]` for the console driver name, `index` for the minor or port index, `devname[32]` for firmware or device-name style console identifiers, `user_specified` to distinguish command-line entries from platform defaults, `options` for driver options, and optional `brl_options` when `CONFIG_A11Y_BRAILLE_CONSOLE` is enabled.

## Control flow

`printk.c` maintains a fixed array of these records. `console_setup()` fills entries from `console=` parameters. `add_preferred_console()` adds platform defaults. `match_devname_and_update_preferred_console()` resolves `devname` entries once a subsystem knows the eventual console driver and index. `try_enable_preferred_console()` consumes the records when drivers call `register_console()`.

## State and persistence behavior

These records persist for the life of the kernel. They are not dynamically allocated and are capped by `MAX_CMDLINECONSOLES` in `printk.c`. The `options` and `brl_options` fields point into boot option storage rather than owning copied strings.

## Dependencies and integration points

The header depends on `bool` being available from the including translation unit. Its optional `brl_options` member must stay aligned with the braille helper stubs and implementation. The structure is the contract between early boot parsing and later console registration, allowing console drivers to register after command-line parsing and still match earlier preferences. The `devname` field supports consoles whose tty driver identity is not known at early parameter time.

## Risks and test signals

Fixed-size `name` and `devname` buffers require bounded copies. Pointer fields rely on long-lived source strings. The fixed entry count means excess `console=` parameters fail with `-E2BIG`. Tests should cover explicit tty names, numeric serial shorthand, `DEVNAME:0.0` resolution, duplicate entries, platform defaults versus user-specified entries, and braille-enabled builds.

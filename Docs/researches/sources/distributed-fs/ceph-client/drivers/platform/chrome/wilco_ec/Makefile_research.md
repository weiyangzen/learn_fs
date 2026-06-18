<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Makefile

## Purpose

This Makefile maps Wilco EC Kconfig symbols to kernel objects and groups core source files into the `wilco_ec` module.

## Important APIs, Types, And Functions

`wilco_ec-objs` includes `core.o`, `keyboard_leds.o`, `mailbox.o`, `properties.o`, and `sysfs.o`. Optional modules are `wilco_ec_debugfs.o`, `wilco_ec_events.o`, and `wilco_ec_telem.o`, each built from its corresponding source file.

## Control Flow

Kbuild links the core object when `CONFIG_WILCO_EC` is enabled and links optional modules according to their symbols. Optional modules remain separate so they can be omitted or loaded independently.

## State And Persistence

No runtime state is defined here. It controls which translation units are linked into each module.

## Dependencies And Integration Points

The file integrates with Kbuild and the Kconfig symbols from the same directory. The object split mirrors the platform devices created by `core.c`.

## Risks

Moving a helper between core and optional modules must preserve exported symbols and module dependencies. The built-in keyboard LED helper means LED code is always part of the core module.

## Test Signals

Build each symbol combination and verify resulting module names and unresolved-symbol checks, especially optional modules using `wilco_ec_mailbox()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Makefile -->

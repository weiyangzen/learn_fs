# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa.h

## Purpose

`cyapa.h` is the shared private interface for Cypress APA trackpad support. It defines Gen3 register commands, PIP/TrueTouch command and response constants, power mode encodings, command-state structures, the main `struct cyapa`, the generation ops vtable, and cross-file helper prototypes used by `cyapa.c` and the generation-specific protocol files.

## Important APIs, Types, and Functions

Important constants include generation IDs (`CYAPA_GEN3`, `CYAPA_GEN5`, `CYAPA_GEN6`), SMBus command encoding macros, Gen3 operational/bootloader register bits, power modes (`PWR_MODE_FULL_ACTIVE`, `PWR_MODE_IDLE`, `PWR_MODE_SLEEP`, `PWR_MODE_BTN_ONLY`, `PWR_MODE_OFF`), PIP report IDs and command lengths, deep-sleep constants, and `CYAPA_MAX_MT_SLOTS`.

`struct cyapa_dev_ops` is the central polymorphic API for firmware checking/updating, baseline/calibration sysfs handling, initialization, state parsing, operational checking, IRQ handling, empty-output sorting, power-mode setting, and proximity control. `struct cyapa_pip_cmd_states` tracks command locks, completions, issued command, response buffers, IRQ/poll mode, PM stage, and scratch buffers. `struct cyapa` stores device state, bus/input/regulator pointers, power policy, product/firmware/geometry data, generation-specific electrode data, synchronization lock, ops pointer, and command states.

## Control Flow

The header does not execute directly. `cyapa.c` initializes a `struct cyapa`, selects one `cyapa_dev_ops` implementation after state parsing, then invokes its callbacks for operational checks, IRQ reporting, firmware update, and power management. Gen5/Gen6 PIP command helpers use the PIP constants and `cyapa_pip_cmd_states` to match command responses and synchronize IRQ-mode commands.

## State and Persistence Behavior

The main persistent state is `struct cyapa`, owned by the I2C client. `state`, `status`, `operational`, power modes, firmware/product fields, geometry, and command-state locks/completions persist until device removal. Firmware image persistence is handled by ops implementations declared here but not defined in this header. Sysfs-configured scanrates are in-memory fields.

## Dependencies and Integration Points

The header includes `<linux/firmware.h>` and relies on Linux I2C/input/regulator types being visible in users. It declares low-level read helpers, PIP command helpers, firmware update helpers, and extern ops tables from `cyapa_gen3.c`, `cyapa_gen5.c`, and `cyapa_gen6.c`. It binds all files into the `cyapatp` composite module listed in the Makefile.

## Risks and Edge Cases

The ops table is broad; missing or incompatible generation callbacks can break probe, IRQ, firmware update, or PM paths. PIP response macros assume exact report offsets and lengths. Power-mode macros cache the last device state and must remain consistent with actual hardware transitions. `CYAPA_MAX_MT_SLOTS` is tied to touch IDs and must match generation report formats. Several prototypes expose raw buffers and lengths, so callers must validate sizes before parsing.

## Test Signals

Build tests should verify all declared extern ops and helpers are defined by the composite module. Runtime and unit-style fixtures should validate PIP header macros, power conversion helpers, command completion matching, max slot assumptions, generation state transitions, and all `cyapa_dev_ops` callback coverage for Gen3/Gen5/Gen6.

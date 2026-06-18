# sources/distributed-fs/ceph-client/drivers/soc/apple/Makefile

## Purpose
This Makefile builds Apple SoC support modules from one or more implementation files.

## Important APIs, Types, And Functions
It creates `apple-mailbox.o` from `mailbox.o`, `apple-rtkit.o` from `rtkit.o` and `rtkit-crashlog.o`, `apple-sart.o` from `sart.o`, and `apple-tunable.o` from `tunable.o`.

## Control Flow
Kbuild includes each composite object based on its `CONFIG_APPLE_*` symbol. Composite object variables collect implementation files for module or built-in linking.

## State, Persistence, And Dependencies
Build state is determined by Kconfig. There is no runtime state.

## Integration Points
This file is reached from `drivers/soc/Makefile` through unconditional Apple directory recursion.

## Risks
Composite object names must match module expectations and exported symbols. If `rtkit-crashlog.o` is omitted, RTKit crash handling would fail to link.

## Test Signals
Build all Apple options as modules and built-ins and confirm generated module names and symbol exports.

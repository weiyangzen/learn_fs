<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/mellanox/Makefile

## Purpose

This Makefile maps Mellanox/Nvidia platform Kconfig symbols to their driver objects.

## Important APIs, Types, And Functions

It builds `mlx-platform.o`, `mlxbf-bootctl.o`, `mlxbf-pmc.o`, `mlxbf-tmfifo.o`, `mlxreg-dpu.o`, `mlxreg-hotplug.o`, `mlxreg-io.o`, `mlxreg-lc.o`, and `nvsw-sn2201.o` according to their corresponding `CONFIG_` symbols.

## Control Flow

Kbuild includes each driver independently as built-in or module. The object list mirrors the Kconfig feature list.

## State And Persistence

The Makefile has no runtime state.

## Dependencies And Integration Points

It integrates the Mellanox platform driver directory with Kbuild and the Kconfig file in the same directory.

## Risks

Object-symbol mismatches would lead to missing drivers or stale builds. Formatting inconsistency on a few lines is cosmetic but worth avoiding in future edits.

## Test Signals

Build every Mellanox platform symbol as built-in and module, and verify each expected object is linked with no unresolved dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Makefile -->

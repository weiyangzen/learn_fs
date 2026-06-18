# sources/distributed-fs/ceph-client/drivers/soc/amlogic/Makefile

## Purpose
This Makefile maps Amlogic SoC Kconfig symbols to their driver object files.

## Important APIs, Types, And Functions
It defines object selection for `meson-canvas.o`, `meson-clk-measure.o`, `meson-gx-socinfo.o`, and `meson-mx-socinfo.o`.

## Control Flow
Kbuild includes each object when its matching `CONFIG_MESON_*` symbol is enabled. There is no runtime flow.

## State, Persistence, And Dependencies
Build state is fully determined by `.config` symbols from `drivers/soc/amlogic/Kconfig`.

## Integration Points
It is reached from `drivers/soc/Makefile` via `obj-y += amlogic/`.

## Risks
Any symbol/object name mismatch prevents configured drivers from building. Since all entries are direct one-object drivers, missing module aggregation is low risk.

## Test Signals
Compile with each `CONFIG_MESON_*` option as built-in and module where applicable and confirm expected `.o` or `.ko` output.

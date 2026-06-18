# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/Makefile

## Purpose
This Makefile registers Socionext UniPhier arm64 board DTBs.

## APIs, Types, And Functions
It exposes one `dtb-$(CONFIG_ARCH_UNIPHIER)` assignment containing eight UniPhier DTB targets.

## Control Flow, State, And Persistence
Kbuild appends the target list when UniPhier support is enabled. There is no runtime state; the outputs are DTB files.

## Dependencies And Integration
The file depends on the listed UniPhier DTS sources and `CONFIG_ARCH_UNIPHIER`. It integrates with the arm64 DTB build pipeline.

## Risks And Test Signals
Risks are stale target names or missing board coverage. `make ARCH=arm64 dtbs` with UniPhier enabled should produce all listed DTBs.

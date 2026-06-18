# sources/distributed-fs/ceph-client/sound/hda/core/ext/Makefile

## Purpose
This Makefile builds the extended HDA core module used by ASoC/SOF-style HDA integrations that need bus, controller, and stream extensions.

## Important APIs, Types, and Functions
No runtime APIs are defined. The object group `snd-hda-ext-core-y` consists of `bus.o`, `controller.o`, and `stream.o`.

## Control Flow
`obj-$(CONFIG_SND_HDA_EXT_CORE)` includes `snd-hda-ext-core.o` when extended HDA core support is selected.

## State and Persistence Behavior
Build-only state. Runtime state is in the compiled extended core objects.

## Dependencies and Integration Points
It depends on `CONFIG_SND_HDA_EXT_CORE`, which selects the base HDA core in Kconfig. It integrates the ext subdirectory with Kbuild.

## Risks
Omitting any object breaks exported extended bus/link/stream symbols expected by ASoC HDA drivers.

## Test Signals
Build `SND_HDA_EXT_CORE` as module and built-in, and verify ext symbols resolve for consumers.

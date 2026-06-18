# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/rsnd.h

## Purpose

`rsnd.h` is the shared internal interface for the R-Car sound driver. It defines pseudo registers, module types and lifecycle operations, stream/DAI/private data structures, DT node names, generation flags, kcontrol helpers, and all cross-file function prototypes.

## Important APIs, types, and functions

`enum rsnd_reg` defines logical register IDs for SCU/SRC/CMD/CTU/MIX/DVC, ADG, SSIU, and SSI, with helper macros such as `SRCIN_TIMSEL(i)`, `CTU_SVxxR(i,j)`, and `SSI_BUSIF_MODE(i)`. `enum rsnd_mod_type` establishes module slots and ordering identifiers from synthetic DMA modules through SSIU. `struct rsnd_mod_ops` is the lifecycle vtable, including DMA request, probe/remove, init/quit, start/stop, IRQ, PCM creation, hw params/free, pointer, fallback, prepare/cleanup, status, ID overrides, and debugfs callbacks. `struct rsnd_mod`, `struct rsnd_dai_stream`, `struct rsnd_dai`, `struct rsnd_priv`, and `struct rsnd_kctrl_cfg*` define the main in-memory object model. The header also declares subsystem probe/remove APIs and convenience macros for stream direction, module lookup, and generation checks.

## Control Flow

The header enables the common pattern used by all modules: subsystem probe initializes arrays inside `rsnd_priv`, DT parsing connects module pointers into each `rsnd_dai_stream`, and `core.c` invokes lifecycle callbacks through `rsnd_mod_ops` in direction-specific order. Register users call `rsnd_mod_read/write/bset()` against pseudo registers instead of generation-specific offsets.

## State and Persistence Behavior

The structures declared here define all persistent driver state. `rsnd_priv` owns device-wide module arrays and DAI drivers. `rsnd_dai_stream` owns active stream links, conversion metadata, DMA module, flags, and runtime substream pointer. `rsnd_mod` owns lifecycle status and clock state. Kcontrol configs persist ALSA control values and update hooks.

## Dependencies and Integration Points

The header depends on Linux clock, device, DMA, IO, list, module, OF, workqueue, and ASoC/PCM headers. Every R-Car driver source in this directory, except standalone `msiof.c`, includes it. It also exposes debugfs helpers conditionally.

## Risks and Test Signals

Risks include ABI drift between vtable definitions and users, pseudo-register additions not mapped in `gen.c`, status-nibble macro errors, and misuse of stream/module lookup macros with NULL modules. Test signals include full-tree compilation with `CONFIG_DEBUG_FS` on/off, all generation probes, lifecycle balance under repeated triggers, and static analysis for unchecked module pointers.

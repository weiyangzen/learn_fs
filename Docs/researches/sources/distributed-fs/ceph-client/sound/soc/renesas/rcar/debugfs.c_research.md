# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/debugfs.c

## Purpose

`debugfs.c` provides optional debugfs views for R-Car sound DAIs and modules when `CONFIG_DEBUG_FS` is enabled. It lets developers inspect ADG clock state, per-module lifecycle status, and module-specific register windows under the ASoC component debugfs tree.

## Important APIs, types, and functions

`rsnd_debugfs_probe()` creates `rdaiN/playback` and `rdaiN/capture` files under the component debugfs root, skipping Gen1. `rsnd_debugfs_show()` emits ADG clock debug information, iterates modules in the selected stream, prints module name/status, and calls each module's `debug_info` callback. `rsnd_debugfs_reg_show()` prints raw 32-bit register rows from a base physical/MMIO pair. `rsnd_debugfs_mod_reg_show()` resolves module base physical and virtual addresses through `gen.c` and delegates to the raw register dump helper.

## Control Flow

The component driver in `core.c` points `.probe` at `rsnd_debugfs_probe`. Opening a debugfs file invokes the generated show function with the relevant `rsnd_dai_stream` as private data. Register dumps are passive reads using `__raw_readl()` and do not acquire the audio spinlock.

## State and Persistence Behavior

This file does not own persistent driver state beyond debugfs dentries automatically cleaned by ASoC component cleanup. It reads live module status and hardware registers, so output reflects the current stream state and may change while audio is running.

## Dependencies and Integration Points

It depends on debugfs, seq_file, `rsnd_adg_clk_dbg_info()`, `for_each_rsnd_mod()`, module `get_status` callbacks, and `rsnd_gen_get_phy_addr()/rsnd_gen_get_base_addr()`. Each module file can contribute its own debug register dump through `struct rsnd_mod_ops.debug_info`.

## Risks and Test Signals

Risks are NULL assumptions when a stream lacks SSI, racing live register changes, and incorrect base/offset ranges in module debug callbacks. Test signals include mounted debugfs paths for Gen2/Gen3/Gen4 devices, readable playback/capture files for every DAI, sane ADG and status output while idle/running, and no crashes for DAIs missing optional modules.

# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/gen.c

## Purpose

`gen.c` is the generation-specific register indirection layer. It maps logical `enum rsnd_reg` pseudo registers to MMIO regmap fields for Gen1, Gen2/Gen3, and Gen4, hiding different SRU/SCU/SSIU/SSI/ADG register layouts from the functional modules.

## Important APIs, types, and functions

`struct rsnd_gen` stores MMIO bases, physical resources, regmaps, per-pseudo-register `regmap_field` handles, and register names. `rsnd_mod_read()`, `rsnd_mod_write()`, and `rsnd_mod_bset()` are the exported accessors used everywhere else. `rsnd_gen_get_phy_addr()` and debug-only `rsnd_gen_get_base_addr()` expose base addresses for DMA calculations and debugfs. `_rsnd_gen_regmap_init()` maps a named resource, creates a regmap, allocates fields from a config table, and records register names. `rsnd_gen_probe()` chooses `rsnd_gen1_probe()`, `rsnd_gen2_probe()`, or `rsnd_gen4_probe()` from `rsnd_priv` generation flags.

## Control Flow

Generation probe allocates `struct rsnd_gen`, then initializes the resource groups required by that generation. Gen1 maps SSI and ADG. Gen2/Gen3 map SSI, SSIU, SCU, and ADG with 10 module IDs. Gen4 maps one SSIU, one SSI, ADG, and an SDMC resource with an empty register table. At runtime, module accessors verify the pseudo register exists for the generation, choose the instance index using `ops->id_cmd` when present or `rsnd_mod_id()` otherwise, and call regmap-field read/write/update operations.

## State and Persistence Behavior

MMIO mappings and regmap fields are devm-managed and persist for the device lifetime. The file does not cache register values; it provides forced writes/updates to hardware. Unsupported pseudo registers are logged and treated as no-op reads/writes rather than fatal errors.

## Dependencies and Integration Points

It depends on platform resources named `ssi`, `ssiu`, `scu`, `adg`, and `sdmc`, Linux regmap MMIO, and the pseudo-register enumeration in `rsnd.h`. ADG, SSI, SSIU, SRC, CMD, CTU, MIX, DVC, DMA, and debugfs all depend on these accessors.

## Risks and Test Signals

Risks include incorrect offsets or id strides, missing resource names in DT, silent no-op behavior for unsupported registers, and module ID callback mistakes. Tests should include probe on each generation, register smoke tests via debugfs, audio paths that touch every pseudo-register family, DMA physical address sanity checks, and negative DT tests for missing resources.

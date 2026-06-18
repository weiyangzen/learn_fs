# sources/distributed-fs/ceph-client/drivers/remoteproc/meson_mx_ao_arc.c

## Purpose

`meson_mx_ao_arc.c` is the Amlogic Meson8/Meson8b AO ARC remoteproc driver. It allocates the always-on SRAM from a gen_pool, configures AO remap and secure bus registers so the ARC core sees SRAM at address zero, controls ARC reset and clock, and loads generic ELF firmware through remoteproc.

## Important APIs, types, and functions

- `struct meson_mx_ao_arc_rproc_priv` stores remap and CPU register bases, SRAM virtual/physical address and size, gen_pool pointer, reset control, clock, and SECBUS2 regmap.
- `meson_mx_ao_arc_rproc_start()` enables the peripheral clock, programs ARM/media SRAM remap fields, updates `AO_SECURE_REG0`, resets the ARC, translates the SRAM physical address by subtracting `MESON_AO_RPROC_MEMORY_OFFSET`, and writes `AO_CPU_CNTL_RUN`.
- `meson_mx_ao_arc_rproc_stop()` writes `AO_CPU_CNTL_HALT` and disables the clock.
- `meson_mx_ao_arc_rproc_da_to_va()` maps ARC device addresses directly into the allocated SRAM because the core sees SRAM starting at 0.
- `meson_mx_ao_arc_rproc_ops` uses generic ELF boot address, load, and sanity-check helpers.

## Control flow

Probe optionally reads `firmware-name`, allocates the rproc, gets the `sram` gen_pool, allocates all available SRAM, validates that the physical address uses only allowed remap bits, obtains the `amlogic,secbus2` syscon, maps resources named `remap` and `cpu`, gets reset and clock, stores drvdata, and calls `rproc_add()`. Remove unregisters remoteproc and frees the SRAM allocation.

Start configures remap registers before releasing the ARC, then sets run control after a short reset delay. Stop halts the CPU and disables the clock. Address translation rejects any firmware address range beyond the SRAM size.

## State and persistence behavior

The driver owns a single gen_pool allocation for the remote firmware memory across the rproc lifetime. Register state persists in AO remap, AO CPU control, and secure bus registers until reset or reconfiguration. Stop halts the core and gates the clock but does not clear SRAM. Remove frees SRAM back to the pool.

## Dependencies and integration points

It depends on genalloc SRAM pools, syscon/regmap, reset, clock, platform resources, and remoteproc generic ELF helpers. DT must provide compatible `amlogic,meson8-ao-arc` or `amlogic,meson8b-ao-arc`, an `sram` pool, `amlogic,secbus2`, and `remap`/`cpu` memory resources.

## Risks and edge cases

- `priv->sram_size = gen_pool_avail()` then allocating that full amount can starve other users of the SRAM pool.
- The code contains hardware behavior learned by trial and error, including an `AO_CPU_CNTL_UNKNONWN` bit and a physical-address translation by subtracting `0x10000000`.
- `da + len` is not overflow-checked before comparing with `sram_size`.
- The driver allocates with `devm_rproc_alloc()` but calls non-devm `rproc_add()` and explicitly `rproc_del()` in remove; probe error cleanup must keep this pairing correct.

## Test signals

Build and boot on Meson8/Meson8b DTs with valid SRAM pool/remap resources. Tests should verify SRAM usable-bit validation, full-pool allocation and release, remap register values, reset/clock sequencing, firmware load at device address 0, rejection of out-of-range ELF segments, halt on stop, and repeated probe/remove or start/stop cycles.

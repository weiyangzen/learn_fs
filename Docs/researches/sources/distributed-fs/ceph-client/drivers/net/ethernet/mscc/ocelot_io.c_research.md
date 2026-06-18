# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_io.c

## Purpose
Centralizes Ocelot low-level register access through regmap. It maps logical registers to targets/offsets, exposes indexed accessors, per-port accessors, regfield allocation, and MMIO regmap initialization.

## Important APIs/types/functions
Exports `__ocelot_bulk_read_ix`, `__ocelot_read_ix`, `__ocelot_write_ix`, `__ocelot_rmw_ix`, `ocelot_port_readl`, `ocelot_port_writel`, `ocelot_port_rmwl`, `ocelot_regfields_init`, and `ocelot_regmap_init`. Also provides direct target-index read/write helpers.

## Control flow, state, persistence
Logical helpers call `ocelot_reg_to_target_addr`, warn on unresolved targets, then use regmap at `addr + offset`. Port helpers use the port target map. `ocelot_regfields_init` creates devm-managed fields in `ocelot->regfields`; `ocelot_regmap_init` maps MMIO and initializes a 32-bit, 4-byte-stride regmap. State is `ocelot->targets`, `ocelot->map`, `ocelot->regfields`, and a shared regmap config name during probe.

## Dependencies and integration
Used by nearly every Ocelot hardware-facing file. Depends on regmap, devm MMIO, and Ocelot register encoding.

## Risks and test signals
`WARN_ON(!target)` does not stop the access, and `ocelot_port_rmwl` is not an atomic regmap update. Test probe on all variants, regfield allocation, per-port access, stats bulk reads, and invalid map diagnostics.

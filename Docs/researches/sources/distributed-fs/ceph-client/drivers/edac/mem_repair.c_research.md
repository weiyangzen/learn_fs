# sources/distributed-fs/ceph-client/drivers/edac/mem_repair.c

## Purpose
Provides the generic EDAC memory-repair sysfs descriptor builder for RAS feature devices. It exposes a uniform set of attributes for repair technologies such as post-package repair, cacheline sparing, row/bank/rank sparing, address selection, DRAM location fields, and the write-only repair trigger.

## Important APIs, Types, And Functions
- `edac_repair_type[]` maps `enum edac_repair_type` values to stable strings and is exported for provider drivers.
- `struct edac_mem_repair_context` owns one named sysfs group, per-attribute `device_attribute` wrappers, and the attribute pointer array.
- `MR_ATTR_SHOW`, `MR_ATTR_STORE`, and `MR_DO_OP` generate the boilerplate show/store handlers that dispatch through `struct edac_mem_repair_ops`.
- `mem_repair_attr_visible` dynamically hides unsupported attributes or downgrades them to read-only when only the getter exists.
- `edac_mem_repair_get_desc` is the public descriptor API used by EDAC feature clients.

## Control Flow
A client calls `edac_mem_repair_get_desc(dev, attr_groups, instance)`. The helper validates inputs, allocates a devm-managed context, clones the static attribute templates, stamps each wrapper with the feature instance, initializes sysfs attributes, and publishes a group named `mem_repairN`. Runtime sysfs reads and writes recover the instance from the wrapper, fetch `edac_dev_feat_ctx` from the RAS feature device, select `ctx->mem_repair[inst]`, and call the provider's callback with the parent device plus provider-private data. The visibility callback runs before sysfs exposure and only returns a mode for callbacks present in the provider ops table.

## State And Persistence
State is devm-managed and persists for the lifetime of the client device. The file does not store repair parameters itself; it forwards all state to provider callbacks. The only exported static state is `edac_repair_type[]`. Attribute values, persistence mode, selected HPA/DPA, DRAM fields, and repair execution state live in the hardware/provider private data.

## Dependencies And Integration Points
Depends on `linux/edac.h`, `struct edac_dev_feat_ctx`, and `struct edac_mem_repair_ops`. It integrates with EDAC RAS feature devices through sysfs attribute groups and expects the RAS feature device's driver data to point at the feature context. Providers decide which attributes are meaningful by filling the getter/setter/do callbacks.

## Risks And Edge Cases
The generated handlers assume visible attributes always have the callback they call; visibility and ops setup must remain consistent. Numeric stores use base autodetection and perform no range checking beyond conversion, so providers must validate addresses, masks, channels, ranks, rows, and policy values. `sprintf(ctx->name, "mem_repair%d", instance)` relies on `EDAC_FEAT_NAME_LEN` being large enough. The write-only `repair` attribute passes the parsed integer directly to `do_repair`, so provider semantics for trigger values must be documented elsewhere.

## Test Signals
Useful tests instantiate providers with full, read-only, and sparse ops tables; verify only supported sysfs files appear with correct permissions; write invalid and out-of-range numeric values; confirm callback errors propagate as sysfs errors; and exercise multiple instances so each file dispatches to the correct `ctx->mem_repair[inst]`.

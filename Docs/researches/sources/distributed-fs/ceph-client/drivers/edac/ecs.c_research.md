# sources/distributed-fs/ceph-client/drivers/edac/ecs.c

## Purpose
This file implements the generic EDAC Error Check Scrub (ECS) sysfs descriptor builder. It is intended for on-die memory error-check scrub controls such as DDR5 ECS and creates per-FRU attribute groups that driver-specific ECS operations can service.

## Important APIs, Types, And Functions
`enum edac_ecs_attributes` defines `log_entry_type`, `mode`, `reset`, and `threshold`. `struct edac_ecs_dev_attr` wraps a `device_attribute` with a FRU id. `struct edac_ecs_fru_context` stores per-FRU name, attributes, attribute pointer array, and group. `struct edac_ecs_context` stores all FRU contexts.

Macro-generated show/store functions call `struct edac_ecs_ops` callbacks from `struct edac_dev_feat_ctx`. `ecs_attr_visible()` hides unsupported attributes or downgrades attributes to read-only when a getter exists without a setter. `edac_ecs_get_desc()` validates inputs and calls `ecs_create_desc()`.

## Control Flow
Consumers call `edac_ecs_get_desc(ecs_dev, attr_groups, num_media_frus)` while registering EDAC RAS features. The code allocates context with device-managed memory, allocates one FRU context per media FRU, initializes four attributes with the correct FRU id, initializes sysfs attributes, names each group `ecs_fruN`, attaches the attribute list and visibility callback, and stores each group into the caller-provided `attr_groups` array.

At sysfs access time, show functions find the FRU id from the attribute wrapper, look up ECS ops through device driver data, call the driver getter, and print the value. Store functions parse an unsigned long and call the corresponding setter or reset callback.

## State And Persistence
The file owns no hardware state. It allocates descriptor state with `devm_kzalloc()` and `devm_kcalloc()`, so it follows the client device lifetime. Actual ECS values are owned by the provider driver through `edac_ecs_ops` and its private context pointer.

## Dependencies And Integration Points
It depends on `linux/edac.h`, EDAC RAS feature context structures, sysfs attribute groups, and provider implementations of `edac_ecs_ops`. It is integrated by `edac_dev_register()` in `edac_device.c` when a feature entry has `RAS_FEAT_ECS`.

## Risks
The caller must provide enough `attr_groups` slots for all media FRUs; `edac_dev_register()` does this accounting. Store macros parse into `unsigned long` even when callbacks conceptually consume narrower values, so providers must validate ranges. Visibility is callback-based; missing ops silently hide files, which is intended but can obscure provider registration mistakes.

## Test Signals
Tests should cover invalid arguments, multiple FRUs, visibility with getter-only, setter-only, full read/write, and absent callbacks. Sysfs access tests should verify that the correct FRU id reaches each callback and that device-managed cleanup removes groups with the parent.

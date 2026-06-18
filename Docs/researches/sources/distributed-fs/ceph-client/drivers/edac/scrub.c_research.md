# sources/distributed-fs/ceph-client/drivers/edac/scrub.c

## Purpose
Provides the generic EDAC scrub sysfs descriptor builder for RAS feature devices. It exposes a uniform interface for scrub address, size, background enablement, and cycle-duration limits/current setting while delegating actual scrub control to provider callbacks.

## Important APIs, Types, And Functions
- `struct edac_scrub_context` owns one named scrub sysfs group and per-attribute wrappers.
- `EDAC_SCRUB_ATTR_SHOW` and `EDAC_SCRUB_ATTR_STORE` generate callback-backed sysfs handlers.
- `scrub_attr_visible` hides unsupported scrub attributes and makes getter-only attributes read-only.
- `scrub_create_desc` allocates and initializes the attribute group named `scrubN`.
- `edac_scrub_get_desc` is the public descriptor API for feature clients.

## Control Flow
Clients call `edac_scrub_get_desc(scrub_dev, attr_groups, instance)`. The helper validates inputs and creates a devm-managed context. `scrub_create_desc` builds local attribute templates for the requested instance, copies them into persistent context storage, initializes sysfs metadata, assigns group name/attrs/visibility, and writes the group into `attr_groups[0]`. Sysfs handlers recover the instance, fetch `edac_dev_feat_ctx`, select `ctx->scrub[inst]`, and call the provider's `edac_scrub_ops`.

## State And Persistence
The file persists only devm-managed descriptor state. Scrub configuration and progress are provider-owned. The generated sysfs files simply pass values through to parent-device callbacks with provider-private data.

## Dependencies And Integration Points
Depends on `linux/edac.h`, `struct edac_dev_feat_ctx`, `struct edac_scrub_ops`, sysfs attribute groups, and devm allocation. It integrates with the EDAC RAS feature framework rather than registering a standalone platform driver.

## Risks And Edge Cases
Visibility must match callbacks because generated handlers dereference provider ops directly. Conversion uses base autodetection and performs no generic range validation, so providers must validate address/size alignment, cycle bounds, and enable values. The descriptor writes only `attr_groups[0]`, so callers must provide storage and chain additional groups themselves.

## Test Signals
Instantiate providers with full, read-only, and sparse scrub ops; verify sysfs permissions; test invalid numeric stores and provider error propagation; confirm multiple instances dispatch correctly; and verify min/max/current cycle attributes appear according to callback availability.

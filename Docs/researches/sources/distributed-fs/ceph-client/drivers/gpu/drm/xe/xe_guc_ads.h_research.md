# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_ads.h

## Purpose

`xe_guc_ads.h` declares the public ADS lifecycle and policy API used by GuC initialization and runtime scheduler policy changes.

## Important APIs, Types, and Functions

- `xe_guc_ads_init()` allocates and sizes ADS storage before hwconfig is available.
- `xe_guc_ads_init_post_hwconfig()` recalculates size requirements after hwconfig and engine discovery.
- `xe_guc_ads_populate_minimal()` writes the minimal ADS needed for early GuC load.
- `xe_guc_ads_populate()` writes the full ADS for normal GuC upload/submission.
- `xe_guc_ads_populate_post_load()` fills data that is only available after GuC/submission initialization, notably golden LRC contents.
- `xe_guc_ads_scheduler_policy_toggle_reset()` updates GuC scheduler reset policy.

## Control Flow

Callers use this interface in phases: init allocation, minimal populate for hwconfig, post-hwconfig recalculation, full populate before firmware upload, post-load populate after default LRCs are captured, and optional runtime policy update through CT.

## State and Persistence Behavior

The header only forward-declares `struct xe_guc_ads`; state is defined in `xe_guc_ads_types.h` and owned by `struct xe_guc`. The functions mutate persistent ADS BO contents and metadata.

## Dependencies and Integration Points

It depends only on Linux types and a forward declaration, keeping ADS callers decoupled from the GuC ABI layout. It is included by `xe_guc.c` and other GuC/submission policy paths.

## Risks and Edge Cases

The phased API is order-sensitive. Calling full populate before post-hwconfig sizing or post-load populate before default LRCs exist can assert or produce invalid firmware data.

## Test Signals

Initialization integration tests should check call ordering and error propagation. Policy tests should verify reset enable/disable requests are reflected in CT actions.

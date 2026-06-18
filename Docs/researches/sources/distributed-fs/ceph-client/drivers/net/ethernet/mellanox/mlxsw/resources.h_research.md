# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/resources.h

## Purpose

`resources.h` defines the mlxsw resource catalog used by the Spectrum driver family to translate firmware-reported resource IDs into driver-visible capacity values. It is a compact state container and accessor layer for quantities such as KVD sizes, trap groups, counter pools, SPAN agents, FIDs, LAG limits, buffer dimensions, ACL TCAM and action limits, policers, virtual routers, RIFs, multicast eRIF list entries, and NVE multicast entries.

The header also carries three software-only resource IDs for computed KVD partition sizes: `KVD_SINGLE_SIZE`, `KVD_DOUBLE_SIZE`, and `KVD_LINEAR_SIZE`. These are not parsed from firmware; they are set internally by profile/resource registration code.

## Important APIs, Types, and Functions

`enum mlxsw_res_id` is the stable driver-side index namespace. `mlxsw_res_ids[]` maps queried hardware resource IDs, such as `0x1001` for `KVD_SIZE` and `0x2902` for `ACL_MAX_TCAM_RULES`, to the enum indexes.

`struct mlxsw_res` stores two parallel arrays, `valid[]` and `values[]`, indexed by `enum mlxsw_res_id`. The inline API is:

- `mlxsw_res_valid()` / `MLXSW_RES_VALID()` to test whether a resource was supplied or set.
- `mlxsw_res_get()` / `MLXSW_RES_GET()` to fetch a resource value, warning and returning zero when the value is not valid.
- `mlxsw_res_set()` / `MLXSW_RES_SET()` to mark a value valid and store it.
- `mlxsw_res_parse()` to consume a raw firmware ID/value pair and update the matching enum slot if the raw ID is known.

## Control Flow

Resource discovery code elsewhere queries firmware and calls `mlxsw_res_parse()` for each returned `(id, value)` pair. The parser linearly scans `mlxsw_res_ids[]`; on match it calls `mlxsw_res_set()` and returns. Unknown firmware IDs are ignored, which lets newer firmware expose resources older driver code does not understand.

Driver code later gates feature setup with `MLXSW_CORE_RES_VALID()` / `MLXSW_RES_VALID()` and reads limits with `MLXSW_CORE_RES_GET()` / `MLXSW_RES_GET()`. Spectrum resource registration in `spectrum.c`, KVDL setup in `spectrum1_kvdl.c` and `spectrum2_kvdl.c`, ACL setup, policers, counters, trap groups, RIFs, and port-range registers all rely on these values.

## State and Persistence Behavior

`struct mlxsw_res` is in-memory driver state populated during device bring-up. It persists for the life of the mlxsw core instance and is not a disk-backed configuration. Validity is explicit per resource; callers must not assume every enum entry is available on every ASIC or firmware version.

Because this is a header with `static` objects and inline functions, each translation unit gets its own private copy of `mlxsw_res_ids[]`. The array is read-only by convention, although it is not declared `const`.

## Dependencies and Integration Points

The header depends only on Linux kernel/types basics, but it is integrated through `core.h` and used broadly by Spectrum files. Resource IDs feed devlink resource registration, config profile sizing, ACL TCAM limits, KVDL allocator partition sizing, CPU policer/trap group programming, LAG limits, RIF capacities, and NVE capacities.

## Risks and Edge Cases

- `mlxsw_res_get()` warns on invalid resources but still returns zero. A caller that treats zero as a real capacity can silently disable or under-size a feature after a missing resource.
- `mlxsw_res_valid()`, `mlxsw_res_get()`, and `mlxsw_res_set()` do not bounds-check `res_id`; callers must pass only valid enum values.
- Unknown raw firmware IDs are ignored without logging, so resource discovery regressions require external tracing or later feature failures to notice.
- Software-only resources are intentionally absent from `mlxsw_res_ids[]`; they must be set by driver profile code, not expected from firmware.
- The non-`const` `mlxsw_res_ids[]` in a header creates a mutable per-translation-unit copy. Accidental writes would affect only one object file and be hard to diagnose.

## Test Signals

Useful validation includes booting Spectrum variants with resource query tracing, checking that required resources are valid before KVDL/ACL/router/trap initialization, and comparing `devlink resource show` output against firmware-reported KVD, counter, SPAN, policer, RIF, and port-range capacities. Static analysis should flag unchecked `MLXSW_RES_GET()` paths for resources that can be absent.

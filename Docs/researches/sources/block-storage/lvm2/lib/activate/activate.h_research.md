# File Research: sources/block-storage/lvm2/lib/activate/activate.h

## Role

`activate.h` is the public internal header for LVM2 activation services. It defines common status structures, activation options, target/module name constants, and the function surface used by commands, metadata code, reports, polling, and segment types.

## Key Types

- `struct lvinfo` captures generic DM state: existence, suspension, open count, major/minor, read-only state, live/inactive table flags, and read-ahead.
- `lv_seg_status_type_t` identifies parsed runtime status classes: cache, raid, snapshot, thin, thin pool, VDO pool, writecache, integrity, unknown, or none.
- `struct lv_seg_status` carries a segment pointer and a union of parsed libdm target status structures or `struct lv_status_vdo`.
- `struct lv_with_info_and_seg_status` joins generic LV info with one segment status for reporting paths that can use a single ioctl when possible.
- `struct lv_activate_opts` is the activation option bundle: exclusivity, origin-only behavior, merge suppression, message sending, skip-in-use, revert/resume flags, read-only/noscan/temporary flags, and optional component LV context.
- `struct dev_usable_check_params` is a bitfield policy for determining if a mapped device is safe for scanning/use.

## API Surface

The header declares:

- Global activation controls and driver/target/module queries.
- DM UUID lookup by devno or `struct device`.
- LV lifecycle operations and user-facing wrappers.
- Runtime status and percent helpers for snapshots, mirrors, RAID, cache, thin, VDO, writecache, and integrity-adjacent paths.
- Active/open LV counting and active-component/holder detection.
- Activation filters, read-only filters, transient checks, target-type checks, and PV-uses-VG dependency checks.
- dmeventd registration helpers behind `DMEVENTD`.
- `add_linear_area_to_dtree()` for segment code that needs a linear/striped wrapper target.
- `fs_unlock()` is declared here rather than exposing `fs.h` broadly, keeping fs fallback internals mostly private to activation.

## Constants

The file centralizes device-mapper target names such as `cache`, `writecache`, `integrity`, `error`, `linear`, `mirror`, `raid`, `snapshot`, `snapshot-merge`, `thin`, `thin-pool`, `vdo`, and `zero`. It also defines kernel module names, including special handling for VDO as `kvdo` rather than a `dm-` prefixed module.

## Dependency and Ownership Notes

This header includes `metadata-exported.h`, so it is designed for broad internal use without exposing all activation-private implementation details. It intentionally references many opaque or externally defined types from metadata, libdm, dmeventd, and device code through declarations or included headers.

## Invariants

- Callers that receive target-specific status structs are often responsible for destroying the associated memory pool, as documented by implementation comments.
- `lv_activate_opts` fields are used by both high-level activation and low-level tree construction; adding fields must account for both layers.
- Target name constants must match kernel/libdm names and segment-type expectations, because they are used for capability checks, table/status parsing, and module loading.

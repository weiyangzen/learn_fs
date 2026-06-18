# sources/distributed-fs/ceph-client/security/landlock/access.h

## Purpose

`access.h` defines Landlock access-mask storage, per-layer access matrices, and helpers shared by filesystem, network, scope, ruleset, and audit code. It is the core representation of which rights are handled, allowed, or still denied in each domain layer.

## Important APIs, Types, and Functions

`access_mask_t` is a `u32` bitmask. `struct access_masks` stores packed `fs`, `net`, and `scope` masks. `union access_masks_all` enables whole-mask comparisons. `struct layer_access_masks` stores one access mask per possible layer. `deny_masks_t` compactly records the layer that denied optional file rights. `_LANDLOCK_ACCESS_FS_INITIALLY_DENIED` contains rights such as `REFER` that are denied when any filesystem access is handled. `_LANDLOCK_ACCESS_FS_OPTIONAL` tracks file rights checked after open, currently truncate and device ioctl. `landlock_upgrade_handled_access_masks()` adds initially denied rights, and `access_mask_subset()` tests bit subset relations.

## Control Flow

Access checks initialize a `layer_access_masks` from a domain and requested access, then path or object rules unmask allowed bits. If every layer mask reaches zero, the request is allowed. Ruleset merging upgrades filesystem handled masks so refer remains initially denied.

## State and Persistence Behavior

This header defines in-memory bit layouts but stores no data itself. The layout is embedded in rulesets, credential/file blobs, and audit requests. Static assertions enforce that UAPI access bits fit and that layer counts align with packed deny-mask encoding.

## Dependencies and Integration Points

It depends on Landlock UAPI constants from `<uapi/linux/landlock.h>` and local limits. It is included by most Landlock source files.

## Risks and Test Signals

Adding new access rights requires updating masks, string tables, static assertions, and optional-deny encoding. Test signals include KUnit coverage for layer masks, deny masks, ruleset merge behavior, and ABI selftests for every UAPI bit.

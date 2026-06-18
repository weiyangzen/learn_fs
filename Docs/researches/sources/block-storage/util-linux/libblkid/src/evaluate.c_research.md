# File Research: sources/block-storage/util-linux/libblkid/src/evaluate.c

## Purpose
Implements high-level resolution of `LABEL=`, `UUID=`, `PARTLABEL=`, `PARTUUID=`, `ID=`, or raw paths to canonical device paths.

## Main Components
- Optional `verify_tag()` re-probes a udev-resolved device to confirm a symlink matches on-device metadata when `CONFIG_BLKID_VERIFY_UDEV` is enabled.
- `blkid_send_uevent()` writes an action to `/sys/dev/block/<maj>:<min>/uevent`.
- `evaluate_by_udev()` constructs `/dev/disk/by-*` symlink paths using `blkid_encode_string()`, stats/canonicalizes them, optionally verifies them, and may send change uevents for stale links.
- `evaluate_by_scan()` uses or creates a cache and calls `blkid_get_devname()` to scan/cache-resolve the token.
- `evaluate_tag()` parses combined `NAME=value` strings, reads config, follows configured evaluation order, and respects `BLKID_EVALUATE_NOPROBE`.
- Public wrappers: `blkid_evaluate_tag()`, `blkid_evaluate_tag2()`, and `blkid_evaluate_spec()`.
- `TEST_PROGRAM` main resolves one supplied tag/spec.

## Dependencies and Interactions
Ties together config parsing, cache scanning, udev symlink conventions, canonicalization, tag parsing, and optional device re-probing.

## Research Notes
If `blkid_evaluate_tag()` receives a token with no value and no `=`, it returns a duplicate of the token. `blkid_evaluate_spec()` canonicalizes plain paths but resolves parsed tags through the evaluation stack.

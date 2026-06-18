# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_pool.py

## Role

Implements pool lifecycle and pool mutation actions: create, stop, start, cache initialization, list, destroy, rename, add devices, grow devices, filesystem limits, overprovisioning mode, and alert-code explanation.

## Main Helpers

- `_generate_pools_to_blockdevs()` maps pools to block devices already using selected devnodes.
- `_check_opposite_tier()` prevents adding devices already used in the other tier.
- `_check_same_tier()` detects devices already in the same tier, distinguishing current pool from other pools.

## Main Actions

- `create_pool()` normalizes device paths, handles key/Clevis/integrity/journal options, calls `Manager.Methods.CreatePool`, and optionally sets overprovisioning.
- `stop_pool()` and `start_pool()` call manager stop/start APIs, with stopped-pool selection and unlock method handling.
- `init_cache()`, `add_data_devices()`, and `add_cache_devices()` validate devices and call pool methods.
- `destroy_pool()` and `rename_pool()` perform pool removal/name changes.
- `extend_data()` grows physical devices and distinguishes missing, expandable, unexpandable, and unchanged devices.
- `set_fs_limit()` and `set_overprovisioning_mode()` set pool properties.
- `explain_code()` maps alert codes through `PoolAlert`.

## Error Handling

Uses many CLI-specific errors: name conflicts, in-use devices across tiers, partial changes, no changes, no property changes, invalid option values, resource-not-found, engine errors, and incoherence errors.

## Notable Risk Areas

This file owns most state-changing pool behavior. Its correctness depends on preflight managed-object checks, absolute device paths, daemon return flags, and postcondition comparisons all matching stratisd behavior.

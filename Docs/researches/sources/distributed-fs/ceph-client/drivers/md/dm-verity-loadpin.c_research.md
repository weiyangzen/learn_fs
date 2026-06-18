# sources/distributed-fs/ceph-client/drivers/md/dm-verity-loadpin.c

## Purpose
`dm-verity-loadpin.c` lets LoadPin decide whether a block device is backed by a trusted dm-verity target. It compares a live verity target's root digest against a global list of trusted root digests supplied through LoadPin integration.

## Important APIs, Types, and Functions
The file defines the global `dm_verity_loadpin_trusted_root_digests` list and implements `dm_verity_loadpin_is_bdev_trusted()`. The helper `is_trusted_verity_target()` validates that a target is dm-verity, checks that its corruption mode is one of EIO/restart/panic rather than logging-only, obtains a copy of the root digest through `dm_verity_get_root_digest()`, and compares it with trusted entries.

## Control Flow
`dm_verity_loadpin_is_bdev_trusted()` rejects null devices and empty trust lists, resolves the mapped device from `bd_dev`, obtains the live table under SRCU, requires a singleton table, fetches target 0, and delegates to `is_trusted_verity_target()`. It then releases the live table and mapped device references before returning the trust result.

## State and Persistence Behavior
This file stores no persistent state. Its only state is the global trusted digest list, which is inspected but not modified here. It allocates a temporary digest copy via `dm_verity_get_root_digest()` and frees it after comparison.

## Dependencies and Integration Points
It depends on device-mapper internals (`dm.h`, `dm-core.h`), public dm-verity query helpers, and `linux/dm-verity-loadpin.h` for trusted digest structures. It integrates with LoadPin's filesystem trust decisions by answering whether a superblock's block device sits on an approved verity root.

## Risks and Test Signals
Risks include races around table lifetime, rejecting valid multi-target stacks, and trusting logging-mode verity devices that allow corrupted reads. Tests should cover null/non-DM devices, empty trust list, non-verity target, multi-target table, mode filtering, digest mismatch, digest match, and cleanup of allocated root digest copies.

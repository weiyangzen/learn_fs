# sources/distributed-fs/ceph/src/mds/FSMapUser.h

## Purpose

`FSMapUser.h` declares the compact, user/client-visible view of the filesystem map. It is smaller than `FSMap` and carries only the data needed to identify available CephFS filesystems by name and cluster ID plus the current map epoch and legacy default.

## Important APIs, Types, And Functions

`FSMapUser::fs_info_t` stores a filesystem `name` and `cid`, with feature-aware encode/decode. `FSMapUser` stores `filesystems`, `legacy_client_fscid`, and `epoch`.

Core methods are `get_epoch()`, `get_fs_cid(std::string_view name)`, `encode()`, `decode()`, `print()`, `print_summary()`, and `generate_test_instances()`. `WRITE_CLASS_ENCODER_FEATURES` registrations make both `fs_info_t` and `FSMapUser` available to Ceph's encoding/dencoder machinery. `operator<<` delegates to `print_summary()`.

## Control Flow And Data Flow

The class is a passive value object. Producers populate `filesystems` from the monitor's authoritative `FSMap`; encode transmits values to clients; decode reconstructs them; users call `get_fs_cid()` to resolve a name to ID. There is no daemon assignment or health logic here.

## State And Persistence Behavior

Encoded state is just epoch, legacy FSCID, and filesystem rows. The map key and each row's `cid` should match after decode, but the row's `cid` is the transmitted source of truth. No persistent state is kept outside the buffer encoding.

Because this type is feature-encoded but currently version 1, additions must preserve old client compatibility. The default values are `FS_CLUSTER_ID_NONE` for IDs and epoch 0.

## Dependencies And Integration Points

Dependencies include Ceph encoding, `fs_cluster_id_t`, `epoch_t`, `mdstypes.h`, `Formatter`, and C++ maps/strings. It integrates with `MFSMapUser` messages, `MDSMonitor` client session subscriptions, and client code that resolves named filesystems.

## Risks And Edge Cases

`get_fs_cid()` scans values and returns `FS_CLUSTER_ID_NONE` for both "not found" and the sentinel value, so callers cannot distinguish a missing name from an invalid/default ID without external validation. Duplicate filesystem names would make lookup order-dependent by numeric ID. The compact model can become stale; clients should compare epochs.

## Test Signals

Tests should cover default construction, name lookup, encode/decode round trips, operator stream output, and compatibility with monitor-generated messages. Negative tests should verify missing names return `FS_CLUSTER_ID_NONE` and empty maps print/encode without crashing.

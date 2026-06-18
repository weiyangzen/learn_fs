# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.h

## Purpose
Declares the public interface for the GuC context ID manager.

## Important APIs, Types, And Functions
The header forward-declares `struct drm_printer` and `struct xe_guc_id_mgr`, then declares initialization, locked reserve/release, unlocked PF range reserve/release, and print APIs.

## Control Flow
The split between `_locked` and non-locked functions mirrors the C implementation: submission paths use the locked form under the GuC submission lock; PF provisioning calls the range APIs that lock internally.

## State And Persistence
The state layout is opaque to callers. Callers own allocated IDs/ranges until released through the paired functions.

## Dependencies And Integration Points
Included by GuC submission and SR-IOV resource management code.

## Risks And Test Signals
Misusing locking variants is the main interface risk. Compile-time users plus the C file’s KUnit tests validate the contract.

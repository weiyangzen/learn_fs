# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.h

## Purpose
This header defines the kernel-side QAT configuration database structures and declares config-management functions.

## Important APIs, Types, And Functions
Important structures are `struct adf_cfg_key_val`, `struct adf_cfg_section`, and `struct adf_cfg_device_data`. Declared functions cover device config allocation/removal, debugfs add/remove, section add, full/partial deletion, key/value add, and value lookup.

## Control Flow
No executable flow exists. The structures are manipulated by `adf_cfg.c` and consumed by control/ioctl and generation config code.

## State And Persistence Behavior
The header defines volatile per-device config state: linked sections, linked key values, optional debugfs dentry, and a read/write semaphore.

## Dependencies And Integration Points
It includes Linux list/rwsem/debugfs and QAT config common/string/device headers. It is included by most configuration-aware QAT code.

## Risks
Fixed-size key/value/section arrays impose truncation boundaries. Exposing `struct adf_cfg_device_data` lets callers assume list layout, so changes need broad review.

## Test Signals
Build coverage plus config ioctl, generated defaults, debugfs `dev_cfg`, and config deletion/rebuild tests validate the header.

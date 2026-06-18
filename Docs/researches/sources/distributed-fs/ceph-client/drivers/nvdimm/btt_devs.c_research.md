# sources/distributed-fs/ceph-client/drivers/nvdimm/btt_devs.c

## Purpose
`btt_devs.c` implements the libnvdimm `nd_btt` device wrapper. It exposes sysfs configuration for BTT instances, manages BTT device allocation and release, probes existing BTT metadata on namespaces, validates arena superblocks, and selects BTT v1.1 versus v2.0 layout rules.

## Important APIs, Types, And Functions
Public functions are `to_nd_btt()`, `is_nd_btt()`, `nd_btt_create()`, `nd_btt_arena_is_valid()`, `nd_btt_version()`, and `nd_btt_probe()`. Internal creation is handled by `__nd_btt_create()`, while `__nd_btt_probe()` reads metadata and registers a discovered device.

Sysfs attributes include `sector_size`, `uuid`, `namespace`, `size`, and `log_zero_flags`. Supported BTT sector sizes include standard and integrity-tagged sizes: 512, 520, 528, 4096, 4104, 4160, and 4224 bytes.

## Control Flow
Seed creation uses `nd_btt_create()`, which allocates an empty `nd_btt`, names it `btt<region>.<id>`, initializes the device, and asynchronously registers it. Userspace can then set UUID, sector size, and namespace while the device is unbound. Probe of an existing namespace uses `nd_btt_probe()`: it ignores forced raw namespaces, accepts only none/BTT/BTT2 claim classes, creates an attached `nd_btt`, allocates a temporary superblock, and calls `__nd_btt_probe()`.

`__nd_btt_probe()` rejects namespaces smaller than 16 MiB, resolves BTT version with `nd_btt_version()`, copies external LBA size and UUID from the superblock, then registers the BTT device. If probe fails, the namespace is detached and the device reference is dropped.

## State And Persistence Behavior
This file owns volatile `nd_btt` configuration fields: UUID, LBA size, namespace claim pointer, size reported after BTT disk attach, version, and initial offset. Persistent state is read from `struct btt_sb` on the namespace. `nd_btt_arena_is_valid()` checks signature, parent namespace UUID when present, checksum, and logs the BTT arena error flag.

`nd_btt_version()` encodes the layout split: BTT2 starts at offset 0 with version 2.0, while legacy or unclaimed/BTT namespaces start at 4 KiB with version 1.1. This offset feeds `btt.c` via `nd_btt->initial_offset`, affecting every arena read/write.

## Dependencies And Integration Points
The file depends on BTT media structures from `btt.h`, namespace attach helpers from `claim.c`, common sysfs helpers from `core.c`, and namespace capacity/UUID helpers from `namespace_devs.c`. Device registration is through the NVDIMM bus helpers in `bus.c`. The actual block disk is created later by `btt.c`.

## Risks And Edge Cases
A BTT device cannot be reconfigured while bound because UUID and sector-size helpers reject active drivers. Incorrect claim-class handling can cause v1.1/v2.0 offset mismatch and failed discovery. `nd_btt_arena_is_valid()` temporarily zeroes `super->checksum` for validation and restores it; callers must pass mutable storage. The parent UUID check allows null parent UUID for compatibility.

## Test Signals
Tests should cover seed device sysfs writes before binding, `namespace` claim rejection for already claimed namespaces, forced-raw namespace skip, BTT1 and BTT2 metadata discovery, invalid signature/checksum/parent UUID rejection, minimum capacity enforcement, and `size` returning `-ENXIO` before the BTT driver is active.

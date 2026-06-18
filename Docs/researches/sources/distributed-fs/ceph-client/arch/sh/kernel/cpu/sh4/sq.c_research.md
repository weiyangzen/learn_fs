# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/sq.c

## Purpose
`sq.c` implements the SH4 Store Queue mapping API, allowing physical I/O regions to be mapped into the store-queue address window and flushed efficiently.

## Important APIs, Types, And Functions
Public exports are `sq_flush_range()`, `sq_remap()`, and `sq_unmap()`. Internal state includes `struct sq_mapping`, `sq_mapping_list`, `sq_mapping_lock`, `sq_cache`, `sq_bitmap`, sysfs `mapping` attribute, CPU hotplug `sq_interface`, and module init/exit.

## Control Flow
`sq_api_init()` creates a slab cache, allocates a bitmap for the 64 MiB SQ window, and registers a CPU subsystem interface that creates per-CPU `sq` sysfs directories. `sq_remap()` validates non-RAM physical ranges, allocates a mapping, reserves bitmap pages, maps through `ioremap_page_range()` or QACR registers, logs the mapping, and links it. `sq_unmap()` finds the mapping, releases bitmap space, removes VM area on MMU builds, unlinks, and frees it. Sysfs writes map when length is nonzero and unmap when length is zero.

## State And Persistence
Mappings persist in kernel memory until explicit unmap or module exit. Hardware state includes QACR registers on no-MMU builds and store queue contents flushed by prefetch/barrier operations.

## Dependencies And Integration Points
It integrates with vmalloc/ioremap, bitmap allocation, slab, CPU sysfs, cache flush semantics, and `cpu/sq.h` address constants. Other drivers can call exported SQ APIs.

## Risks
`sq_unmap()` walks `sq_mapping_list` without taking the list lock until deletion, so concurrent sysfs/API access deserves scrutiny. Physical-address validation rejects normal RAM but relies on `high_memory`. Sysfs accepts raw hex input and can expose privileged footguns.

## Test Signals
Module init logs, sysfs mapping create/remove, driver SQ API use, concurrent map/unmap stress, no-MMU QACR behavior, and data-transfer flush correctness are the main signals.

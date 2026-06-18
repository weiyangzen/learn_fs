# sources/distributed-fs/ceph-client/arch/arm64/mm/mmap.c

## Purpose
This file defines ARM64 user VMA protection translation and `/dev/mem` physical range validation. It maps generic `vm_flags` combinations to ARM64 `pgprot_t` values, adjusts that table for features such as Enhanced PAN and LPA2, and adds feature-specific bits for GCS, BTI, MTE, and permission overlays.

## Important APIs, Types, and Functions
The important data is `protection_map[16]` and `gcs_page_prot`. The main functions are `valid_phys_addr_range()`, `valid_mmap_phys_addr_range()`, initcall `adjust_protection_map()`, and exported `vm_get_page_prot()`.

## Control Flow
`valid_phys_addr_range()` accepts `/dev/mem` reads/writes only when the whole range is memblock memory and the start address is map memory. `valid_mmap_phys_addr_range()` rejects mmap requests beyond `PHYS_MASK`. During `adjust_protection_map()`, Enhanced PAN converts execute-only entries from readable executable to `PAGE_EXECONLY`, and LPA2 clears `PTE_SHARED` from all protections and GCS protection.

`vm_get_page_prot()` selects GCS shadow-stack protection if supported and requested, otherwise indexes `protection_map` by read/write/exec/shared flags. It then adds `PTE_GP` for BTI, Normal-Tagged memory attributes for MTE mappings, and POE pkey bits when supported.

## State and Persistence
`protection_map` and `gcs_page_prot` are initialized once and then become read-only after init. There is no per-VMA persistence in this file beyond the protection bits returned to generic mmap/mprotect paths.

## Dependencies and Integration Points
The file depends on memblock for `/dev/mem` validation and on ARM64 CPU feature helpers for EPAN, LPA2, GCS, MTE, BTI, and POE. It integrates directly with generic MM through `vm_get_page_prot()` and with userspace ABI flags such as `VM_MTE`, `VM_ARM64_BTI`, `VM_SHADOW_STACK`, and pkey flags.

## Risks
Protection-bit composition is security-sensitive. Incorrect execute-only handling can expose readable executable mappings; missing BTI or MTE attributes can break user ABI promises; wrong LPA2 shareability bits can produce invalid descriptors. `/dev/mem` checks can be too strict across adjacent memblock regions with differing attributes, as noted in the source comment.

## Test Signals
Signals include mmap/mprotect tests for read/write/execute combinations, EPAN execute-only behavior, BTI-enabled mappings, MTE `PROT_MTE` mappings, GCS shadow-stack VMAs, POE pkey behavior, and `/dev/mem` range validation tests. Boot-time feature combinations with LPA2 are especially useful for catching descriptor-bit mistakes.

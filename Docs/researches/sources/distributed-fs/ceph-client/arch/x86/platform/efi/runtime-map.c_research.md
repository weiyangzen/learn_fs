<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/runtime-map.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/runtime-map.c

## Purpose
Exports the active EFI runtime memory map through sysfs and provides helper APIs for copying the map to other kernel consumers.

## Important APIs, Types, And Functions
`struct efi_runtime_map_entry` wraps an `efi_memory_desc_t` in a kobject. `map_attribute` and the generated show functions expose `type`, `phys_addr`, `virt_addr`, `num_pages`, and `attribute`. `efi_get_runtime_map_size()`, `efi_get_runtime_map_desc_size()`, and `efi_runtime_map_copy()` are programmatic accessors.

## Control Flow
At `subsys_initcall_sync`, the initializer exits if EFI memory maps or `efi_kobj` are absent. It allocates a pointer array, creates the `runtime-map` kset under the EFI kobject, and adds numbered child kobjects for each descriptor. Attribute reads format descriptor fields as hexadecimal strings.

## State And Persistence
The sysfs hierarchy persists until shutdown and holds heap copies of EFI descriptors. The source of truth remains `efi.memmap`; `efi_runtime_map_copy()` copies from that live map, not the per-kobject snapshots.

## Dependencies And Integration Points
Integrates with EFI core, sysfs/kobject lifecycle, and `/sys/firmware/efi/runtime-map`. Kexec and diagnostic users can use the exported copy helpers.

## Risks And Edge Cases
Partial sysfs creation unwinds only created kobjects; kset lifetime errors can leak or remove the whole map. The copy helper silently truncates to caller buffer size. Descriptor values are read-only and not synchronized against later EFI memory-map replacement.

## Test Signals
Presence of `/sys/firmware/efi/runtime-map/N/*` with sane descriptor values, successful boot without kobject warnings, and consumers receiving a descriptor-size-aligned map validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/runtime-map.c -->

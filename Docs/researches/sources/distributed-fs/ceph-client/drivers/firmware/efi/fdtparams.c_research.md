# sources/distributed-fs/ceph-client/drivers/firmware/efi/fdtparams.c

Purpose: extracts EFI system-table and memory-map parameters from the flattened device tree for architectures that receive EFI boot metadata through `/chosen` or Xen's `/hypervisor/uefi` node.

Important APIs/types/functions: exports init-only `efi_get_fdt_params()`. Helper `efi_get_fdt_prop()` reads 32-bit or 64-bit big-endian properties into target variables and logs values under `efi=debug`.

Control flow: `efi_get_fdt_params()` checks `initial_boot_params`, then searches known nodes in priority order. For each found node it reads system table, memmap base, memmap size, descriptor size, and descriptor version properties. Missing system-table property falls through to the next node; missing later properties abort EFI discovery. Xen/paravirt nodes set `EFI_PARAVIRT`.

State and persistence behavior: fills the caller's `struct efi_memory_map_data` and returns the EFI system-table address. It may set an EFI flag; no additional state is retained.

Dependencies and integration points: used by `efi_init()` on FDT-based EFI boots. Depends on libfdt, initial boot params, unaligned big-endian reads, and optional Xen property names.

Risks and test signals: incorrect DT property sizes or absent required properties disable EFI init. 64-bit values are saturated when stored into 32-bit descriptor-size/version fields. Test signals include `efi=debug` property logs, successful EFI boot through `/chosen`, and `EFI_PARAVIRT` set for Xen-provided UEFI parameters.

# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64.c

Purpose: implements arm64 EFI stub platform feature checks, virtual-address-map workaround selection, cache synchronization/remapping, and final kernel entry.

Important APIs/types/functions: key functions are `check_platform_features()`, `efi_cache_sync_image()`, weak `primary_entry_offset()`, and `efi_enter_kernel()`. Helper `system_needs_vamap()` identifies Ampere systems needing `SetVirtualAddressMap()`.

Control flow: feature checks set `efi_novamap` when 48-bit TTBR0 mappings allow 1:1 runtime access and the system is not an Ampere eMAG/Altra workaround case. Non-4K page kernels verify CPU translation granule support. Cache sync cleans data cache lines for code when IDC is absent, invalidates instruction cache, executes barriers, then calls `efi_remap_image()`. Final entry adds `primary_entry_offset()` to the entry point and calls the kernel with FDT address and zeroed registers.

State and persistence behavior: may set global stub state `efi_novamap`; otherwise stateless.

Dependencies and integration points: depends on ARM64 CPU feature registers, SMBIOS records/strings, EFI remap helpers, cache maintenance instructions, and common stub entry.

Risks and test signals: wrong granule detection can boot unsupported kernels; skipping virtual address map on affected Ampere systems breaks runtime `SetTime()`. Test signals include 16K/64K page rejection on unsupported CPUs, Ampere workaround log, and successful kernel entry after cache sync/remap.

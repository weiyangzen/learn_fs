# sources/distributed-fs/ceph-client/arch/x86/xen/efi.c

Purpose: Builds a paravirtual EFI system table for Xen initial domains and initializes Linux EFI flags/secure-boot state using Xen firmware-info hypercalls.

Important APIs/types/functions: `xen_efi_probe()` queries EFI config tables, vendor, firmware version, and runtime version through `XENPF_firmware_info`, then calls `xen_efi_runtime_setup()`. `xen_efi_get_secureboot()` uses EFI variables and shim MokSBState to classify secure boot. `xen_efi_init()` writes the Xen EFI signature and table address into `boot_params`, sets `boot_params->secure_boot`, and marks `EFI_BOOT`, `EFI_PARAVIRT`, and `EFI_64BIT`.

Control flow and state: EFI probing is limited to `xen_initial_domain()`. Static initdata holds the synthetic EFI table and vendor buffer. Runtime services pointers are intentionally invalid because runtime calls are handled through Xen-specific setup.

Dependencies and integration points: It integrates Xen platform firmware ops with generic Linux EFI boot parameter processing, secure boot policy, and PVH/PV early boot paths.

Risks and test signals: Incorrect table addresses or flags can break EFI config-table discovery in Dom0. Secure boot classification must respect shim insecure mode. Test signals include Xen Dom0 EFI boot, correct `efi=runtime` behavior through Xen hooks, secure boot reporting, and graceful no-op on non-initial domains.

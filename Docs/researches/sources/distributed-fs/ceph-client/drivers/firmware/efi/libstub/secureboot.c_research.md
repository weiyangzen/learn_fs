
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/secureboot.c

Purpose: determines UEFI Secure Boot mode for the EFI stub, with shim MOK insecure-mode override handling.

Important APIs/types/functions: exports `efi_get_secureboot()`. Internal `get_var()` adapts EFI variable access to `efi_get_secureboot_mode()`.

Control flow: the function calls the generic secure-boot mode helper. If enabled, it checks shim's `MokSBStateRT` variable under `EFI_SHIM_LOCK_GUID`; a non-nonvolatile value of 1 disables secure boot from the kernel's perspective. Otherwise it logs that secure boot is enabled.

State and persistence behavior: reads EFI variables only; it does not modify state. The returned enum is stored by callers such as x86 boot params.

Dependencies and integration points: depends on EFI runtime variable access and shim variable conventions. FDT code uses the result to reject unauthenticated `dtb=` loads under secure boot.

Risks and test signals: inability to determine mode returns unknown and callers may conservatively treat it as secure. Shim variable attributes matter; nonvolatile insecure state is not honored here. Test signals include SecureBoot on/off, SetupMode-like platform states, shim insecure mode, variable read failure, and x86 `boot_params->secure_boot` propagation.

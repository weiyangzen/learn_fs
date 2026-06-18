# sources/distributed-fs/ceph-client/security/integrity/efi_secureboot.c

Purpose: exposes architecture secure-boot status to the integrity subsystem by querying EFI secure boot mode safely after EFI runtime support is available.

Important APIs, types, and functions: key functions are `get_sb_mode()` and `arch_get_secureboot()`. It uses `arch_efi_boot_mode` when provided, `efi_get_secureboot_mode()`, `efi_rt_services_supported()`, and `efi_enabled(EFI_BOOT)`.

Control flow: `arch_get_secureboot()` lazily initializes static state once. If EFI boot is active, it uses an architecture-provided mode or queries EFI variables; it returns true only for `efi_secureboot_mode_enabled`.

State and persistence: caches `sb_mode` and `initialized` statically for subsequent calls. It logs mode status.

Dependencies and integration: integrates with EFI runtime services, architecture EFI hooks, and integrity policy decisions that depend on secure boot.

Risks and test signals: calling too early can hang, which the comment explicitly warns against. Test signals include EFI-disabled, runtime-variable unsupported, arch-provided enabled/disabled, and queried enabled/disabled/unknown modes.

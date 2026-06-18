
# sources/distributed-fs/ceph-client/drivers/firmware/efi/reboot.c

Purpose: routes system reboot and optional poweroff through EFI ResetSystem runtime services, honoring firmware quirks and pending capsule update reset requirements.

Important APIs/types/functions: exports `efi_reboot()`, weak `efi_poweroff_required()`, and global `efi_reboot_quirk_mode`. Internal `efi_power_off()` and `efi_shutdown_init()` register a sys-off handler when needed.

Control flow: reboot first checks ResetSystem support, maps Linux reboot mode to EFI warm/cold, applies quirk override, checks pending capsule update reset mode and logs if it changes the requested reset type, then calls `efi.reset_system()`. Late init registers an EFI shutdown handler before ACPI poweroff if the architecture/platform requires EFI poweroff.

State and persistence behavior: `efi_reboot_quirk_mode` can be set by platform quirks. `efi_sys_off_handler` stores the registered poweroff handler.

Dependencies and integration points: depends on EFI runtime service wrappers, capsule update state, Linux reboot/sys-off framework, and platform overrides of `efi_poweroff_required()`.

Risks and test signals: ResetSystem may not return but firmware failures can leave system running. Capsule reset mode must override user-requested warm/cold resets. Test signals include warm/cold reboot, quirk-forced modes, pending capsule update, unsupported runtime reset service, and EFI-required poweroff systems.

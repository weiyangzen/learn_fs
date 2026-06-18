# sources/distributed-fs/ceph-client/drivers/firmware/efi/Kconfig

Purpose: defines EFI firmware feature switches for ESRT, efivars pstore, special-purpose memory reservation, DXE memory attributes, FDT-derived parameters, runtime wrappers, generic/zboot stubs, DTB loader, bootloader control, capsule loader, EFI tests, Apple properties, reset attack mitigation, RCI2 table support, early PCI DMA disabling, and EFI early console.

Important APIs/types/functions: Kconfig symbols include `EFI_ESRT`, `EFI_VARS_PSTORE`, `EFI_VARS_PSTORE_DEFAULT_DISABLE`, `EFI_SOFT_RESERVE`, `EFI_DXE_MEM_ATTRIBUTES`, `EFI_PARAMS_FROM_FDT`, `EFI_RUNTIME_WRAPPERS`, `EFI_GENERIC_STUB`, `EFI_ZBOOT`, `EFI_ARMSTUB_DTB_LOADER`, `EFI_BOOTLOADER_CONTROL`, `EFI_CAPSULE_LOADER`, `EFI_CAPSULE_QUIRK_QUARK_CSH`, `EFI_TEST`, `EFI_DEV_PATH_PARSER`, `APPLE_PROPERTIES`, `RESET_ATTACK_MITIGATION`, `EFI_RCI2_TABLE`, `EFI_DISABLE_PCI_DMA`, and `EFI_EARLYCON`.

Control flow: no runtime control flow. The symbols select objects in the EFI Makefiles, enable boot-stub paths, and gate runtime services, sysfs, pstore, capsule, and platform quirk features.

State and persistence behavior: state is build configuration persisted in `.config`; it determines which EFI facilities exist in the built kernel or modules.

Dependencies and integration points: integrates with global `EFI`, `EFI_STUB`, `PSTORE`, `ACPI_HMAT`, `X86`, architecture-selected `EFI_PARAMS_FROM_FDT`, `UCS2_STRING`, and EFI runtime/device-path consumers.

Risks and test signals: risky options include capsule loading, runtime tests, reset attack mitigation, DXE memory attribute changes, and early PCI busmaster disabling because they depend heavily on firmware behavior. Test signals are matrix builds for symbol combinations and runtime visibility of `/sys/firmware/efi`, `/dev/efi_capsule_loader`, pstore backend registration, and early console behavior when selected.

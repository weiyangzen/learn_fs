# sources/distributed-fs/ceph-client/drivers/firmware/efi/efibc.c

Purpose: implements EFI Bootloader Control by writing bootloader variables during reboot so compatible bootloaders can perform a one-shot boot entry selection and know the reboot reason.

Important APIs/types/functions: key functions are `efibc_set_variable()`, `efibc_reboot_notifier_call()`, `efibc_init()`, and `efibc_exit()`. It registers `efibc_reboot_notifier`.

Control flow: module init requires EFI `SetVariable` runtime support, then registers a reboot notifier. On reboot/shutdown, the notifier writes `LoaderEntryRebootReason` as `reboot` or `shutdown`. If reboot command data is present, it copies up to 511 bytes into UCS-2 and writes `LoaderEntryOneShot`.

State and persistence behavior: state is stored in nonvolatile EFI variables under `LINUX_EFI_LOADER_ENTRY_GUID`, so it survives until consumed/cleared by the bootloader.

Dependencies and integration points: depends on EFI runtime `set_variable`, reboot notifier chain, UCS-2 strings, and bootloaders honoring the LoaderEntry variables.

Risks and test signals: runtime variable writes can fail due to firmware policy, full variable store, or missing runtime services. Test signals include variables appearing before reset, bootloader performing the one-shot entry, and clean notifier unregister on module removal.

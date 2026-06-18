# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-pstore.c

Purpose: registers EFI variables as a pstore backend for crash/dmesg records, storing and enumerating records under the `LINUX_EFI_CRASH_GUID` namespace.

Important APIs/types/functions: main pstore callbacks are `efi_pstore_open()`, `efi_pstore_close()`, `efi_pstore_read()`, `efi_pstore_write()`, and `efi_pstore_erase()`. Helpers include `efi_pstore_read_func()`, `generic_id()`, `efivars_pstore_init()`, `efivars_pstore_exit()`, and the runtime `pstore_disable` parameter setter.

Control flow: module init checks EFI variable write support and the disable flag, clamps `record_size` to at least 1024, allocates the pstore buffer, and calls `pstore_register()`. Reads lock efivars, enumerate variables with `efivar_get_next_variable()`, filter by crash GUID, parse legacy and current `dump-type...` names, read variable data, and store a UCS-2 name copy for later erase. Writes format a UCS-2 variable name with type/part/count/time/compression, try-lock efivars, and set a nonvolatile runtime variable. Erase sets the variable size to zero.

State and persistence behavior: crash records persist in EFI nonvolatile variable storage across reboot until erased. Runtime state includes the pstore buffer, enumeration name buffer in `psi->data`, and module parameters.

Dependencies and integration points: depends on the EFIVAR namespace API, pstore core, UCS-2 conversion, EFI variable runtime services, and firmware variable-store capacity/quirks.

Risks and test signals: EFI variable stores are small and firmware-specific; write failures, enumeration size quirks, lock contention, and excessive record fragmentation are important risks. Test signals include pstore registration, crash records under pstore after reboot, successful erase, `pstore_disable` toggling registration, and sane behavior when writes are unsupported.

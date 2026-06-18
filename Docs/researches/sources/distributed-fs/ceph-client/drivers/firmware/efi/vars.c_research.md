# sources/distributed-fs/ceph-client/drivers/firmware/efi/vars.c

Purpose: Implements the common EFI variable operation registry and serialized helper API used by variable filesystems and alternate EFI backends.

Important APIs/types/functions: Global `__efivars` points to the active backend. `efivars_register()` and `efivars_unregister()` install/remove one `struct efivars`. `efivar_lock()`, `efivar_trylock()`, and `efivar_unlock()` expose serialization. Helper wrappers include `efivar_get_variable()`, `efivar_get_next_variable()`, `efivar_set_variable_locked()`, `efivar_set_variable()`, `efivar_query_variable_info()`, `efivar_is_available()`, and `efivar_supports_writes()`.

Control flow: Registration takes the semaphore, rejects a second backend, stores ops, emits notifier state for read-only/read-write capability, and logs success. Set-variable calls validate variable-store capacity via `query_variable_store` or a 64 KiB fallback, select blocking or nonblocking set ops, then call the backend under the required lock.

State and persistence behavior: Maintains one global backend pointer and semaphore. It does not store EFI variables directly, but all persistent NVRAM mutations route through backend ops. Notifier events inform other subsystems when operations become available.

Dependencies and integration points: Integrates Linux EFI type definitions, UCS-2 sizing, EFIVAR namespace exports, notifier chain `efivar_ops_nh`, and backend drivers such as generic EFI runtime services, GSMI, and TEE STMM.

Risks and test signals: Callers must hold the lock for low-level helpers; missing `__efivars` checks in some helpers assume proper availability sequencing. Backend replacement must avoid races with users. Tests should cover double registration, unregister mismatch, lock failure paths, nonblocking set behavior, variable size checks, and notifier behavior on read-only vs read-write backends.

# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks.c

Purpose: Provides the core Power LPAR Platform KeyStore implementation: configuration discovery, OS password management, object label/auth construction, read/write/remove/signed-update APIs, wrapping-key operations, and kexec password handoff.

Important APIs/types/functions: Defines `struct plpks_auth`, label structures, cached config globals, `pseries_status_to_err()`, `_plpks_get_config()`, `plpks_is_available()`, config getters, `plpks_signed_update_var()`, `plpks_write_var()`, `plpks_remove_var()`, read wrappers for OS/firmware/bootloader owners, `plpks_gen_wrapping_key()`, `plpks_wrap_object()`, `plpks_unwrap_object()`, `plpks_populate_fdt()`, and `plpks_early_init_devtree()`.

Control flow: Early boot may recover an existing OS password from `/chosen/ibm,plpks-pw` and nop it from the FDT. Arch init checks the firmware feature, fetches and validates PLPKS config with `H_PKS_GET_CONFIG`, then generates or reuses an OS owner password. Object operations build aligned auth and label buffers, call the relevant `H_PKS_*` hcall, map hypervisor status to errno, and for mutating operations wait for object flush confirmation.

State and persistence: Static globals cache the OS password and config values (`version`, sizes, policies, wrapping flags, used space). PLPKS objects persist in hypervisor storage. Kexec persistence is handled by embedding the password into the next FDT and clearing it early on the next boot.

Dependencies and integration points: Used by secvar, SED, sysfs, secure-boot wrapping, kexec, FDT code, memblock, PAPR hcall wrappers, and firmware feature detection.

Risks: Password buffers and auth/label structures must satisfy hypervisor alignment and page-boundary constraints. Long-busy signed updates and object flush polling can time out. Wrapping/unwrap output length arithmetic assumes wrapped objects are at least the fixed overhead. `plpks_is_available()` refreshes config on every call, which has side effects on cached fields.

Test signals: PLPKS available/unavailable boot, kexec password carryover, read/write/remove OS variables, signed update policies, object flush timeout, config validation failures, wrapping-key generation idempotency, wrap/unwrap round trips, and sensitive-buffer leak checks.

Source read size: 1379 lines, 38660 bytes.

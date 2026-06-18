<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/vars.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/vars.c

## Purpose
`vars.c` wraps EFI runtime variable enumeration and access for efivarfs and validates writes to sensitive UEFI variables. It converts EFI names to efivarfs filenames, identifies variables safe to remove, and serializes firmware access through the EFIVAR lock.

## Important APIs, types, and functions
Important helpers include validators for device paths, boot order, load options, uint16 values, and ASCII strings; `variable_matches`; `efivar_get_utf8name`; `efivar_validate`; `efivar_variable_is_removable`; `efivar_init`; `efivar_entry_delete`; `efivar_entry_size`; `__efivar_entry_get`; `efivar_entry_get`; and `efivar_entry_set_get_size`. The static `variable_validate` table is both a validation table and removable whitelist.

## Control flow
Variable names are converted from UCS-2 to UTF-8, suffixed with `-GUID`, and slash characters are replaced with `!`. Validation converts the UCS-2 name to UTF-8, finds vendor/name patterns including wildcards, and invokes type-specific validators for boot/device variables. Enumeration allocates a 512-byte name buffer, locks EFI variable iteration, repeatedly calls `efivar_get_next_variable`, checks duplicate presence when requested, and invokes a caller callback. Set/get-size first validates data, locks firmware access, calls SetVariable, then calls GetVariable with size zero to determine the new size or deletion result.

## State and persistence
Persistent state is firmware variable storage changed by SetVariable/DeleteVariable. Runtime state is limited to temporary name buffers and the global EFIVAR lock. The validation whitelist affects whether efivarfs inodes default to immutable.

## Dependencies and integration points
It imports the `EFIVAR` namespace and depends on EFI runtime services, UCS-2 helpers, GUID utilities, hex parsing, and efivarfs superblock duplicate detection callback. File and inode operations call these helpers for all firmware access.

## Risks and test signals
Risks include firmware implementations that loop or return duplicate names, validation accepting malformed boot entries, incorrect wildcard matching, SetVariable/GetVariable races, NVRAM exhaustion, and destructive writes to sensitive variables if whitelist rules are wrong. Test signals include Boot/Driver variable validation, invalid device paths, oversized variable names, duplicate enumeration, delete of missing variables, ENOSPC handling, random seed exclusion, and concurrent readers/writers under efivar locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/vars.c -->

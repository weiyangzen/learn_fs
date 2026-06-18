# sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/efi_secret.c

## Purpose
Exposes firmware-injected confidential-computing secrets as read/delete files under `securityfs` at `secrets/coco`.

## APIs, Types, and Functions
Important structures are `struct efi_secret`, `struct secret_header`, and `struct secret_entry`. Main functions are `efi_secret_probe()`, `efi_secret_map_area()`, `efi_secret_securityfs_setup()`, `efi_secret_bin_file_show()`, `efi_secret_unlink()`, `wipe_memory()`, `efi_secret_securityfs_teardown()`, and `efi_secret_unmap_area()`.

## Control Flow and State
Probe maps the EFI CoCo secret descriptor from `efi.coco_secret`, validates base and size, maps the actual secret area encrypted, validates the table header GUID and reported length, creates `securityfs` directories, then creates up to 64 files named by secret GUID. Reading a file streams the secret bytes through seq_file. Unlinking a file zeros secret data, flushes cache on x86, marks the entry GUID `NULL_GUID`, clears `inode->i_private`, and delegates to `simple_unlink()`. Global state is `the_efi_secret`, containing the mapped region and root dentry.

## Dependencies and Integration
Depends on EFI CoCo secret table support, `ioremap_encrypted()`, securityfs, seq_file helpers, GUID helpers, and platform-driver binding named `efi_secret`.

## Risks and Test Signals
Security risks are stale secret exposure, incomplete wiping, malformed table walking, and teardown after partial securityfs creation. The parent `secrets` directory is removed via `securityfs_remove(s->secrets_dir)`, relying on recursive cleanup. Tests should cover invalid GUID, short/oversized table length, corrupt entry length, more than 64 entries, read-after-delete, and x86 cache flushing behavior.

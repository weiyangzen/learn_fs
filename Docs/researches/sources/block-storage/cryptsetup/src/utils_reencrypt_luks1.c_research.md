# File Research: sources/block-storage/cryptsetup/src/utils_reencrypt_luks1.c

This file implements legacy offline LUKS1 reencryption. Unlike the LUKS2 path, it performs reencryption by creating temporary headers, activating old/new temporary mappings, copying data between them, and tracking progress in an external log file.

Key responsibilities:
- Supports LUKS1 reencrypt, encrypt, decrypt, resume, and keep-key modes.
- Creates and manages temporary files named from the LUKS UUID:
  - `LUKS-<uuid>.org`
  - `LUKS-<uuid>.new`
  - `LUKS-<uuid>.log`
- Marks an original LUKS1 header unusable by replacing the normal magic with `LUKS dead` style `NOMAGIC`.
- Detects an in-progress legacy LUKS1 reencryption by checking for the unusable magic.
- Activates two private temporary dm-crypt mappings, one with the old header and one with the new header.
- Copies data forward or backward depending on whether the device size is reduced.
- Restores the final LUKS1 header after copying completes.

Main state:
- `struct reenc_ctx` stores device/header paths, UUID, mode, direction, offsets, temporary file names, dm paths, log file descriptor/buffer, passphrases per slot, selected keyslot, and resume byte count.
- Modes are `REENCRYPT`, `ENCRYPT`, and `DECRYPT`.
- Directions are `FORWARD` and `BACKWARD`.

Important control flow:
- `reencrypt_luks1()` allocates and initializes the context, gathers passphrases, prepares backup/fake headers, marks the original header unusable when needed, activates temporary mappings, copies data unless `--keep-key` is set, then restores or finalizes headers.
- `initialize_context()` prepares filenames, validates exclusive device open, initializes UUID, removes stale temporary mappings, opens/parses the log, and sets initial mode/direction.
- `open_log()` creates a new log or opens an existing one to resume.
- `write_log()` and `parse_log()` store/restore version, UUID, direction, mode, offset, and shift in a single sector.
- `backup_luks_headers()` saves the original LUKS1 header and creates the new LUKS1 header for reencryption.
- `backup_fake_header()` creates `cipher_null` fake headers for encrypt/decrypt transitions.
- `activate_luks_headers()` opens private temporary mappings for old and new views of the same data device.
- `copy_data_forward()` and `copy_data_backward()` perform the actual IO and update the log.
- `restore_luks_header()` restores the completed new header to the real header location or renames it for new detached-header encryption.
- `destroy_context()` closes mappings, removes clean temporary files, and clears passphrase memory.

Safety and recovery:
- The original LUKS1 header is intentionally made unusable during reencryption to prevent accidental normal activation of partially converted data.
- The `.log` file is the resume source; deleting or editing it breaks recovery.
- `stained` controls whether temporary files are retained after failure.
- IO errors during copy are reported and leave recovery artifacts.
- Signal interruption returns retryable/resumable errors and writes the current log.
- For decrypt, extra space in the now-plain device may be zeroed to remove leftover encrypted tail data.

Limitations and notable behavior:
- The implementation is offline-only and requires exclusive device access.
- It relies on passphrase material stored in memory per keyslot during the operation.
- It has a FIXME noting non-PBKDF2 PBKDFs should be blocked.
- The file-level comment and surrounding LUKS2 code indicate this is legacy behavior retained for LUKS1 compatibility.

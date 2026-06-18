<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-space.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-space.c

## Purpose
Implements TPM2 resource-manager spaces for `/dev/tpmrm*`, virtualizing transient object handles and sessions by loading contexts before each command and saving/flushing them afterward.

## Important APIs, Types, And Functions
Exports `tpm2_init_space()`, `tpm2_del_space()`, `tpm2_load_context()`, `tpm2_save_context()`, `tpm2_flush_space()`, `tpm2_prepare_space()`, `tpm2_commit_space()`, `tpm_devs_add()`, and `tpm_devs_remove()`. Internal helpers include `tpm2_load_space()`, `tpm2_map_command()`, `tpm_find_and_validate_cc()`, `tpm2_map_response_header()`, `tpm2_map_response_body()`, and `tpm2_save_space()`.

## Control Flow
Before a user command, `tpm2_prepare_space()` validates the command code against `chip->cc_attrs_tbl`, copies the file space into `chip->work_space`, loads saved transient and session contexts, maps virtual transient handles in the command to physical handles, and records `last_cc`. After transmit, `tpm2_commit_space()` maps returned physical handles to virtual handles, filters `GetCapability` handle lists to handles owned by the space, saves and flushes active contexts, copies updated state back to the file space, and adjusts the response length.

## State And Persistence
Each `struct tpm_space` owns context/session backing buffers plus tables of virtual-to-physical transient handles and session handles. Saved contexts persist across commands for a file descriptor, while physical TPM handles are flushed after saving.

## Dependencies And Integration Points
Used by common TPM char-device transmit for resource-manager files and by chip allocation for the internal work space. It depends on TPM2 context load/save/flush commands, command attribute tables from `tpm2_get_cc_attrs_tbl()`, cdev device registration, and TPM class state.

## Risks And Edge Cases
Handle-table slots are finite; when full, newly returned handles are flushed and `-ENOMEM` is reported. Context integrity, stale sessions, or external flushes can make loads return `-ENOENT` or `-EINVAL`. Command-length validation must match command attributes or user buffers could be remapped incorrectly.

## Test Signals
Create/load/flush transient objects through `/dev/tpmrm*`, session persistence across commands, concurrent spaces with isolated virtual handles, handle table exhaustion, `GetCapability` handle filtering, invalid command codes/lengths, context integrity errors, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm2-space.c -->

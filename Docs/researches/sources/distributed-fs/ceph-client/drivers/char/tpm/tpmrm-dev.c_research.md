# sources/distributed-fs/ceph-client/drivers/char/tpm/tpmrm-dev.c

## Purpose
Implements file operations for the TPM resource-manager character device, giving each open file its own TPM2 transient-object/session space.

## Important APIs, Types, And Functions
Defines `struct tpmrm_priv`, embedding generic `file_priv` and `struct tpm_space`. Implements `tpmrm_open()`, `tpmrm_release()`, and exported `tpmrm_fops`.

## Control Flow
Open obtains the containing `tpm_chip` from the inode cdev, allocates per-file private state, initializes a TPM2 space with `TPM2_SPACE_BUFFER_SIZE`, and calls `tpm_common_open()` with that space. Release retrieves the private container, calls `tpm_common_release()`, deletes the TPM2 space from the chip, frees memory, and returns success. Read/write/poll delegate directly to common TPM file helpers.

## State And Persistence
Each open resource-manager fd owns a `tpm_space` that virtualizes TPM2 handles for the lifetime of the file. No durable state is kept after release.

## Dependencies And Integration Points
Depends on `tpm-dev.h`, common TPM file operations, and TPM2 space management helpers `tpm2_init_space()` and `tpm2_del_space()`.

## Risks And Edge Cases
Allocation or space initialization failure aborts open. Release must delete the space after common release while the chip reference is still available. The file is meaningful only for TPM2-capable chips, enforced by higher TPM core registration logic.

## Test Signals
Multiple concurrent opens with isolated spaces, open failure injection, resource cleanup on release, read/write/poll behavior through common helpers, and TPM2 transient handle virtualization.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.c

## Purpose
Provides the exclusive raw TPM character-device file operations for `/dev/tpmN`.

## Important APIs, Types, And Functions
Defines `tpm_open()`, `tpm_release()`, and exported `tpm_fops`. It uses `struct file_priv`, `container_of(inode->i_cdev, struct tpm_chip, cdev)`, `test_and_set_bit()` on `chip->is_open`, and shared common file helpers.

## Control Flow
Open resolves the chip from the inode cdev and atomically enforces a single opener for the raw TPM device. It allocates per-file state and calls `tpm_common_open()` with no TPM2 resource-manager space. Release calls `tpm_common_release()`, clears `chip->is_open`, and frees the per-file state.

## State And Persistence
The raw-device open bit persists while one file descriptor owns the device. Per-open command/response state is stored in `struct file_priv` until release.

## Dependencies And Integration Points
Registered by `tpm-chip.c` through `cdev_init()`. It delegates read, write, poll, and release mechanics to `tpm-dev-common.c`.

## Risks And Edge Cases
Exclusive open is raw-device-specific; `/dev/tpmrm*` can support isolated spaces separately. Allocation failure must clear the open bit. Release assumes `file->private_data` was initialized by open.

## Test Signals
Open contention should return `-EBUSY`, allocation-failure injection should leave the device reopenable, and raw command traffic should bypass TPM2 space virtualization while still using common transmit logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.c

## Purpose
Coordinates firmware event-log discovery and exposes TPM measurement logs through securityfs seq_files.

## Important APIs, Types, And Functions
Key functions are `tpm_bios_measurements_open()`, `tpm_bios_measurements_release()`, `tpm_read_log()`, `tpm_bios_log_setup()`, and `tpm_bios_log_teardown()`. It uses `struct tpm_chip_seqops`, `struct tpm_chip`, `securityfs_create_dir()`, `securityfs_create_file()`, and TPM1/TPM2 seq operation tables.

## Control Flow
Open locks the inode, rejects removed dentries, grabs the chip device reference, opens the configured seq iterator, and stores the chip in `seq->private`. Setup skips virtual chips, tries ACPI then EFI then OF readers, creates a securityfs directory named after the TPM device, selects TPM2 binary or TPM1 binary/ascii seqops, and creates the exported measurement files. Any creation failure tears down the directory.

## State And Persistence
Securityfs dentries persist while the chip is registered. Per-open device references keep the chip alive during seq_file reads. `chip->bin_log_seqops`, `chip->ascii_log_seqops`, and `chip->bios_dir` hold the runtime export state.

## Dependencies And Integration Points
Called by `tpm_chip_register()` and `tpm_chip_unregister()`. It integrates firmware log readers from `common.h`, securityfs, seq_file, and TPM event parser files `tpm1.c` and `tpm2.c`.

## Risks And Edge Cases
The inode link check avoids opening removed files, but lifetime correctness still depends on paired `get_device()`/`put_device()`. Securityfs may be disabled and return `-ENODEV`; setup intentionally treats missing logs as nonfatal. TPM2 gets no ascii export here.

## Test Signals
Register/unregister chips while reading securityfs files, boot with securityfs disabled, exercise ACPI/EFI/OF fallback ordering, verify TPM1 exposes both binary and ascii files, and verify TPM2 exposes only binary output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/common.c -->

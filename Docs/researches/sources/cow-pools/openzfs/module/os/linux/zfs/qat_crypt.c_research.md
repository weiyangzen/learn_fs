# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/qat_crypt.c

## Purpose

Implements Intel QAT acceleration for ZFS encryption/decryption and checksumming. QAT cryptographic instances serve both operations, so they share initialization and instance selection.

## Main State

- `cy_inst_handles`: QAT crypto instance handles.
- `num_inst`: active crypto instance count.
- `inst_num`: round-robin instance counter.
- `qat_cy_init_done`: initialization flag.
- `zfs_qat_encrypt_disable`: encryption/decryption disable parameter.
- `zfs_qat_checksum_disable`: checksum disable parameter.

## Eligibility

- `qat_crypt_use_accel(s_len)`: encryption enabled, initialized, and size within QAT bounds.
- `qat_checksum_use_accel(s_len)`: checksum enabled, initialized, and size within QAT bounds.

## Initialization And Cleanup

- `qat_cy_init()`: discovers crypto instances, caps to `QAT_CRYPT_MAX_INSTANCES`, sets address translation, starts instances, and marks initialized.
- `qat_cy_clean()`: stops instances and resets state.
- `qat_cy_fini()`: cleans if initialized.
- `symcallback()`: records QAT verification result and completes the waiting thread.

## Session Setup

- `qat_init_crypt_session_ctx()`: creates AES-GCM session context for encrypt/decrypt. CCM is explicitly unsupported and returns failure without counting as a GCM failure.
- `qat_init_checksum_session_ctx()`: creates a SHA256 hash session context. ZFS SHA512/256 is not supported by QAT and is rejected.
- `qat_init_cy_buffer_lists()`: allocates QAT private metadata for source and destination buffer lists.

## Encryption/Decryption

- `qat_crypt()`: maps source and destination buffers page-by-page, allocates session and operation metadata, copies IV/AAD/digest as needed, submits `cpaCySymPerformOp`, waits for completion, validates callback result, copies produced digest on encryption, updates kstats, unmaps pages, removes session, and frees allocations.

## Checksumming

- `qat_checksum()`: maps input pages, creates checksum session, allocates digest buffer, submits QAT hash operation, waits for completion, copies digest into `zio_cksum_t`, updates kstats, and cleans resources.

## Parameter Hooks

- `param_set_qat_encrypt()`: enabling attempts crypto initialization.
- `param_set_qat_checksum()`: enabling attempts crypto initialization.
- Module parameters expose encryption and checksum disable flags.

## Notes

The file uses fixed arrays sized for up to 48 QAT crypto instances and `MAX_PAGE_NUM` stack arrays for mapped pages. Unsupported algorithms are returned as failures to the caller but not always counted as QAT operational failures.

# sources/distributed-fs/ceph-client/include/linux/tpm.h

## Purpose
Defines the kernel TPM core interface: TPM 1.2/2.0 constants, command and response metadata, chip state, low-level bus operation callbacks, TPM command-buffer helpers, PCR/random APIs, and optional TPM2 HMAC session support. It is a central integration header for TPM device drivers, trusted keys, RNG, ACPI PPI, event logs, and callers that transmit TPM2 commands.

## Important APIs, Types, And Functions
Key types are `struct tpm_chip`, `struct tpm_class_ops`, `struct tpm_buf`, `struct tpm_digest`, `struct tpm_bank_info`, `struct tpm_space`, and `struct tpm_header`. `struct tpm_class_ops` is the bus-driver vtable for `send`, `recv`, `status`, `cancel`, locality, clock, timeout, and idle/ready transitions. `struct tpm_chip` owns device/cdev state, ops lifetime locking, event log seqops, RNG registration, timeout/duration tables, PCR banks, ACPI PPI data, TPM space buffers, command attributes, active locality, and optional HMAC auth session state.

Public APIs include `tpm_try_get_ops()`, `tpm_put_ops()`, `tpm_transmit_cmd()`, `tpm_pcr_read()`, `tpm_pcr_extend()`, `tpm_get_random()`, `tpm_default_chip()`, `tpm2_flush_context()`, `tpm2_find_hash_alg()`, and TPM buffer helpers such as `tpm_buf_init()`, `tpm_buf_append_u32()`, `tpm_buf_read_u16()`, `tpm_buf_append_handle()`, `tpm_buf_append_auth()`, and HMAC response validation helpers.

## Control Flow
Callers construct a `tpm_buf` with a tag and ordinal, append handles/auth/payload, then pass it to `tpm_transmit_cmd()`. The core uses `tpm_chip.ops` under `ops_sem` and `tpm_mutex` to serialize and dispatch to the transport. Return codes are normalized by helpers such as `tpm2_rc_value()` and `tpm_ret_to_err()`. Auth-session builds are conditional: when TPM2 HMAC is configured, session start/fill/check/end functions participate in request/response flow; otherwise inline stubs preserve source compatibility.

## State, Persistence, And Dependencies
Persistent kernel state is per `tpm_chip`: cdev lifetime, locality, timeout tuning, PCR bank information, event log pointers, allocated command attributes, work-space context buffers, and optional TPM2 HMAC seed/context data. Dependencies include `hw_random`, `acpi`, `cdev`, `fs`, `highmem`, `crypto/hash_info`, and AES definitions. Compile-time dependency gates provide no-op or `-ENODEV` fallbacks when TPM support is not built.

## Integration Points
Integrates with `/dev/tpm*`, sysfs groups, ACPI PPI, BIOS/EFI event logs, hwrng, TPM2 trusted-key/auth paths, and bus drivers implementing `tpm_class_ops`. `tpm_is_firmware_upgrade()` and chip flags expose state to drivers that must restrict normal command paths during firmware update mode.

## Risks And Test Signals
Risks include command-buffer overflow/boundary flags being ignored, mismatched TPM2 handle/name/auth encoding, stale ops after driver unregister, locality leaks, timeout calibration errors, and conditional stubs hiding missing TPM support. Test signals are TPM command self-tests, PCR read/extend coverage across hash banks, random read behavior, firmware-upgrade mode checks, HMAC-session positive/negative tests, suspend/resume locality handling, and compile coverage with TPM, ACPI, and HMAC configs both enabled and disabled.

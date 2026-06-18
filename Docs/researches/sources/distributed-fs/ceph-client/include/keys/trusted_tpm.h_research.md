# sources/distributed-fs/ceph-client/include/keys/trusted_tpm.h

Source read summary: 18 lines, 475 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_tpm.h` declares TPM2 trusted-key seal and unseal helpers used by the TPM backend.

Important APIs, types, and functions: Important exported functions or hooks: `tpm2_seal_trusted`, `tpm2_unseal_trusted`. Important types: none. Important constants/macros: none.

Control flow: The trusted-key implementation passes parsed payload/options into `tpm2_seal_trusted()` or `tpm2_unseal_trusted()` to create or recover sealed key blobs.

State and persistence behavior: TPM-sealed blobs persist in the key payload and are bound to TPM policy/PCR state; decrypted payload bytes are transient secret material.

Dependencies and integration points: It includes `keys/trusted-type.h`, `linux/tpm_command.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: TPM command errors, PCR mismatch, authorization failures, and blob size mismatches must unwind without leaking key bytes.

Test signals: Run TPM2 trusted-key seal/unseal tests, PCR policy changes, wrong authorization, and blob corruption cases.

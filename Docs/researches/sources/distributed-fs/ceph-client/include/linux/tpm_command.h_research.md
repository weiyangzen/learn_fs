# sources/distributed-fs/ceph-client/include/linux/tpm_command.h

## Purpose
Provides small TPM 1.2 command constants used by legacy trusted-key and command-building paths: request/response tags, selected ordinals, the storage-root-key handle, and nonce size.

## Important APIs, Types, And Functions
There are no functions or structs. Exports are preprocessor constants: `TPM_TAG_RQU_COMMAND`, `TPM_TAG_RQU_AUTH1_COMMAND`, `TPM_TAG_RQU_AUTH2_COMMAND`, response tag equivalents, ordinals such as `TPM_ORD_GETRANDOM`, `TPM_ORD_OSAP`, `TPM_ORD_OIAP`, `TPM_ORD_SEAL`, `TPM_ORD_UNSEAL`, `SRKHANDLE`, and `TPM_NONCE_SIZE`.

## Control Flow
The header has no runtime control flow. Consumers use these constants while serializing TPM 1.2 command packets and interpreting command classes.

## State, Persistence, And Dependencies
No state is held. It has no include dependencies beyond its guard and is strictly compile-time metadata.

## Integration Points
Integrates with TPM 1.2 command construction, especially sealed/unsealed data flows and OSAP/OIAP authorization sessions. It complements the broader `tpm.h` TPM2 definitions.

## Risks And Test Signals
Risks are wrong wire values causing TPM command rejection or authentication mismatch. Test signals are legacy TPM command vectors, build coverage for trusted-key paths that still include this header, and checking serialized packets against TCG constants.

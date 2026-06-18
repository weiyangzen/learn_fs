# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_loader.c

Purpose: loads a concatenated list of in-kernel DER X.509 certificates into a supplied keyring as asymmetric keys.

Important APIs/types/functions: `x509_load_certificate_list()` walks a byte array, validates that each certificate begins with a DER SEQUENCE using two-byte length form, computes each certificate length, and calls `key_create_or_update()` with type `"asymmetric"` and built-in/bypass flags.

Control flow: the function advances from certificate to certificate until the end of the list. Successful imports log the created key description; failures log the error and continue to the next parsed certificate. Dodgy list structure logs an error and returns 0.

State and persistence: imported keys persist in the target keyring. The input certificate list is borrowed and not retained directly. Created keys are marked built-in and not charged to quota.

Dependencies and integration points: depends on keyrings, asymmetric key type parsing, and callers that provide built-in certificate blobs for system, platform, or selftest keyrings.

Risks: structural parsing is intentionally simple and expects long-form DER lengths; unusual but valid DER encodings may be rejected. Parse errors return 0 after logging, so callers must rely on logs or resulting keyring contents rather than a hard error for malformed trailing data.

Test signals: concatenated multiple DER certs, short or malformed blobs, parser failure for one cert while continuing, built-in key flags, and selftest keyring loading.

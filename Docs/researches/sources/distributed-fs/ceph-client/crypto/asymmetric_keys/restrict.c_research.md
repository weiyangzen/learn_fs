# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/restrict.c

Purpose: implements asymmetric keyring restriction callbacks that decide whether a new asymmetric key may be linked into a destination keyring based on signatures, CA attributes, digital signature usage, builtin trust, and specified trusted keys/keyrings.

Important APIs/types/functions: boot parameter parsing for `ca_keys=` can restrict acceptable signer IDs or builtin keys. `restrict_link_by_signature()` verifies a new key against a trust keyring. `restrict_link_by_ca()` accepts only CA certificates with keyCertSign. `restrict_link_by_digsig()` accepts non-CA digital-signature certificates and then verifies trust. `key_or_keyring_common()` backs `restrict_link_by_key_or_keyring()` and `restrict_link_by_key_or_keyring_chain()`. Builtin/secondary/system restriction wrappers are referenced by `asymmetric_type.c`.

Control flow: restriction callbacks receive the candidate key payload and destination keyring. They validate key type, inspect public key extension flags and auth signature IDs, find a signer key in trusted material, optionally enforce builtin-key-only policy, and call `verify_signature()`. Chain mode can accept a candidate if signed by a trusted key or a key already in the destination keyring.

State and persistence: `use_builtin_keys` and `ca_keyid` are boot-time static policy state for built-in kernels. Restriction allocations can hold referenced trusted keys. Candidate key payload data is read but not owned.

Dependencies and integration points: depends on asymmetric key IDs, public-key extension flags, system keyrings, keyring restriction hooks, boot parameter parsing, and signature verification.

Risks: trust decisions hinge on exact/partial ID matching and key usage bits. Builtin/secondary trusted keyring policy is configuration-sensitive. Chain mode allowing `serial 0` must be limited to the intended restriction syntax. Missing auth IDs must reject rather than accidentally trust.

Test signals: adding CA and non-CA certificates to restricted keyrings, builtin-only restrictions, `ca_keys=id:` and `ca_keys=builtin`, chain restrictions with destination signer, rejected key usage combinations, and signature failure propagation.

# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2.py

## Purpose
This Python module is a lightweight TPM2 protocol client used by the TPM2 selftests. It constructs binary TPM2 commands, parses responses, maps TPM return codes to names, and exposes higher-level helpers for PCR, policy, seal/unseal, capabilities, resource-manager spaces, and nonblocking operation.

## Important APIs, Types, and Functions
Constants define TPM2 command codes, algorithms, handles, return codes, capabilities, and feature values. `ProtocolError` decodes TPM RC families. `AuthCommand`, `SensitiveCreate`, and `Public` serialize TPM structures. Utility functions include `get_digest_size()`, `get_hash_function()`, `get_algorithm()`, and `hex_dump()`. `Client` owns the device file and implements `send_cmd()`, `read_pcr()`, `extend_pcr()`, `start_auth_session()`, `policy_pcr()`, `policy_password()`, `get_policy_digest()`, `flush_context()`, `create_root_key()`, `seal()`, `unseal()`, `reset_da_lock()`, `get_cap()`, and `get_cap_pcrs()`.

## Control Flow
`Client.__init__()` opens `/dev/tpm0` or `/dev/tpmrm0` based on `FLAG_SPACE` and optionally enables `O_NONBLOCK`. `send_cmd()` writes a fully packed command, polls if nonblocking, reads the response, optionally hex-dumps it, and raises `ProtocolError` on nonzero response code. Higher-level methods pack command-specific request bodies, call `send_cmd()`, and slice response payloads. `unseal()` first loads a sealed blob under a parent key, then unseals it with either password or policy session auth, and always flushes the loaded data handle.

## State and Persistence
The client holds an open TPM character device and, under resource-manager mode, a kernel TPM space. TPM transient objects and sessions are kernel state and must be flushed by callers. PCR extension mutates TPM PCR state. The module itself keeps no global mutable state except constants.

## Dependencies and Integration Points
It depends on Python `struct`, `hashlib`, `fcntl`, `select`, Linux TPM character devices, and TPM2 command wire formats. It is imported by `tpm2_tests.py` and run by shell wrappers.

## Risks
The module hand-packs TPM binary protocol and response offsets; mistakes in structure length or response slicing can produce brittle failures. `UnknownAlgorithmIdError.__str__()` and related methods reference local names rather than `self.*`, which could itself fail if stringified. PCR byte concatenation in `__calc_pcr_digest()` relies on Python bytearray behavior over collected PCR bytes. Operations can change PCR state and depend on TPM owner hierarchy being usable.

## Test Signals
Protocol-level success is a zero TPM RC in `send_cmd()`. Higher-level tests use expected data equality, known RC values such as `TPM2_RC_AUTH_FAIL`, `TPM2_RC_POLICY_FAIL`, `TPM2_RC_SIZE`, and resource-manager layered `TPM2_RC_COMMAND_CODE`.

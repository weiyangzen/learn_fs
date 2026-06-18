<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-stubs.c -->
# sources/distributed-fs/orangefs/src/common/security/security-stubs.c

## Purpose
Provides the non-secure implementation used when OrangeFS is built without real security. It preserves API shape and timeout behavior without cryptographic signing or verification.

## Important APIs, Types, And Functions
Implements the same lifecycle, capability, credential, and error-facing functions declared by `pint-security.h`: `PINT_security_initialize`, `PINT_security_finalize`, `PINT_init_capability`, `PINT_sign_capability`, `PINT_server_to_server_capability`, `PINT_verify_capability`, `PINT_init_credential`, `PINT_sign_credential`, and `PINT_verify_credential`.

## Control Flow
Initialize/finalize return success. Capability signing sets timeout and null signature fields. Capability verification accepts null capabilities and otherwise only checks timeout unless bypassed. Server-to-server capability builds an all-ops `S:` issuer and calls stub signing. Credential signing sets issuer, timeout, null signature, and verification checks timeout only.

## State And Persistence
No global state or persistent key material is used. The functions mutate caller-provided capability and credential structures.

## Dependencies And Integration Points
Depends on server configuration, PVFS types, `pint-util`, `security-util`, and `pint-security.h`. It is selected by `security/module.mk.in` when neither key nor certificate security is enabled.

## Risks And Test Signals
This intentionally provides no cryptographic trust. `PINT_sign_credential` assumes `cred->issuer` already points to writable storage, unlike the real implementation that allocates it. Tests should cover timeout accept/reject behavior, issuer buffer sizing, null capability acceptance, server-to-server capability construction, and build selection in no-security configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-stubs.c -->

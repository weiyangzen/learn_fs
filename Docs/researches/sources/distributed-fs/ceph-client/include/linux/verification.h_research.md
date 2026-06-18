# sources/distributed-fs/ceph-client/include/linux/verification.h

## Purpose
This header defines kernel data/signature verification interfaces for PKCS#7 and PE signatures and enumerates key usage contexts.

## Important APIs, types, and functions
Important items are sentinel keyring selectors `VERIFY_USE_SECONDARY_KEYRING` and `VERIFY_USE_PLATFORM_KEYRING`, `system_keyring_id_check()`, `enum key_being_used_for`, `verify_pkcs7_signature()`, `verify_pkcs7_message_sig()`, and optional `verify_pefile_signature()`.

## Control flow, state, and persistence
Callers pass data, signature or parsed PKCS#7 message, selected trusted keyring, usage context, and optional content-view callback. Verification code checks signatures against builtin/secondary/platform trust roots. This header stores no state; trust keyrings and parsed messages are external runtime objects.

## Dependencies and integration points
It depends on errno/types and, when enabled, key and PKCS#7 subsystems. It integrates module loading, firmware loading, kexec PE verification, key signing, and BPF signature verification.

## Risks and test signals
Risks include invalid sentinel keyring IDs, wrong usage context policy, accepting malformed PKCS#7 data, and disabled verification config. Tests should cover trusted/untrusted signatures, secondary/platform keyring selectors, PE verification, callback data views, and malformed signatures.

# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_type.c

Purpose: implements the `"asymmetric"` key type, parser registry, key-id matching, key descriptions, key cleanup, keyring restriction lookup, and pkey operation dispatch.

Important APIs/types/functions: `find_asymmetric_key()` searches keyrings by issuer/serial, subject key ID, or subject name ID. `asymmetric_key_generate_id()`, `asymmetric_key_id_same()`, `asymmetric_key_id_partial()`, and `asymmetric_key_hex_to_key_id()` build and compare identifiers. Match-preparse helpers support `id:`, `ex:`, and `dn:` search prefixes. `asymmetric_key_preparse()` iterates registered parsers. `register_asymmetric_key_parser()` and `unregister_asymmetric_key_parser()` manage the parser list. `key_type_asymmetric` wires all operations into the keyring core.

Control flow: key instantiation calls `asymmetric_key_preparse()`, which scans parser modules under `asymmetric_key_parsers_sem` until one returns something other than `-EBADMSG`. Searches can use direct description matching or iterative key-id matching. Restriction strings such as `builtin_trusted`, `builtin_and_secondary_trusted`, and `key_or_keyring:<serial>[:chain]` are parsed into `struct key_restriction` callbacks. Pkey encryption/decryption/sign/verify operations dispatch through the key subtype stored in the payload.

State and persistence: global parser list state is protected by an rwsem. Each key persists subtype, key IDs, crypto payload, and auth signature data in `key->payload` until destroyed. Restriction objects can hold referenced trust keys.

Dependencies and integration points: depends on Linux keyrings, public-key subtype interfaces, system keyring restriction functions, user-type helpers, module references, and parser modules such as X.509 and PKCS#8.

Risks: key-id search prefixes are security-sensitive because partial versus exact matching changes trust decisions. Parser lifetime depends on module owner references and correct free-preparse behavior. Restriction parsing must not leak referenced keys on allocation failure. Payload slot indexes must match public asymmetric key conventions.

Test signals: key add/search by description, `id:` partial, `ex:` exact, and `dn:` exact searches; parser registration conflicts; restriction string variants; unsupported subtype pkey operations; key destroy/free-preparse leak checks; and concurrent parser registration with key instantiation.

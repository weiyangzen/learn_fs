# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/signature.c

Purpose: provides shared signature object cleanup and exported asymmetric key query/verify dispatch wrappers.

Important APIs/types/functions: `public_key_signature_free()` frees all auth key IDs, signature bytes, optionally owned digest/message bytes, and the signature object. `query_asymmetric_key()` validates key type and subtype and calls subtype `query`. `verify_signature()` validates key type and subtype and calls subtype `verify_signature`.

Control flow: parsers allocate `struct public_key_signature` objects and verifier/trust code eventually frees them through this file. Keyctl query and verifier callers enter the generic asymmetric key surface, then dispatch to the concrete subtype such as `public_key_subtype`.

State and persistence: no global state. It frees per-signature heap state and reads key payload subtype pointers.

Dependencies and integration points: depends on asymmetric subtype definitions, keyctl pkey query structures, public key structures, and user-type headers. Used by X.509, PKCS#7, trust restriction, and public-key operations.

Risks: `sig->m_free` controls ownership of `sig->m`; incorrect parser setup can leak or free borrowed data. Dispatch rejects missing subtype/payload but assumes payload slot conventions are stable.

Test signals: signature objects with and without owned message buffers, multiple auth IDs, unsupported subtype operations, non-asymmetric key rejection, and normal public-key verification calls.

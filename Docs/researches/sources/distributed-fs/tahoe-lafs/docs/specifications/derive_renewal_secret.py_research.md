## sources/distributed-fs/tahoe-lafs/docs/specifications/derive_renewal_secret.py

Purpose: reference implementation and self-test for Tahoe-LAFS lease renewal secret derivation as of 1.16.0.

Important APIs: `derive_renewal_secret`, `demo`, and `test`.

Control flow: `derive_renewal_secret` asserts exact byte lengths for lease secret, storage index, and tubid, derives client renewal secret with tagged hash, derives file renewal secret with tagged pair hash over storage index, then derives bucket renewal secret with peer id/tubid. `test` decodes base32 vectors, re-derives secrets, asserts expected base32 output, and prints success. `demo` prints one example. Both run at import/execution time.

State and dependencies: stateless cryptographic derivation using `allmydata.util.base32` and `hashutil`. No persistence.

Risks: top-level `test()` and `demo()` make import side-effectful. Assertions can be disabled with optimized Python, so this is a reference script, not hardened validation code. Test vectors provide strong regression signal for protocol compatibility.

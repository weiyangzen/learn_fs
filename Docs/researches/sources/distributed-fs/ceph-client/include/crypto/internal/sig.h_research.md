# sources/distributed-fs/ceph-client/include/crypto/internal/sig.h

Purpose: defines private public-key signature algorithm registration and template wrapping support.

Important APIs, types, and flow: `struct sig_instance` overlays a crypto instance with `sig_alg`, and `struct crypto_sig_spawn` references an inner signature algorithm. Helpers expose transform context, register/unregister algorithms, register template instances, cast instance/context objects, grab/drop spawns, instantiate spawned transforms, and recover the spawned `sig_alg`.

State and persistence: signature key material and implementation state are held in `crypto_sig` transform contexts. Request data is passed directly to sign/verify APIs; no persistence is declared.

Dependencies and integration: depends on public `crypto/sig.h` and crypto template infrastructure. It supports algorithms such as RSA/ML-DSA signature providers and padding/encoding templates.

Risks and test signals: risks include key-size/digest-size reporting mismatch, stale spawn references, and template instance cleanup. Signals include sign/verify self-tests, invalid key tests, module unload/reload, and template-generated algorithm registration tests.

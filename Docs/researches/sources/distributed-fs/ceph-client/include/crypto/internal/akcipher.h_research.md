# sources/distributed-fs/ceph-client/include/crypto/internal/akcipher.h

Purpose: defines the internal asymmetric cipher interface for public-key encryption algorithms and template instances.

Important APIs, types, and flow: `struct akcipher_instance` embeds template lifecycle and an `akcipher_alg`; `struct crypto_akcipher_spawn` references an inner public-key cipher. Helpers expose request/transform contexts, DMA-aligned private data, request-size setters, request completion, algorithm names, instance casting, instance context lookup, spawn grab/drop/instantiate, and algorithm registration through `crypto_register_akcipher()` and `akcipher_register_instance()`.

State and persistence: key material and per-transform state live in `crypto_akcipher` contexts owned by implementations; request contexts are transient. The header itself declares no storage or persistence.

Dependencies and integration: depends on public `crypto/akcipher.h` and crypto algorithm/template infrastructure. It is used by RSA and padding templates and hardware/software asymmetric crypto providers.

Risks and test signals: risks include request context under-allocation, DMA alignment mistakes, stale spawn references during template teardown, and wrong algorithm name/reporting for nested templates. Test signals include RSA encrypt/decrypt/signature padding template self-tests, module unload/load, key-size boundary tests, and hardware driver DMA tests.

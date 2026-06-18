# sources/distributed-fs/ceph-client/include/crypto/internal/kpp.h

Purpose: defines private key-agreement protocol primitive registration, template instance, spawn, context, and request helpers.

Important APIs, types, and flow: `struct kpp_instance` overlays `crypto_instance` with a `kpp_alg`, and `struct crypto_kpp_spawn` binds template instances to inner KPP algorithms. Helpers expose request and transform contexts, DMA-aligned request/transform data, request-size setters, request completion, algorithm names, instance casting, instance context lookup, algorithm registration, template instance registration, spawn grab/drop, and transform instantiation.

State and persistence: secrets and per-transform key material live in KPP implementation contexts; request input/output SGs are transient. The header declares no persistent state.

Dependencies and integration: depends on public `crypto/kpp.h` and crypto algorithm/template infrastructure. It is used by ECDH/DH implementations and templates that wrap KPP algorithms.

Risks and test signals: risks include key material lifetime, request-size/DMA alignment mistakes, missing completion on asynchronous failures, and stale spawned algorithm references. Signals include ECDH/DH self-tests, invalid secret handling, max-size output checks, template load/unload, and DMA hardware-driver runs.

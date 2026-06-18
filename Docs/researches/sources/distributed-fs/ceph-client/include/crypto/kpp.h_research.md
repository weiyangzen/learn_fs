# sources/distributed-fs/ceph-client/include/crypto/kpp.h

Purpose: exposes the public crypto API for key-agreement protocol primitives such as ECDH and DH.

Important APIs, types, and flow: `struct kpp_alg` provides `set_secret`, `generate_public_key`, `compute_shared_secret`, `max_size`, and optional init/exit callbacks. `struct crypto_kpp` holds the transform, request size, and algorithm exit callback. `struct kpp_request` carries source/destination SGs, source length, destination length pointer, base async request, and request-private context. Helpers allocate/free transforms and requests, set callbacks, set input/output buffers, set secrets through `struct kpp_secret`, generate public keys, compute shared secrets, and query max output size.

State and persistence: secrets live in transform context after `crypto_kpp_set_secret()`; requests are transient. No external persistence is present.

Dependencies and integration: uses generic crypto transform allocation, async request completion, scatterlists, and KPP implementations. It is consumed by kernel protocols and asymmetric-key code needing key agreement.

Risks and test signals: risks include caller-provided `dst_len` underruns, secret encoding mismatches, asynchronous completion handling, and insufficient key validation. Signals include KPP known-answer tests, invalid/short secret tests, max-size probes, SG boundary tests, and async request cancellation or completion tests.

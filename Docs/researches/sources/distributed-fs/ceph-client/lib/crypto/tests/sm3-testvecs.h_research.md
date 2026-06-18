# sources/distributed-fs/ceph-client/lib/crypto/tests/sm3-testvecs.h

Purpose: generated SM3 digest test-vector data for the shared KUnit hash template.

Important APIs/types/functions: defines `hash_testvecs[]` with `SM3_DIGEST_SIZE` digests and `hash_testvec_consolidated`. There is no HMAC data in this header because the SM3 driver only maps the plain hash macro set.

Control flow: none locally. The template uses the table to test deterministic generated inputs over the same boundary-oriented lengths used by other hash vector headers, including empty input, block boundaries around 64/128 bytes, and larger multi-block inputs.

State and persistence: constant data only; no mutation, allocation, or persistence.

Dependencies: `SM3_DIGEST_SIZE`, `u8`, `size_t`, and generated-vector conventions. The header was produced by `scripts/crypto/gen-hash-testvecs.py sm3`.

Integration points: included by `sm3_kunit.c` to validate `<crypto/sm3.h>` implementations.

Risks: because the data is generated and compact, input content is implicit; diagnosis requires tracing the shared generator/template. If future SM3 implementation changes alter endian handling or padding, this table should catch it but not explain it.

Test signals: covers SM3 digest correctness across padding and block-boundary cases; no HMAC signal.

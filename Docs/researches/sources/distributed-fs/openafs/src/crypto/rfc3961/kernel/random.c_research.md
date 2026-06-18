# sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/random.c

This kernel adapter implements `krb5_generate_random_block` by calling `osi_readRandom(buf, len)`. It ignores any return value, matching a void Kerberos random-block API.

State is only the caller-provided output buffer. Dependencies are OpenAFS kernel includes and `rfc3961.h`. Integration is upstream RFC3961 key generation and confounder generation in kernel mode.

Risks are lack of error reporting from `osi_readRandom`; if the kernel RNG fails or returns short data, callers cannot know from this wrapper. Test signals are kernel random-block tests using instrumentation around `osi_readRandom` and crypto known-answer tests that do not require deterministic randomness.

# sources/distributed-fs/ceph-client/security/ipe/digest.h

Purpose: Declares IPE digest representation and helper APIs.

Important APIs/types/functions: `struct digest_info` stores algorithm name, digest bytes, and length. Declares parser, free, audit, and equality helpers.

Control flow: Header-only interface; functions are implemented in `digest.c`.

State and persistence: Digest info instances are dynamically allocated by policy parsing or LSM blob update paths and must be freed with `ipe_digest_free()`.

Dependencies and integration: Includes audit and policy headers; consumed by IPE policy parser, evaluation, hooks, and audit.

Risks and test signals: Risks are const pointer ownership ambiguity and callers freeing non-owned digest values. Static analysis and KUnit parser tests are useful signals.

# sources/distributed-fs/openafs/src/rxkad/v5der.c

Purpose: Bundled Heimdal DER helper implementation used by rxkad Kerberos v5 ASN.1 generated code.

Important APIs/functions: Provides `_der_timegm`, `_der_gmtime`, DER getters for integers, lengths, booleans, strings, octet strings including BER constructed form, OIDs, tags, times, and bit strings; DER putters for the same families; free functions; DER length calculators; and deep copy helpers.

Control flow and state: Decode helpers validate lengths, allocate output buffers, return ASN.1 error codes, and free partial state on some failures. Encoding writes backward from the end of caller-provided buffers, matching Heimdal generated encoder expectations. Time helpers bound far-future calculations to avoid denial-of-service loops.

Dependencies and integration: Included directly by `ticket5.c` after `v5gen-rewrite.h`, so symbols are renamed to `_rxkad_v5_*`. It depends on ASN.1 error codes, Heimdal types from `der.h`/`v5gen.h`, and libc allocation/time functions.

Risks: Memory ownership is caller-sensitive. Some helpers accept BER indefinite/constructed forms even in a DER support file for compatibility. Because it is included into `ticket5.c`, local warnings and symbol rewriting matter for build hygiene.

Test signals: Any Kerberos v5 ticket decode/encode path exercises this file extensively through generated ASN.1 functions.

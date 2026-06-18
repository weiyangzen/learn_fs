# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.h

Purpose: defines PE verification shared context and the Microsoft code-signing parser entry declaration.

Important APIs/types/functions: `struct pefile_context` stores parsed PE metadata such as header size, checksum offset, certificate directory offset, data directory and section counts, signature offset/length, section table pointer, and signed digest details. `kenter` and `kleave` provide local debug tracing. `mscode_parse()` is declared for use by PE verification.

Control flow: `verify_pefile.c` fills the context during PE parsing, `mscode_parser.c` fills digest fields during PKCS#7 content parsing, and PE digest comparison consumes the combined state.

State and persistence: context state is per-verification and stack-owned by the top-level verifier. The digest pointer is heap-owned until freed by the verifier.

Dependencies and integration points: includes public PKCS#7 API and hash info. Shared only by PE verification and Microsoft code-signing parser.

Risks: ownership of `digest` and borrowed section pointers must remain clear. Field width is `unsigned`, so bounds checks in the C file must guard arithmetic and offsets.

Test signals: compile coverage of PE verification, digest allocation/free paths, and debug builds that exercise kenter/kleave macros.

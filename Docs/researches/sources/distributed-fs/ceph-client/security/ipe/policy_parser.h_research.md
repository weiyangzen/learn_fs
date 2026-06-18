# sources/distributed-fs/ceph-client/security/ipe/policy_parser.h

Purpose: Declares IPE plaintext policy parser and parsed-policy cleanup APIs.

Important APIs/types/functions: Prototypes `ipe_parse_policy()` and `ipe_free_parsed_policy()`.

Control flow: No runtime logic.

State and persistence: Parsed policy ownership is transferred into `struct ipe_policy` on success and freed through the declared cleanup function.

Dependencies and integration: Used by `policy.c` and parser tests.

Risks and test signals: Build drift and missing cleanup on parser failure are primary risks. KUnit parser tests cover most interface use.

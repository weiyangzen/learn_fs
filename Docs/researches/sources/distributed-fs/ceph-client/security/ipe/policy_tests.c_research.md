# sources/distributed-fs/ceph-client/security/ipe/policy_tests.c

Purpose: Provides KUnit tests for unsigned IPE policy parser behavior.

Important APIs/types/functions: Defines `struct policy_case`, `policy_cases[]`, KUnit parameter generator `KUNIT_ARRAY_PARAM(ipe_policies, ...)`, tests `ipe_parser_unsigned_test()` and `ipe_parser_widestring_test()`, and suite `ipe-parser`.

Control flow: Parameterized tests call `ipe_new_policy(policy, strlen(policy), NULL, 0)` and compare expected errno or validate parsed/text/pkcs7 fields for success. The wide-string test passes UTF-16-like data and expects parser failure.

State and persistence: Allocates temporary policies through production policy creation and frees successful policies.

Dependencies and integration: Exercises parser, digest parsing, policy allocation/freeing, and KUnit. It does not require signed policy verification.

Risks and test signals: Strong coverage exists for comments, whitespace, CRLF, versions, malformed headers, duplicate defaults, invalid operations/actions, old-style digests, embedded NUL behavior, and wide strings. Gaps include signed PKCS#7 policy load, active policy update semantics, evaluator outcomes, and config-gated provider evaluation.

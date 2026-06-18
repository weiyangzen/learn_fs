# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/hashchk_test.c

## Purpose
Tests DEXCR NPHIE and hashchk/hashst behavior, including signal delivery and key sharing/randomization across exec, fork, and clone.

## Important APIs, Types, and Functions
Important functions are `require_nphie()`, `hashchk_handler()`, `hashchk_detected_test()`, `fill_hash_values()`, `count_hash_values_matches()`, `hashchk_exec_child()`, `hashchk_exec_random_key_test()`, `hashchk_fork_share_key_test()`, `hashchk_clone_share_key_test()`, and `main()`.

## Control Flow
The suite enables NPHIE, verifies a bad hashchk raises SIGILL/ILL_ILLOPN, execs a child to compare hash keys, forks to ensure key sharing, and uses clone with shared VM to verify thread-like sharing.

## State and Persistence
State includes process DEXCR NPHIE controls, global hash buffer contents, signal jump state, pipes for child output, and temporary clone stack mappings.

## Dependencies and Integration Points
Depends on DEXCR helpers, raw hash instructions, prctl, signal handling, fork/exec/clone, mmap, and `test_harness()`.

## Risks and Test Signals
Risks are hardware support and security-sensitive key semantics. Strong signals are wrong SIGILL code, identical hashes after exec, differing hashes after fork/clone, or inability to enable NPHIE.

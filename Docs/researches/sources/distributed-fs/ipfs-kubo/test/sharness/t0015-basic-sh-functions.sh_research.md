## sources/distributed-fs/ipfs-kubo/test/sharness/t0015-basic-sh-functions.sh

Purpose: unit-style shell tests for shared helper functions, especially robust quoting.

Important control flow: sources `lib/test-lib.sh`, invokes `shellquote` with simple strings, complex printf inputs, quotes, whitespace, and varied bytes, then compares output to expected quoted forms. No daemon or repo behavior is under test.

State and dependencies: uses expected/actual files in the sharness trash directory. Depends on `printf`, sed quoting behavior, and `test_cmp`.

Risks: because `shellquote` is used by diagnostic failure helper `test_fsh`, quoting regressions can hide or distort many later test failures. Test signal is exact quoted output for edge-case arguments.

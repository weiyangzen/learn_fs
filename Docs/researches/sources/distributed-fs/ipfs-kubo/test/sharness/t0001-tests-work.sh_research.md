## sources/distributed-fs/ipfs-kubo/test/sharness/t0001-tests-work.sh

Purpose: meta-test that validates sharness scripts are structurally well-formed.

Important control flow: after sourcing `lib/test-lib.sh`, it iterates over top-level `t*.sh` files and asserts each has `test_done` and `test_description`. For most scripts it also uses awk to ensure daemon launch/kill helper calls are balanced. It exempts daemon/shutdown tests that intentionally manage process lifecycle manually.

State and dependencies: reads sibling test files only; no Kubo state is created except normal test framework setup. Dependencies include grep, awk, find, basename, and sharness assertions.

Risks: static checks can reject legitimate new patterns unless exemptions are updated. Test signal is early detection of missing descriptions, missing `test_done`, or unbalanced daemon helpers.

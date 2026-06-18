## sources/distributed-fs/ipfs-kubo/test/sharness/t0018-indent.sh

Purpose: style/meta-test ensuring sharness test scripts do not use tab indentation.

Important control flow: iterates over `../t*.sh` and asserts each file has no tab-indented lines according to the grep pattern used in the test. It relies on sharness `test_expect_success` for each file.

State and dependencies: read-only over test scripts; no Kubo repo or daemon state. Depends on find/grep and shell iteration.

Risks: purely stylistic and can fail after harmless formatting changes. Test signal is uniform indentation across sharness scripts, reducing noisy diffs and shell readability problems.

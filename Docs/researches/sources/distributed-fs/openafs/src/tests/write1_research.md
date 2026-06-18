# sources/distributed-fs/openafs/src/tests/write1

Purpose: minimal shell smoke test for create, write, read-back, and remove in the current test directory.

Important behavior: it writes `hej` to `foo` with shell redirection, compares command-substituted `cat foo` output against `hej`, and removes `foo`. Each step exits one on failure.

State/dependencies: state is a temporary relative file `foo`, normally removed. It depends on `/bin/sh`, `echo`, `cat`, `test`, and `rm`, plus normal AFS client read-after-write behavior.

Risks/test signals: command substitution strips trailing newlines, so the comparison checks logical text rather than byte-for-byte file content. The test is intentionally small and only signals gross write/read/remove failures.

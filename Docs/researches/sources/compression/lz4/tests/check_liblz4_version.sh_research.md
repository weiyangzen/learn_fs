# sources/compression/lz4/tests/check_liblz4_version.sh

Purpose: verifies that a supplied binary dynamically links to `liblz4`.

Important commands: under `set -e`, runs `ldd $1 | grep liblz4`.

Control flow/state: one positional argument; no persistent output beyond stdout/stderr.

Dependencies/integration: POSIX shell, `ldd`, and `grep`; used by shared-library/install tests.

Risks: Linux/ldd-specific; unquoted `$1` breaks paths with spaces; static linking intentionally fails.

Test signals: success is a matching `liblz4` dependency line; otherwise exits non-zero.

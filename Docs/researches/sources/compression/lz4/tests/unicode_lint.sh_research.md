# sources/compression/lz4/tests/unicode_lint.sh

## Purpose
This Bash lint script enforces ASCII-only C and header sources under `lib/`, `programs/`, and `tests/`, addressing the policy described in LZ4 issue 1018.

## Important Control Flow
It initializes `pass=true`, then for each directory runs `find` for `*.c` and `*.h` files and `grep -P -n "[^\x00-\x7F]"`. Any result is printed with a `FAIL` marker and flips `pass=false`. The script exits 0 with a PASS message or 1 with FAIL.

## State, Dependencies, and Integration
There is no persistent state. Dependencies are Bash, `find`, and a `grep` implementation with PCRE `-P`. It integrates with style/portability checks rather than compression behavior.

## Risks and Test Signals
The lint strongly catches accidental non-ASCII source bytes but excludes shell, Python, docs, and other file types. It may fail on systems where `grep -P` is unavailable, making it less portable than the policy it enforces.

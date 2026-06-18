# sources/distributed-fs/ceph-client/scripts/rustc-version.sh

Purpose: `rustc-version.sh` prints the Rust compiler version in a comparable integer form that can represent Rust versions past 1.99.

Important APIs, types, and functions: `get_canonical_version()` maps `x.y.z` to `100000*x + 100*y + z`. The main path runs `"$@" --version`, splits the output, and canonicalizes the second word, which is expected to be the numeric rustc version.

Control flow: successful version command prints the canonicalized version. Failure prints `0` and exits with status 1.

State and persistence: no persistent state.

Dependencies and integration points: Makefiles and shell checks can call it with a rustc command or wrapper. It uses POSIX shell arithmetic and expects rustc-like version output.

Risks: if a wrapper prints extra words before `rustc`, `$2` may not be the version. Suffixes are not explicitly stripped here, so callers should verify input format or rely on rustc's normal output.

Test signals: run with real rustc, wrapper failures, and version strings around 1.100.0 to verify canonical ordering.

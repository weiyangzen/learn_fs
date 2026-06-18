# sources/distributed-fs/ceph-client/scripts/rustc-llvm-version.sh

Purpose: `rustc-llvm-version.sh` prints the LLVM version used by a rustc binary in a six-digit comparable integer form.

Important APIs, types, and functions: `get_canonical_version()` converts `x.y.z` to `10000*x + 100*y + z`. The script runs `"$@" --version --verbose`, greps the first `LLVM.*x.y.z` line, and canonicalizes the third shell word after `set -- $output`.

Control flow: if the command and grep succeed, it prints the canonical version. Otherwise it prints `0` and exits with status 1.

State and persistence: no persistent state; stdout is the version number.

Dependencies and integration points: used by Kbuild version checks or Makefile conditionals that need the Rust compiler's LLVM backend version. Depends on rustc verbose output format, grep, and POSIX shell.

Risks: output parsing assumes the LLVM version appears as the third whitespace-delimited token. Nonstandard rustc wrappers or localized output may produce `0`.

Test signals: test rustc wrappers with normal verbose output, missing rustc, and unexpected LLVM lines. Makefile consumers should treat `0` as unavailable.

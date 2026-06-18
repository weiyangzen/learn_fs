# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/setup-llvm-links.sh

Purpose: normalizes versioned LLVM tool names to unversioned names in `/usr/bin` for kernel build scripts that expect `clang`, `ld.lld`, `llvm-ar`, and related tools.

Important behavior: with `set -euo pipefail`, the script uses `which` and `ln -svf` to point `/usr/bin/clang++`, `clang`, `ld.lld`, `lld`, `llvm-ar`, `llvm-nm`, `llvm-objcopy`, `llvm-readelf`, and `llvm-strip` at their `${LLVM_VERSION}`-suffixed binaries.

Control flow: missing `LLVM_VERSION` or any missing tool aborts the script. Symlinks are overwritten forcefully.

State and persistence: mutates `/usr/bin` inside the CI container.

Dependencies and integration points: used by `dtbs-check.sh` and `kunit.sh` after GitLab jobs install `clang-${LLVM_VERSION}`, `lld-${LLVM_VERSION}`, and `llvm-${LLVM_VERSION}`.

Risks: requires permission to write `/usr/bin`. Force-updating global symlinks can affect later commands in the same job. `which` output is unquoted inside command substitution but tool paths are expected to be simple.

Test signals: symlink targets resolve to installed LLVM version; subsequent `make LLVM=1` and KUnit runs use the intended compiler/linker; missing package causes early failure.

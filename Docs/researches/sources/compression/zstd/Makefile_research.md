# sources/compression/zstd/Makefile

Purpose: top-level GNU Make orchestrator for zstd library, CLI, tests, examples, documentation, contrib tools, install/uninstall, and a large set of CI-oriented build variants.

Important targets and control flow: defaults build `lib-release` and `zstd-release`. `all` expands to `allmost examples manual contrib`; `allzstd` builds lib, programs, and tests; `zstd`/`zstd-release` build programs and symlink the root binary; `test` builds all program variants, runs tests, and educational decoder tests; `check` delegates to tests. Install/list targets are enabled on supported POSIX OSes. Variant targets cover compiler versions, C standards, cross-compilation, QEMU fuzz/test, sanitizers, static analysis, CMake, Meson, PGO, and dependency installation helpers.

State, dependencies, and integration: state is build outputs across `lib`, `programs`, `tests`, `examples`, `contrib`, wrapper dirs, `cmakebuild`, `mesonbuild`, and install staging. It depends on included `lib/install_oses.mk`, platform `uname`, compiler/tool variables, and optional external libraries.

Risks and test signals: many targets mutate shared build directories and call `clean`, so parallel external invocation needs care. The GitHub workflows exercise this file extensively; failures here usually indicate broad build-system regressions.

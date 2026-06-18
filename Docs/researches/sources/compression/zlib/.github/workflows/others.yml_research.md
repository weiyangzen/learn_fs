# sources/compression/zlib/.github/workflows/others.yml

Purpose: CI workflow for less common operating systems through VM-based GitHub Actions.

Important jobs/settings: covers DragonFlyBSD, FreeBSD aarch64/x86_64, NetBSD aarch64/x86_64, OmniOS, OpenBSD aarch64/x86_64/riscv64, and Solaris. OpenIndiana is present but commented out.

Control flow: each VM job checks out source, installs CMake and bzip2 or equivalent packages, configures zlib with minizip and bzip2 enabled where supported, builds, and runs CTest. FreeBSD excludes tests matching `.*summary`.

State and persistence: VM-local build directories only; `copyback: false` avoids syncing generated files back.

Dependencies and integration: uses `vmactions/*-vm` actions, platform package managers, CMake, and CTest. Exercises portability of root CMake and minizip paths.

Risks: VM actions and package repositories are external moving parts. Some jobs run `ctest` without `--output-on-failure`, reducing diagnostic detail. OpenBSD prepare contains a bare `bzip2` line after `pkg_add cmake`, which may be intentional command availability check or a typo.

Test signals: broad OS portability signal for configure-free CMake builds, especially non-Linux Unix variants.

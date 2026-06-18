# sources/control-plane/rook/.github/workflows/build.yml

Purpose: Rook pull-request build workflow for macOS and Linux.

Important configuration and control flow: triggers on `pull_request`, uses strict bash defaults, cancels superseded runs by workflow/head ref, and grants contents read. `macos-build` skips PRs labeled `skip-ci`, checks out full history, installs Go 1.26 and Helm 3.18.2, runs build, codegen, module check, CRD generation, and RBAC generation, validating modified files after each generated step. `linux-build-all` runs on Ubuntu 22.04 for Go 1.25 and 1.26, installs QEMU, and delegates to `tests/scripts/github-action-helper.sh build_rook_all`.

State, dependencies, and integration: state is CI workspace output and generated file diffs. It depends on pinned checkout/setup-go/setup-helm/setup-qemu actions, Make targets, Go toolchains, Helm, Docker/QEMU, and Rook test scripts.

Risks and test signals: macOS `make -j$nproc` may rely on shell variable behavior; Linux uses a matrix for compatibility. Signals are build success and validation scripts confirming generated artifacts are committed.

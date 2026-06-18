# sources/cloud-native/composefs/.github/workflows/test.yaml

Purpose: primary CI workflow for C composefs builds, formatting, sanitizer tests, baseline builds, integration tests, distcheck, and required-check aggregation.

Important APIs/types/functions: jobs `clang-format`, `build` with ASAN/UBSAN and unit tests, `build-noasan`, `build-baseline` on Ubuntu Focal, `build-latest-clang`, `integration`, `distcheck`, and `required-checks`.

Control flow: builds install dependencies, configures Meson with `--werror` and optional sanitizers, compiles/tests, uploads artifacts/logs, runs integration tests after installing kernel modules/fsverity and extracted artifacts, then required-checks inspects `needs` JSON for failures.

State/persistence: CI artifacts, Meson logs, installed composefs tar in integration runner, and ephemeral build directories.

Dependencies/integration: GitHub Actions, Meson/Ninja, apt, erofs-utils, go-md2man, Linux modules, fsverity, jq, and repository integration scripts.

Risks/test signals: broad and valuable signal set; risks include sanitizer package names (`libasan6`) and baseline dependency allowances drifting. Required-checks sentinel allows skipped jobs but fails failed/cancelled jobs.

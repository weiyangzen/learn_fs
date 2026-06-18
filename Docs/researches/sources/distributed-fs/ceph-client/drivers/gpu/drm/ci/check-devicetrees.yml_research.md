# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-devicetrees.yml

Purpose: adds GitLab CI jobs for device-tree binding and DTB schema checks scoped to display/GPU schemas.

Important jobs/templates: `.dt-check-base` runs in `static-checks`, sets `GIT_DEPTH=1`, enables GitLab's new bash eval strategy, sets default `SCHEMA=display:gpu`, creates a venv at `/tmp/dtcheck-venv`, installs clang/lld/llvm for `$LLVM_VERSION`, Python venv/pip, yamllint, and `dtschema`, then runs `drivers/gpu/drm/ci/${SCRIPT_NAME}`. It preserves `${ARTIFACT_FILE}` on failure and allows exit code 102 for warnings. `dtbs-check:arm32` and `dtbs-check:arm64` extend architecture build templates and run `dtbs-check.sh`. `dt-binding-check` extends the x86_64 build container and runs `dt-binding-check.sh`.

Control flow: the shell scripts produce normal failure exit 1 for make errors and exit 102 when stderr log files are non-empty, so schema warnings can be soft failures.

State and persistence: creates a per-job Python virtual environment, log files `dtbs-check.log` or `dt-binding-check.log`, and failure artifacts.

Dependencies and integration points: depends on `.build:*` templates, Debian packages, kernel DT build targets, the `dtschema` Python package, `setup-llvm-links.sh`, and environment variables `KERNEL_ARCH`, `LLVM_VERSION`, `SCRIPT_NAME`, and `ARTIFACT_FILE`.

Risks: `pip install dtschema` is not pinned, so schema tooling can change independently. `SCHEMA=display:gpu` narrows coverage and may miss non-display dependencies. Exit code 102 being allowed must remain aligned with GitLab and script behavior.

Test signals: job expansion for arm32/arm64 binding checks, venv activation, successful `make dt_binding_check`/`dtbs_check`, warning-only jobs marked allowed failure, and log artifacts on warnings or failures.

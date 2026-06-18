# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/dt-binding-check.sh

Purpose: runs the kernel `dt_binding_check` target for DRM CI with a configurable schema filter and treats warnings as a distinct soft-failure status.

Important behavior: the script uses `set -euxo pipefail`, activates `${VENV_PATH:-/tmp/dtschema-venv}`, runs `make -j${FDO_CI_CONCURRENT:-4} dt_binding_check DT_SCHEMA_FILES="${SCHEMA:-}"` with stderr redirected to `dt-binding-check.log`, exits 1 on make failure, and exits 102 if the log file is non-empty after a successful make.

Control flow: all setup is expected to be done by `check-devicetrees.yml`; this script only activates the venv and runs make. Exit 102 is intentionally allowed by CI for warning-only reports.

State and persistence: writes `dt-binding-check.log`, which becomes a failure artifact.

Dependencies and integration points: depends on a Python venv containing `dtschema`, kernel make targets, `FDO_CI_CONCURRENT`, and optional `SCHEMA`. Used by the `dt-binding-check` GitLab job.

Risks: any stderr output, even benign make noise, is treated as warnings and exit 102. If the venv path is wrong, `source` fails immediately. No LLVM setup is done here because binding checks normally do not need the compiler symlink helper.

Test signals: successful empty-log binding check, warning log causing exit 102, make failure causing exit 1, and schema filtering through `SCHEMA=display:gpu`.

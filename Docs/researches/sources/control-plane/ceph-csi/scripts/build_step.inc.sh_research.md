<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build_step.inc.sh -->
## sources/control-plane/ceph-csi/scripts/build_step.inc.sh

Purpose: shared shell helper for periodic build-step progress logging.

APIs and control flow: creates a temp file for current step, `build_step` writes the step and starts a background loop that logs `running:` every minute, and `build_steps_cleanup` kills the logger and removes the temp file via EXIT trap.

State and persistence: temporary file and background process. No repo state.

Dependencies: POSIX shell utilities, `date`, `mktemp`, `sleep`, `kill`.

Integration points: sourced by build scripts to avoid silent long-running CI stages.

Risks: `build_step` never calls a separate done function; callers rely on overwriting current step and final trap. If a sourced script exits abnormally without trap execution, temp/log process cleanup could lag.

Test signals: no tests; behavior is operational in CI logs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build_step.inc.sh -->

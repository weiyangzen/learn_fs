# sources/control-plane/mayastor/scripts/release.sh

Purpose: Mayastor-specific wrapper around shared dependency release tooling for Docker image builds/uploads.

Important APIs/types/functions: sets `SOURCE_REL` default to `utils/dependencies/scripts/release.sh`, initializes submodules when needed outside CI, sets `IMAGES`, `CARGO_DEPS`, and `PROJECT`, sources the shared release script, and calls `common_run "$@"` unless `NO_RUN=true`.

Control flow: mostly delegates to sourced release logic after project variables are set.

State/persistence: may initialize submodules and build/push Docker images depending on shared script arguments.

Dependencies/integration: integrates with repository dependency submodule release framework and Docker registry credentials.

Risks: behavior is opaque without the sourced script. Sourcing external shell code means variable/function names can collide.

Test signals: dry-run or release CI should show expected image list: `mayastor.io-engine`, `mayastor.casperf`, and `fio-spdk`.

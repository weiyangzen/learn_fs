# sources/cloud-native/ostree/tests/admin-test.sh

Purpose: large sourced integration test script for `ostree admin` workflows: sysroot initialization, deployment, bootloader layout, status, upgrades, origins, remote config placement, undeploys, kernel arguments, downgrade guards, and fsfreeze watchdog behavior.

Important operations: initializes sysroots with modern/epoch modes; defines `validate_bootloader()` and `assert_ostree_deployment_refs()`; pulls local commits; deploys with kargs; verifies status text and JSON; checks composefs artifacts when enabled; tests `--print-current-dir`; validates bootloader directories/entries and deployment refs across multiple deploys; exercises staging failure when not booted; independent OS deployments; retain/rollback behaviors; modified `/etc` merge; undeploy errors; upgrades with remote add; set-origin; deploy unknown OS failure; multiple kargs; upgrade title/version formatting; override commit downgrade policy; source title display; remote add to physical and nonphysical sysroot; `core.add-remotes-config-dir=false`; and fsfreeze failure injection.

Control flow: linear shell assertions under `set -euo pipefail`, with many `echo "ok ..."` checkpoints. It mutates the test sysroot through a progression of deployments, upgrades, and cleanup operations, checking filesystem and command output after each stage.

State/persistence: creates/removes sysroot directories, repository refs, deployment directories, bootloader entries, origin files, remote config entries, and test commits. It deliberately changes deployment `/etc`, symlinks deployment `sysroot` for nonphysical tests, and configures repo settings.

Dependencies/integration: depends on the broader test harness for `CMD_PREFIX`, `assert_*`, `fatal`, `test_tmpdir`, `os_repository_new_commit`, `has_ostree_feature`, `bootcsum`, and repository fixtures. Uses `jq`, `stat`, `diff`, `sort`, and helper Python `bootloader-entries-crosscheck.py`.

Risks: because it is sourced, it assumes harness variables/functions are defined and current directory is controlled. Many assertions depend on exact bootversion/subbootversion layout and command output. Sleep is used to create chronological commit differences.

Test signals: broad high-value integration coverage for `ot-main` admin parsing, remote add/list behavior, deployment state persistence, bootloader integration, and upgrade/downgrade safety. It does not directly test prepare-root mount namespace code.

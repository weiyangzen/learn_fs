<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/install-wrappers.sh -->
## sources/cloud-native/ostree/tests/kolainst/install-wrappers.sh

Purpose: generates one kola wrapper script per Rust destructive test listed by `ostree-test list-destructive`.

Important APIs/functions: reads a list file, symlinks `../nondestructive-rs` as `${testdir}/data`, and writes executable shell wrappers that exec `${KOLA_EXT_DATA}/ostree-test run-destructive <name>`.

Control flow/state: modifies the target install tree by creating a symlink and wrapper files. Uses `set -xeuo pipefail` for fail-fast install behavior.

Dependencies/integration: called by the kola `Makefile` during install. Depends on `KOLA_EXT_DATA` being set at runtime by kola and on destructive-list contents matching Rust test names.

Risks/test signals: unquoted wrapper names from list input can be problematic if names contain spaces, though current function paths do not. Signal is generated executable wrappers per listed test.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/install-wrappers.sh -->

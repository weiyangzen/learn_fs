<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-extras.sh -->
## sources/control-plane/ceph-csi/scripts/lint-extras.sh

Purpose: runs non-Go lint checks for shell, YAML, Markdown, Helm charts, and Python.

APIs and control flow: `run_check` finds matching files excluding vendor and runs a checker if installed, warning unless `lint-all` set `all_required=1`. Commands include `lint-shell`, `lint-yaml`, `lint-markdown`, `lint-helm`, `lint-py`, and `lint-all`.

State and dependencies: no persistent state. Depends on shellcheck, bash, yamllint, mdl, helm, pylint, find/xargs.

Integration points: CI lint jobs and local developer checks.

Risks: optional mode silently skips missing tools for individual lint commands. Regex-based file selection can miss unusual filenames or include generated files not intended. Helm lint command expands chart dirs dynamically.

Test signals: no tests; CI exit status is validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-extras.sh -->

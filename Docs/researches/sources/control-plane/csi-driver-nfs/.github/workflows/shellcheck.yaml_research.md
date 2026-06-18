# sources/control-plane/csi-driver-nfs/.github/workflows/shellcheck.yaml

Purpose: runs ShellCheck for NFS driver shell scripts on protected branches, release branches, version tags, and PRs.

Important APIs and types: uses pinned checkout and pinned `ludeeus/action-shellcheck`, sets `SHELLCHECK_OPTS: -e SC2034`, warning severity, checks scripts together, ignores `vendor`, `release-tools`, and `hack`, and formats output as gcc.

Control flow: GitHub triggers, action scans eligible shell scripts, and reports annotations.

State and persistence: workflow annotations/logs only.

Dependencies and integration: complements release-tools shellcheck but intentionally excludes imported release-tools and hack scripts.

Risks: warning severity may not fail issues depending on action behavior. Ignored paths can contain shell code not covered here.

Test signals: workflow status and annotations.

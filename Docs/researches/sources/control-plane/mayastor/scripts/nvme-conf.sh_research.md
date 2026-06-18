# sources/control-plane/mayastor/scripts/nvme-conf.sh

Purpose: validates and optionally writes NVMe host identity files under the NVMe sysconf directory.

Important APIs/types/functions: defaults to `/etc/nvme`, fixed hostid `03f79caf-dc58-475a-a111-bf0b75214a51`, and matching hostnqn. Options include `--apply`, `--check`, `--overwrite`, `--hostid`, `--hostnqn`, `--sysconfdir`, and help.

Control flow: parses args, reads existing `hostid` and `hostnqn`, prints current/requested state, exits success on valid/matching config, exits failure if check fails without apply, enforces overwrite for existing files, creates directory/files when allowed, checks write permissions, and writes requested values.

State/persistence: mutates `/etc/nvme/hostid` and `/etc/nvme/hostnqn` or an alternate sysconfdir.

Dependencies/integration: used by cargo, grpc, and pytest wrappers to ensure stable NVMe host identity for tests.

Risks: apparent bug checks `-f "$NVME_SYSCONFDIR_HOSTID_P"` before reading hostnqn, so hostnqn detection depends on hostid file existence. Missing quote in one permission error message. Requires elevated permissions for default path.

Test signals: `--check` returning `0` indicates nonempty hostid and hostnqn are present.

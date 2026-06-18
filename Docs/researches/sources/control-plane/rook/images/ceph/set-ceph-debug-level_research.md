# sources/control-plane/rook/images/ceph/set-ceph-debug-level

Purpose: helper script to set or reset Ceph debug levels across many Ceph subsystems.

Important APIs/types/functions: Bash functions `check` and `exec_ceph_command`; accepts integer 0 through 20 or `default`; iterates `CEPH_DEBUG_FLAG` and runs `ceph config set global debug_<flag> <level>` or `ceph config rm global debug_<flag>`.

Control flow: validates the single argument, builds ceph config commands for each debug flag, runs them in the background, and waits for all updates.

State and persistence: modifies Ceph monitor configuration database for global debug settings.

Dependencies/integration: requires `ceph` CLI configured with admin or suitable caps.

Risks: high debug levels can flood logs and storage; background commands suppress output, so individual failures may be hard to diagnose.

Test signals: invalid input exits non-zero, `default` removes settings, and `ceph config dump` reflects expected debug keys.

# sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.c

Purpose: FreeBSD C constructor support for parent/child startup synchronization and session/process-group setup.

Important APIs/types/functions: `_containers_unshare_parse_envint` and `_containers_unshare`.

Control flow: reads pipe fd environment values, writes child PID to the parent, waits on the continue pipe, optionally calls `setsid`, `setpgrp(0,0)`, and `TIOCSCTTY`.

State/persistence: mutates session, process group, controlling terminal, and consumes environment variables. It does not create Linux-style namespaces.

Dependencies/integration: coordinated by `unshare_freebsd.go` `Cmd.Start` through extra files and environment.

Risks: exits the process on malformed env or setup failures. It shares the early-constructor risks of the Linux C path but with fewer features.

Test signals: FreeBSD command tests should verify PID synchronization, `Setsid`, `Setpgrp`, and controlling terminal behavior.

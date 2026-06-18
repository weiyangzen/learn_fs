# sources/cloud-native/containers-storage/pkg/unshare/unshare_test.go

Purpose: Linux integration tests for the unshare command wrapper and C constructor path.

Important APIs/types/functions: `TestMain`, reexec handler `report`, `CloneFlags`, `Report`, and tests `TestUnshareNamespaces`, `TestUnsharePgrp`, `TestUnshareSid`, `TestUnshareOOMScoreAdj`, and `TestUnshareIDMappings`.

Control flow: registers a child command that reports namespace symlink targets, uid/gid maps, pgrp, sid, and OOM score as JSON. Tests run that command through `Command`, configure flags/options, decode JSON, and compare child state to parent expectations.

State/persistence: creates child processes and user namespaces; reads `/proc/self/ns`, `/proc/self/oom_score_adj`, and uid/gid maps.

Dependencies/integration: validates Go `Cmd.Start`, C early unshare, reexec, Linux `/proc`, and capability-dependent namespace behavior.

Risks: tests require kernel support for user namespaces and relevant clone flags; unprivileged CI may fail if userns is disabled. The tests are Linux-only.

Test signals: strong end-to-end signal for synchronization, namespace creation, ID mapping, session/pgrp, and OOM score setup.

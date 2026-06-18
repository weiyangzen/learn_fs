# sources/cloud-native/moby/integration/container/remove_test.go

Purpose: Container removal tests for missing bind sources, anonymous volume cleanup, running-container conflicts, force removal, invalid IDs, and auto-remove cleanup after daemon restart.

Important APIs and flow: `dPath` maps Linux paths to Windows-style daemon paths. Tests create containers with bind mounts or anonymous volumes, remove host source directories, call `ContainerRemove` with `RemoveVolumes` or `Force`, and inspect container/volume absence with not-found errors. The daemon restart test runs an auto-remove top container on a child daemon and expects it gone after restart.

State and dependencies: Mutates host temp directories, daemon volumes, container metadata, and child-daemon state. Remote and Windows skips apply for local bind/remove and multi-daemon scenarios.

Risks and signals: It guards cleanup correctness and prevents stale container/volume metadata. Failures can leave leaked volumes, make `rm` fail after host path deletion, or allow unsafe removal semantics.

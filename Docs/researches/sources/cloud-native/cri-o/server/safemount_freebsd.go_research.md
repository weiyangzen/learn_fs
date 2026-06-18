# sources/cloud-native/cri-o/server/safemount_freebsd.go

Purpose: FreeBSD placeholder for secure subpath mounting.

Important APIs and functions: empty `safeMountInfo`, no-op `Close`, and `safeMountSubPath` returning an empty info object with nil error.

Control flow: all inputs are ignored.

State and persistence: no file descriptors, mounts, or temporary paths are created.

Dependencies and integration: provides the same API as Linux for container mount setup.

Risks: callers receive apparent success without an actual bind mount on FreeBSD; platform code must not depend on Linux subpath behavior there.

Test signals: no direct tests in this subset.

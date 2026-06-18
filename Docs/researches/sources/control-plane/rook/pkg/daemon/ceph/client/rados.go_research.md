# sources/control-plane/rook/pkg/daemon/ceph/client/rados.go

This file provides low-level RADOS object helpers used by higher-level Rook controllers for object locks, namespace object detection, and idempotent object deletion.

The lock API is `RadosLockObject()` and `RadosUnlockObject()`. Lock creation generates a random hex cookie, calls `rados lock get` with pool, namespace, tag, cookie, and duration, and returns the cookie as the caller's unlock handle. Unlock first queries `radosObjectLockInfo()`, treats mismatched locks or absent cookies as already-unlocked success, and uses `rados lock break` only when it finds a locker with the matching cookie. `findLockerWithCookie()` is a small lookup helper. `RadosNamespaceHasObjects()` builds finalized rados arguments and shells through `head -c 1` to avoid buffering an entire namespace listing. `RadosRemoveObject()` stats before removing and treats non-timeout stat errors as the object already being absent.

State is in RADOS object locks and objects; no Kubernetes state is written. Dependencies include cryptographic randomness, JSON parsing of lock info, command finalization, `NewRadosCommand`, and Ceph command timeouts.

Risks include shell command construction in `RadosNamespaceHasObjects()`, lock-cookie collision assumptions, and broad idempotency that treats most stat errors as absence. `rados_test.go` focuses on removal behavior, including timeout propagation, stat idempotency, remove errors, and successful removal.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace_test.go

Purpose: unit tests for RBD cleanup in block pools and Rados namespaces.

Important APIs/types/functions: `TestRadosNamespace`, `TestBlockPoolCleanup`, and `TestGetClientIPs` use mock executor command argument assertions with fixture JSON for images, snapshots, and watcher status.

Control flow: tests cover empty image lists, images with snapshots, snapshot removal, trash move, trash deletion task formatting with and without namespace, and watcher-client deduplication across images.

State and persistence behavior: all Ceph operations are mocked through `MockExecuteCommandWithOutput`; no real cluster is mutated.

Dependencies and integration points: depends on cleanup functions, Ceph client command wrappers, `clusterd.Context`, exec test mocks, and testify assertions.

Risks: tests emphasize success paths and command shape, but do not cover blocklist command failure, snapshot/list failure accumulation, trash failures, or malformed JSON from Ceph commands.

Test signals: strong signal for command argument compatibility between cleanup code and Ceph client helpers for namespace-aware and pool-wide RBD deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace_test.go -->

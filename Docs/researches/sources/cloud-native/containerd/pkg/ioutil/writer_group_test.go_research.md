# sources/cloud-native/containerd/pkg/ioutil/writer_group_test.go

Purpose: unit tests for `WriterGroup` registry and fan-out semantics.

Important APIs/types/functions: local `writeCloser` records written bytes and close state. `TestEmptyWriterGroup` checks writes to an empty group. `TestClosedWriterGroup` verifies add-after-close immediately closes the writer. `TestAddGetRemoveWriter` exercises add, retrieval, write, removal, and close. `TestReplaceWriter` ensures replacing an existing key closes the old writer and directs subsequent writes to the new one.

Control flow: tests create a group, mutate writer membership, call `Write` or `Close`, and assert writer content and close flags.

State/persistence: in-memory buffers only.

Dependencies/integration: same-package tests with Go `testing` and simple fake write closers.

Risks: does not cover underlying writer errors or concurrent method calls. Close error swallowing is not asserted.

Test signals: confirms the intended ownership rule: once a writer is removed, replaced, or added after group closure, the group closes it.

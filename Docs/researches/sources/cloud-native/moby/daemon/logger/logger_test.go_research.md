# sources/cloud-native/moby/daemon/logger/logger_test.go

Purpose: test-package helper code for copying core logger messages.

Important APIs/types/functions: `(*Message).copy` deep-copies `Line` and `Attrs` while copying scalar fields and `PLogMetaData` pointer.

Control flow/state/persistence: in-memory helper only; no `Test*` function is defined in this file. It supports nearby tests that need message copies without aliasing line/attrs slices.

Dependencies/integration: imports `backend.LogAttr`; used from logger package tests.

Risks: `PLogMetaData` is not deep-copied, so tests using this helper must not mutate shared partial metadata through either message.

Test signals: helper only; no standalone assertions in this file.

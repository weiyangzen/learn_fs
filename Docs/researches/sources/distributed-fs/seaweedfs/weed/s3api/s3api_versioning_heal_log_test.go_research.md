<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_heal_log_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_heal_log_test.go

Purpose: pins the log format and sanitization behavior for versioning heal/reconciler events.

Important APIs/functions: tests cover `versioningHealLogPrefix`, `versioningHealInfof`, `sanitizeHealArg`, `sanitizeHealArgs`, and the documented event vocabulary.

Control flow: tests reproduce expected log-line assembly, smoke-call the logger with percent-containing strings, assert unsafe strings/errors are `strconv.Quote` escaped, and verify event names are explicit and token-safe.

State and persistence behavior: no persistent state. It protects operator-facing logs rather than data paths.

Dependencies and integration: uses glog, flag initialization, errors, fmt, strings, and testify. It guards helper functions in `s3api_versioning_reconciler.go` used by queue and healing events.

Risks: tests mostly avoid capturing glog output, so final sink formatting is not fully asserted. The vocabulary list includes events emitted outside the visible reconciler file, making it a documentation contract that must be updated alongside code changes.

Test signals: passing tests mean user-controlled bucket/object/error fields cannot split log tokens or inject fake `event=` fields, and the `[versioning-heal] event=...` prefix remains stable for dashboards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_heal_log_test.go -->

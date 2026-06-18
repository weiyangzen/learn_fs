# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_old_entry_test.go

Purpose: fills coverage for event builder options when events have only `OldEntry` or need bootstrap-version attachment.

Important tests: `WithModTime`, `WithTtlSec`, `WithVersionID`, `WithExtended`, and `WithChunks` apply to `OldEntry` on delete events. `WithBootstrapVersion` attaches the same pointer to create, delete, and update events. `TestEventOption_NoPanicOnEmptyEvent` applies all options to a degenerate empty event and verifies entry-targeting options do not allocate entries while bootstrap-version still sets the event field.

Control flow/state: confirms generic option fall-through branches in `eventbuilder.go`. No persistence; uses constructed `reader.Event`.

Dependencies/integration: imports filer chunks, S3 constants, and `reader.BootstrapVersion`.

Risks: these tests document no-op behavior that callers may depend on when composing options. If future options allocate missing entries, test fixture semantics would change.

Test signals: focused branch coverage for delete/old-entry paths that create/update-oriented tests would miss.

# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind_test.go

Purpose: regression tests for lifecycle action-kind expansion and stable storage labels.

Important APIs/types: tests call `RuleActionKinds` and `ActionKind.String()`.

Control flow: table tests cover each standalone action. Separate tests validate multi-action rules, noncurrent/newer-noncurrent subsumption, nil/empty rules, and string labels.

State and persistence behavior: the string test is explicitly a persistence guard because labels are directory names on disk.

Dependencies and integration points: depends on the local `Rule` model and `mustTime` helper in the same package's tests.

Risks: tests do not cover proto conversion or engine compilation directly. A new action kind can pass this file if developers forget to update dispatch mappings elsewhere.

Test signals: strong coverage of a previous bug where multi-action XML rules collapsed into one action instead of producing independent action keys.

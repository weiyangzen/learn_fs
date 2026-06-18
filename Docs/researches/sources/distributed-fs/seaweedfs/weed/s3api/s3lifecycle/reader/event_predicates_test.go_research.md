# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/event_predicates_test.go

Purpose: direct tests for `reader.Event` create/delete predicates.

Important tests: a populated `NewEntry` with nil `OldEntry` is create; populated `OldEntry` with nil `NewEntry` is delete; update events with both entries are neither; degenerate events with neither entry are neither.

Control flow/state: pure predicate checks over event entry fields. No persistence.

Dependencies/integration: uses filer protobuf entries. Dispatcher/router paths use these predicates to select create/delete/update routing behavior.

Risks: classifying updates as creates or deletes would route pointer transitions incorrectly. Classifying empty metadata events could trigger spurious lifecycle dispatch.

Test signals: small but important direct coverage for routing-critical predicates.

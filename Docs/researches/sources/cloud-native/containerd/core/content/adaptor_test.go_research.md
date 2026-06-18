# sources/cloud-native/containerd/core/content/adaptor_test.go

Purpose: unit tests for `AdaptInfo`.

Important coverage: table-driven tests check absent empty field path, digest string conversion, unsupported `size`, simple `labels.foo`, and joined dotted label path `labels.foo.bar.qux`.

Control flow and state: each test constructs an `Info`, calls `AdaptInfo`, then calls `Field` with the field path and compares value plus presence with testify assertions.

Dependencies and integration: exercises the filter adaptor without invoking the full filters parser/matcher.

Risks: no negative label lookup tests with non-empty maps, no nil map behavior beyond absent labels through default zero values, and no integration with parsed filter expressions.

Test signals: good focused signal for the adaptor's current public behavior, especially that size is not currently filterable.

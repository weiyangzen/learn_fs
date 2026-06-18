<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/filters_test.go -->
# sources/cloud-native/moby/client/filters_test.go

Purpose: tests the `Filters` helper.

Important coverage: adding multiple values to terms, encoding filters into URL values, empty filter behavior, and deep-copy behavior of `Clone`.

Control flow and dependencies: tests build filter maps, compare JSON query strings, mutate clones, and assert original maps are unaffected.

State and risks: no persistence. The tests protect shared query semantics used by many list/prune methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/filters_test.go -->

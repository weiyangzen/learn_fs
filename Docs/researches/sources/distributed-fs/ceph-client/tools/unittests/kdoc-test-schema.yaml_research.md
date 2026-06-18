# sources/distributed-fs/ceph-client/tools/unittests/kdoc-test-schema.yaml

## Purpose

`kdoc-test-schema.yaml` defines the JSON Schema used to validate dynamic kernel-doc test cases in `kdoc-test.yaml`.

## Important APIs, Types, and Fields

The schema describes a top-level `tests` array. Each test object has required `name`, `fname`, and `expected` fields, with optional `description`, `source`, and `exports`. Expected entries may contain a `kdoc_item` object, `rst` string, and/or `man` string. `kdoc_item` properties mirror `KdocItem` data: name, type, declaration line, sections, parameter lists/descriptions/types, and `other_stuff`.

## Control Flow and Data Flow

There is no executable control flow. `test_kdoc_test_schema.py` loads this file with YAML, creates a `Draft7Validator`, and validates the dynamic test YAML before parser/output tests consume it.

## State and Persistence Behavior

The file persists the contract for test data shape. It does not store test results.

## Dependencies and Integration Points

It depends on JSON Schema draft-07 semantics and Python `jsonschema` when available. It integrates with kernel-doc parser/output unit tests and the YAML test corpus.

## Risks and Edge Cases

The schema is permissive in places, especially `other_stuff` and expected-output strings. The `anyOf` block appears intended to require either `kdoc_item` or `source`, but indentation/shape must be validated carefully because YAML-to-JSON-schema mistakes can silently weaken checks. The schema requires `expected` but not necessarily every output flavor.

## Test Signals

Pass signals are successful schema loading and no validation errors for `kdoc-test.yaml`. Negative schema tests would be useful for missing required fields, malformed `kdoc_item`, and invalid expected entries.

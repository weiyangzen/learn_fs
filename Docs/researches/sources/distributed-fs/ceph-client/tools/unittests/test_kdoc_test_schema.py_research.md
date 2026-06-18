# sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_test_schema.py

## Purpose

`test_kdoc_test_schema.py` validates that `kdoc-test.yaml` conforms to `kdoc-test-schema.yaml` when the optional `jsonschema` package is available.

## Important APIs, Types, and Functions

The central class is `TestYAMLSchemaValidation`. `setUpClass()` imports `Draft7Validator`, loads the schema, and stores a validator. `test_kdoc_test_yaml_followsschema()` loads test data, collects validation errors, and fails with all messages if any exist.

## Control Flow and Data Flow

At runtime the test attempts to import `jsonschema`. If unavailable, it prints a warning and skips validation by returning from the test. If available, schema and test YAML files are loaded with `yaml.safe_load()` and checked.

## State and Persistence Behavior

The test reads YAML files only and writes no state. Class attributes cache the validator.

## Dependencies and Integration Points

It depends on PyYAML, optional `jsonschema`, unittest, and repository path layout. It complements `test_kdoc_parser.py` by checking data shape before dynamic parser tests use the corpus.

## Risks and Edge Cases

Missing `jsonschema` turns validation into a soft skip, so CI environments without the package lose this signal. The method name has a typo (`followsschema`) but is still discovered. Schema permissiveness can still allow semantically poor expected data.

## Test Signals

The key pass signal is zero schema validation errors. A warning about missing `jsonschema` means parser tests may still run but schema coverage is absent.

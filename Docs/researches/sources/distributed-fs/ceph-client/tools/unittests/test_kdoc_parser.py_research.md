# sources/distributed-fs/ceph-client/tools/unittests/test_kdoc_parser.py

## Purpose

`test_kdoc_parser.py` validates the Python kernel-doc parser and output formatters, using both hand-written self-tests and dynamically generated tests from `kdoc-test.yaml`.

## Important APIs, Types, and Functions

Key helpers are `clean_whitespc()`, `MockLogging`, `MockKdocConfig`, `GenerateKdocItem.run_test()`, `cleanup_timestamp()`, and `gen_output()`. Dynamic test classes include `CToKdocItem`, `KdocItemToMan`, `KdocItemToRest`, `CToMan`, and `CToRest`. `KernelDocDynamicTests.create_tests()` attaches methods at import time.

## Control Flow and Data Flow

Parser tests patch `open()` with mocked source, construct `KernelDoc`, parse entries and export tables, and compare normalized `KdocItem` dictionaries. Output tests either render expected items or parse source then render to man/RST. The main entry point accepts `--yaml-file` and passes environment overrides to `TestUnits`.

## State and Persistence Behavior

Tests run in memory using mocked file reads. The selected YAML path can be passed through an environment dictionary. Logging is captured in a custom handler for possible warning assertions.

## Dependencies and Integration Points

It depends on PyYAML, unittest/mock, `KdocConfig`, `KdocItem`, `KernelDoc`, `RestFormat`, `ManFormat`, `CTransforms`, and `TestUnits`. It is the primary integration test between parsing, transform, export-symbol handling, and output generation.

## Risks and Edge Cases

Whitespace cleanup and timestamp normalization intentionally relax some output differences. Dynamic test creation assumes the YAML has already been schema-valid and can generate method-name collisions if scenario names repeat. Several `@expectedFailure` tests validate that the harness fails on empty or incomplete expectations.

## Test Signals

Passing tests confirm exported-symbol parsing, section/parameter extraction, dynamic YAML scenarios, RST rendering, man rendering, and source-to-output pipelines. Running with alternate `--yaml-file` verifies corpus extensibility.

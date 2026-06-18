# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_helper.py

## Purpose
Provides small list, category, and pretty-print helpers used by `tdc.py` when discovering and displaying test cases.

## Important APIs, Types, and Functions
Functions are `get_categorized_testlist`, `get_unique_item`, `get_test_categories`, `list_test_cases`, `list_categories`, `print_list`, `print_sll`, and `print_test_case`.

## Control Flow
Helpers take loaded JSON test dictionaries and compute category groupings, ordered unique lists, or user-facing display text. `tdc.py` calls these during `--list`, `--show`, category discovery, and ID generation flows.

## State and Persistence Behavior
All functions are stateless and return derived values or print to stdout. No files or global state are modified.

## Dependencies and Integration Points
Depends only on Python built-ins. It integrates with TDC CLI selection and display paths.

## Risks and Edge Cases
`get_unique_item` returns the original list unchanged when length is one, but a new list for longer inputs; callers should not depend on object identity. `print_test_case` treats lists specially but prints other nested structures with `str()`, which is adequate for display but not stable serialization.

## Test Signals
Signals include correct ordered category discovery, duplicate-free category lists, readable `--list` output, and full case details in `--show`.

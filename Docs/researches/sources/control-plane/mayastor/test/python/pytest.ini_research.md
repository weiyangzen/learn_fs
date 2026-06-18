# sources/control-plane/mayastor/test/python/pytest.ini

## Purpose
pytest configuration for Mayastor Python tests.

## Important APIs, Types, And Functions
Sets `log_cli = true`, `log_level = warn`, `console_output_style = classic`, and `asyncio_default_fixture_loop_scope = function`.

## Control Flow
pytest reads this configuration before collecting tests.

## State And Persistence
No runtime state beyond pytest configuration.

## Dependencies And Integration Points
Applies to pytest, pytest-asyncio, and logging output for the Python test tree.

## Risks
Changing async fixture loop scope can affect tests using module-scoped async resources. Warn-level logging may hide useful debug details in flaky integration failures.

## Test Signals
Consistent collection/runtime behavior and visible warnings/errors in console output.

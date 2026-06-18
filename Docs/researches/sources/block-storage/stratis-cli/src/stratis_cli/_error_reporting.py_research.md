# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_error_reporting.py

## Role

Turns chained exceptions from action execution into user-facing CLI error messages and exits with the correct error code.

## Error Interpretation

- `_interface_name_to_common_name()` maps D-Bus interface names to resource names.
- `_interpret_errors_0()` handles raw D-Bus errors such as access denied, service unknown, and missing daemon cases.
- `_interpret_errors_1()` handles generated-client errors, engine errors, user errors, version errors, incoherence, synthetic uevent failures, and invocation wrappers.
- `_interpret_errors_2()` handles method/property invocation context for zbus failures, disconnected bus, failed `GetManagedObjects`, property get failures, and no-reply timeouts.
- `_interpret_errors()` validates the chain starts with `StratisCliActionError`.
- `handle_error()` prints or raises based on whether a known explanation exists.

## Dependencies

Depends on D-Bus exceptions, generated-client exception/context types, action interface constants, `get_errors()`, CLI error classes, and `exit_()`.

## Notable Behavior

For missing daemon detection, it optionally imports `psutil` to distinguish “stratisd not running” from service connection problems.

## Risk Areas

This module encodes operational assumptions about D-Bus failure modes. If generated-client errors or stratisd error names change, explanations can become misleading or fall into the unexpected-error path.

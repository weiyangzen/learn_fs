# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_environment.py

## Role

Validates and converts environment-provided D-Bus timeout values.

## Main Behavior

`get_timeout(value: str)` parses the value as an integer number of milliseconds and enforces a positive timeout.

## Error Handling

Raises `StratisCliEnvironmentError` when the value is not an integer or is less than one.

## Dependencies

Only depends on the shared error type.

## Notable Behavior

This file isolates environment validation so D-Bus client generation can fail early with a CLI-specific setup error instead of a lower-level timeout/configuration exception.

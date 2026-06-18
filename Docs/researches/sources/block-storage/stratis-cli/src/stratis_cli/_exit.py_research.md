# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_exit.py

## Role

Defines process exit codes and a common exit helper.

## Exit Codes

`StratisCliErrorCodes` includes:

- `OK = 0`
- `ERROR = 1`
- `PARSE_ERROR = 2`

## Main API

`exit_(code, msg)` prints the message to stderr and exits with the integer value of the enum.

## Dependencies

Uses `sys.exit` and `enum.IntEnum`.

## Notable Behavior

All centralized error-reporting exits pass through this helper, keeping CLI status codes consistent.

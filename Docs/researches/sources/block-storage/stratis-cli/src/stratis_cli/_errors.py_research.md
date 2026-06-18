# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_errors.py

## Role

Defines the CLI’s exception hierarchy and human-readable messages for user, runtime, daemon, and environment failures.

## Error Families

- Base: `StratisCliError`.
- Runtime: `StratisCliRuntimeError`.
- User-facing command errors: `StratisCliUserError`.
- Generation/environment/version/action errors.
- Engine and incoherence errors.
- Resource lookup, name conflict, no-change, partial-change, in-use, keyfile, passphrase, invalid option, and in-place-required errors.

## Notable Types

- `StratisCliEngineError` wraps stratisd return code and message.
- `StratisCliActionError` wraps the command line and argparse namespace around an underlying exception.
- `StratisCliPartialChangeError` reports changed and unchanged resource sets.
- `StratisCliInUseOtherTierError` and `StratisCliInUseSameTierError` render device/tier conflicts.
- `StratisCliStratisdVersionError` reports supported daemon version range.

## Dependencies

Imports `BlockDevTiers` and `StratisdErrors` for error messages and return-code interpretation.

## Risk Areas

String output from these exceptions is the basis for `_error_reporting.py` user messages. Changes affect test expectations and CLI UX.

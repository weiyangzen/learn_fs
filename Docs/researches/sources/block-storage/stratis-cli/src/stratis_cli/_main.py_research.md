# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_main.py

## Role

Defines the executable CLI entry function.

## Main Flow

`run()` returns a callable that:

1. Configures `justbytes` display defaults.
2. Builds the argparse parser with `gen_parser()`.
3. Parses command-line arguments.
4. Runs any post-parser verifier.
5. Checks stratisd version unless the selected command is exempt.
6. Executes the selected action function.
7. Wraps action failures in `StratisCliActionError`.
8. Uses `handle_error()` unless `--propagate` is set.

## Dependencies

Uses `justbytes`, parser generation, action error handling, and environment/version error types.

## Notable Risk Areas

This file is the boundary between parsing and action execution. Namespace defaults such as `func`, `post_parser`, and `check_stratisd_version` must be set correctly by parser construction.

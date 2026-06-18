# File Research: sources/block-storage/stratis-cli/src/stratis_cli/__init__.py

## Role

Package initializer for `stratis_cli`. It exposes the public entry points and top-level exception/exit helpers used by the installed CLI wrapper.

## Contents

- Imports `StratisCliEnvironmentError` from `._errors`.
- Imports `StratisCliErrorCodes` and `exit_` from `._exit`.
- Imports `run` from `._main`.

## Dependencies

This file intentionally stays minimal and delegates all real startup behavior to `_main.py`, error types to `_errors.py`, and process exit behavior to `_exit.py`.

## Notable Behavior

Because it imports `run`, other modules can assert that `stratis_cli` has completed enough initialization before generated D-Bus classes are loaded. `_actions/_data.py` depends on this import-order invariant.

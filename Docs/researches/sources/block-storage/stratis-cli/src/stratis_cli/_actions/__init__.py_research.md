# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/__init__.py

## Role

Aggregator module for CLI action classes, D-Bus interface constants, version checking, and error-chain helpers. Parser modules import from here instead of importing each action implementation directly.

## Exported Surface

It re-exports:

- Action classes: `BindActions`, `RebindActions`, `CryptActions`, `TopDebugActions`, `PoolDebugActions`, `FilesystemDebugActions`, `BlockdevDebugActions`, `LogicalActions`, `PhysicalActions`, `PoolActions`, `StratisActions`, `TopActions`.
- Interface constants: `BLOCKDEV_INTERFACE`, `FILESYSTEM_INTERFACE`, `MANAGER_0_INTERFACE`, `POOL_INTERFACE`.
- Utility functions: `check_stratisd_version`, `get_errors`.

## Dependencies

This module ties parser construction to the action layer. Importing it can trigger imports of D-Bus-related modules, so `_actions/_data.py` includes an import-order assertion to avoid eager generation before the package root is initialized.

## Notable Risk Areas

As an aggregator, this file can create circular import pressure. The current design centralizes parser imports, but any new action import added here should be checked against `_data.py`, `_error_reporting.py`, and parser startup.

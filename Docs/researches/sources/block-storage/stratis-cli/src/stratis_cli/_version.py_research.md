# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_version.py

## Purpose

Defines package version information for Stratis CLI.

## Definitions

### `__version_info__`

Tuple version:

```python
(3, 9, 0)
```

### `__version__`

String version generated from `__version_info__`:

```python
".".join(str(x) for x in __version_info__)
```

For the current file contents, this evaluates to:

```python
"3.9.0"
```

## Dependencies

No imports.

## Cross-File Relationships

Other modules can import `__version__` or `__version_info__` for CLI version display, packaging metadata, compatibility checks, or user-facing diagnostics.

The parser move notices in `_parser/_pool.py` mention deprecated pool-level encryption commands being removed in Stratis `3.10.0`, which is one minor release after the version declared here.

## Important Behaviors

- The string version is derived from the tuple, avoiding duplicate literal version strings.
- There is no dynamic package metadata lookup; the version is static source data.

## Research Notes

This is a small metadata module. The main maintenance risk is keeping this static version synchronized with packaging/release metadata elsewhere in the Stratis CLI source tree.

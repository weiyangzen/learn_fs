# File Research: sources/block-storage/mdadm/uuid.c

## Purpose
UUID helper implementation for mdadm metadata and configuration parsing.

## Main Responsibilities
- Defines `uuid_zero`.
- Compares UUIDs with optional 32-bit word byte swapping via `same_uuid()`.
- Copies UUIDs with optional byte swapping via `copy_uuid()`.
- Parses a 128-bit UUID from 32 hex digits while allowing `:`, `.`, space, and `-` separators.

## Integration
Used by metadata backends, sysfs rule parsing, config parsing, and export/detail code.

## Risks and Edge Cases
- Parsing accepts separators anywhere and succeeds only when exactly 32 hex digits are found.
- Swap mode is tailored to legacy host-endian vs on-disk byte-order compatibility.

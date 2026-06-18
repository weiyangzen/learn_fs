# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratis.py

## Role

Implements daemon-information actions.

## Main Behavior

`StratisActions.list_stratisd_version()` gets the top object and prints `Manager0.Properties.Version.Get(proxy)`.

## Dependencies

Uses `get_object(TOP_OBJECT)` and generated manager interface access.

## Notable Behavior

This command is intentionally minimal and uses the lowest manager interface so version discovery can work even when newer CLI/daemon API compatibility is limited.

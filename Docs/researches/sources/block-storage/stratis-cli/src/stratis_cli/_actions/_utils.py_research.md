# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_utils.py

## Role

Shared action-layer utilities for encryption metadata, stopped-pool parsing, passphrase handling, size triples, exception-chain traversal, and long-running D-Bus calls.

## Main Components

- `EncryptionInfo`, `EncryptionInfoClevis`, and `EncryptionInfoKeyDescription` normalize legacy optional/inconsistent encryption data.
- `Device`, `PoolFeature`, and `StoppedPool` parse `StoppedPools` property content.
- `get_pass()` reads passphrases while disabling terminal echo when possible.
- `get_passphrase_fd()` returns a file descriptor from stdin or a keyfile, with optional verification.
- `fetch_stopped_pools_property()` reads `Manager.Properties.StoppedPools`.
- `SizeTriple` computes total/used/free values.
- `get_errors()` walks exception causes.
- `long_running_operation()` treats selected D-Bus `NoReply` failures as initiated long-running operations.

## Error Handling

Raises passphrase mismatch/empty and keyfile-not-found user errors. `STRATIS_STRICT_POOL_FEATURES` controls whether unknown stopped-pool feature strings are tolerated as `UNRECOGNIZED`.

## Notable Risk Areas

Passphrase handling uses raw file descriptors and terminal mode changes. The long-running decorator is intentionally narrow: only configured method names suppress `NoReply`.

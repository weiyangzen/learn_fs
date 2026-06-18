# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_pool.py

## Role

Implements pool listing for active and stopped pools, in both table and detailed formats.

## Main Flow

`list_pools()` selects active or stopped-pool display. Active pools are read from managed objects; stopped pools are read from the manager `StoppedPools` property. A `PoolId` selection triggers detailed output.

## Active Pool Views

- `Default` provides shared active-pool helpers for metadata version, volume key state, alert codes, size triples, UUIDs, and names.
- `DefaultTable` prints compact rows for active pools.
- `DefaultDetail` prints expanded properties, encryption/binding/token-slot information, feature state, allocation, timestamps, and alerts.

## Stopped Pool Views

- `Stopped` formats stopped-pool name and metadata version.
- `StoppedTable` prints stopped-pool summary rows.
- `StoppedDetail` prints stopped-pool details, including devices, encryption info, features, and key/Clevis state.

## Supporting Types

- `TokenSlotInfo` formats token slot plus key or Clevis binding information.
- `DeviceSizeChangedAlerts` computes per-pool size-increase/decrease alert codes.
- `_non_existent_or_inconsistent_to_str()` normalizes optional or inconsistent encryption data.
- `_clevis_to_str()` renders Clevis information.

## Dependencies

Uses pool alert enums, generated managed-object helpers, `StoppedPool`, `EncryptionInfo` variants, `PoolFeature`, `SizeTriple`, `dateutil`, `justbytes`, and table formatting.

## Notable Risk Areas

This is one of the densest presentation modules. It must keep active-pool D-Bus properties, stopped-pool dictionary shapes, metadata versions, and encryption feature combinations in sync with stratisd.

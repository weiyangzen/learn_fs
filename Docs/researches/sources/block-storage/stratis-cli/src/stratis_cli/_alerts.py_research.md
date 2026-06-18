# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_alerts.py

## Role

Defines pool alert code enums, summaries, explanations, and lookup helpers.

## Alert Families

- `PoolMaintenanceAlert`: no IPC state changes, no pool maintenance changes.
- `PoolAllocSpaceAlert`: no allocatable space.
- `PoolDeviceSizeChangeAlert`: device size increased/decreased.
- `PoolEncryptionAlert`: volume key not loaded or status unknown.

## Main Behavior

Each alert enum implements `__str__()`, `explain()`, and `summarize()`. `PoolAlert` builds a `CODE_MAP`, exposes all codes/string codes, and converts a string code back to an alert object.

## Dependencies and Notes

Used by pool listing for alert display and by `PoolActions.explain_code()` to provide detailed explanations.

# File Research: sources/block-storage/stratisd/src/jsonrpc/server/report.rs

## Purpose

Implements the server-side report endpoint.

## Main Types and Behavior

- `report` returns `engine.engine_state_report()` as JSON.

## Integration Points

Called by `StratisParamType::Report` dispatch and returned directly as `StratisRet::Report`.

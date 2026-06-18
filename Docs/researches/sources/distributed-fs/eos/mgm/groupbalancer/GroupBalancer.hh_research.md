# sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.hh

## Purpose
Declares the public and private contract for the per-space group balancing service.

## Important APIs, types, and functions
`GroupBalancer` exposes construction, destruction, `Stop()`, `GroupBalance()`, `Configure()`, `Status()`, `is_valid_engine()`, and `reconfigure()`. `Config` holds enable flags, converter status, transfer limit, min/max file sizes, attempt count, and engine type. `FileInfo` carries selected FID, proc filename, and size with a boolean validity operator.

## Control flow
The class owns an `AssistedThread` that runs `GroupBalance()`. Private helpers split the workflow into file selection, transfer preparation, converter scheduling, cache-expiry checks, and transfer-list cleanup.

## State and persistence
Members track the space name, current configuration, reconfiguration flag, engine mutex and engine pointer, last group-size refresh, scheduled transfers, engine config, and proc-path filter. There is no direct persistence, but scheduled converter jobs produce storage movement.

## Dependencies and integration points
Uses EOS namespace, filesystem view, file IDs, assisted threading, `BalancerEngineTypes`, and `ConverterUtils`. It is instantiated per MGM space and depends on `gOFS` services at runtime.

## Risks and test signals
Defaults are large-file oriented: 1 GiB to 16 GiB and 50 attempts. Tests should validate `Config` defaults, `FileInfo` truthiness, engine-name validation, `reconfigure()` atomic semantics, and lifecycle behavior when `Stop()` is called during waits.

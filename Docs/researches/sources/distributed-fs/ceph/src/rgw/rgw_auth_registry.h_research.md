# sources/distributed-fs/ceph/src/rgw/rgw_auth_registry.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_registry.h` defines `StrategyRegistry`, the aggregate that owns RGW's main authentication strategies and exposes them to request dispatch. The source was read as a complete 97-line header.

## Important APIs, Types, and Functions

`StrategyRegistry` owns `s3_main_strategy`, `s3_post_strategy`, `swift_strategy`, and `sts_strategy`. The nested `s3_main_strategy_t` combines a general S3 AWS strategy that allows anonymous fallback with a Boto2-compatible strategy. Public accessors return references to each strategy, and `create()` returns a `std::unique_ptr<StrategyRegistry>`. Aliases `rgw_auth_registry_t` and `rgw_auth_registry_ptr_t` preserve legacy naming.

## Control Flow

Construction builds all strategies with Ceph context, implicit tenant context, and SAL driver. `s3_main_strategy_t` adds the normal general S3 strategy as `SUFFICIENT`, then adds Boto2 as `FALLBACK`. Callers choose the correct strategy for S3 main requests, S3 browser uploads, Swift, or STS.

## State and Persistence Behavior

The registry owns long-lived strategy objects and their embedded engines for the current RGW configuration. It has no persistence and no mutable runtime state beyond the strategies it contains.

## Dependencies and Integration Points

It depends on core auth interfaces, S3 auth, Swift auth, and STS REST auth. It is the central construction point for request-layer code that needs the current authentication strategy after initialization or realm/config reconfiguration.

## Risks and Edge Cases

Adding a new auth strategy or engine requires exposing it here or it will not participate in request authentication. The S3 main order is security-sensitive: a `SUFFICIENT` normal strategy short-circuits success, while Boto2 only influences fallback failures. Anonymous access is enabled only on the plain main strategy template parameter.

## Test Signals

Tests should assert registry construction, strategy non-emptiness, expected strategy names/orders, S3 fallback behavior, and that Swift/STS accessors return stable references for the registry lifetime.

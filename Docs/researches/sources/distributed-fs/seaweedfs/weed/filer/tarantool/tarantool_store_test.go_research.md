# sources/distributed-fs/seaweedfs/weed/filer/tarantool/tarantool_store_test.go

## Purpose

`tarantool/tarantool_store_test.go` wires the Tarantool store into the shared filer store test suite. It was read as a complete 23-line file.

## Important APIs, Types, and Functions

`TestStore` checks `RUN_TARANTOOL_TESTS`; if enabled, it initializes a `TarantoolStore` at `127.0.1:3303` with user/password `client` and calls `store_test.TestFilerStore`.

## Control Flow

The test skips by default, requiring external Docker/test environment setup. When enabled, it opens a live store and runs shared CRUD/list/KV assertions.

## State and Persistence Behavior

State is in the external Tarantool instance and is not isolated by this file beyond whatever the environment provides.

## Dependencies and Integration Points

Depends on build tag `tarantool`, environment variable gating, and the shared `store_test` suite.

## Risks and Edge Cases

Hardcoded address/credentials and external state can make tests flaky or destructive if not run in the expected Docker setup.

## Test Signals

Provides integration coverage only when explicitly enabled.

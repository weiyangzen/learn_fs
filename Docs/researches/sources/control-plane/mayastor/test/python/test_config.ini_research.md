# sources/control-plane/mayastor/test/python/test_config.ini

## Purpose
pytest-testconfig configuration for Mayastor Python tests.

## Important APIs, Types, And Functions
Defines `[grpc] client_timeout = 120`.

## Control Flow
`pytest_testconfig` loads this value; `MayastorHandle` reads it to set default gRPC call timeouts.

## State And Persistence
No runtime state beyond configuration.

## Dependencies And Integration Points
Used by `common/hdl.py` and all tests that instantiate `MayastorHandle`.

## Risks
A single global timeout may be too high for fast-fail tests or too low for overloaded integration hosts.

## Test Signals
Consistent timeout behavior across gRPC test calls.

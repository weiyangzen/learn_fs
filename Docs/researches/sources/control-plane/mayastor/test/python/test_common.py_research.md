# sources/control-plane/mayastor/test/python/test_common.py

## Purpose
Small smoke tests for the reusable Mayastor Python fixtures and handle methods.

## Important APIs, Types, And Functions
Uses `containers` and `mayastors` fixtures and asserts that container mappings and gRPC handles are available, including pool/bdev list readiness.

## Control Flow
pytest collects simple tests that access fixture-provided dictionaries and perform basic handle operations against compose services.

## State And Persistence
No resources are intentionally persisted; any state is read-only inspection of running Mayastor containers.

## Dependencies And Integration Points
Depends on `common.mayastor` fixtures and the active Docker Compose test environment.

## Risks
These tests mostly validate fixture wiring, so they can pass while deeper control/data path behavior is broken.

## Test Signals
Passing smoke tests show compose service discovery, network IP extraction, and gRPC readiness are functional.

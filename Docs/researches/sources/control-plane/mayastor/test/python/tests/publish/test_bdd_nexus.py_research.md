# sources/control-plane/mayastor/test/python/tests/publish/test_bdd_nexus.py

## Purpose
BDD tests for legacy nexus creation, destruction, listing, child mutation, and publish/unpublish behavior.

## Important APIs, Types, And Functions
Scenarios cover creating a nexus, duplicate create, in-use children, no children, missing children, mixed block sizes, oversized nexus, destroy variants, list, remove/add child, publish/unpublish, republish same/different protocol, and crypto-key publish. Fixtures provide bdevs, shared remote bdev URI, local aio/uring/malloc files, child lists, created nexus cleanup, and `find_nexus`.

## Control Flow
The suite creates base bdevs on local/remote nodes, shares one remote bdev over NVMf, prepares local file-backed child URIs, creates legacy nexuses, executes BDD steps through legacy Mayastor gRPC calls, and asserts list state, child URI sets, device URI presence, or expected gRPC errors.

## State And Persistence
State includes module-scoped bdevs, temporary local files, shared NVMf exports, created nexuses map, and published device URIs. Fixtures destroy bdevs/nexuses and remove files.

## Dependencies And Integration Points
Depends on pytest-bdd, common Mayastor fixtures, `Volume`, `grpc`, legacy `mayastor_pb2`, `nvme_nqn_prefix`, and feature files.

## Risks
Error-code assertions document current behavior, including INTERNAL for no-children and oversized cases. The file uses duplicate function names for some BDD steps, which is legal but can make debugging less clear.

## Test Signals
Passing scenarios provide broad legacy nexus API contract coverage for lifecycle, validation, child management, and publication semantics.

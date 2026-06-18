# sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/test_bdd_nexus.py

## Purpose
BDD compatibility tests proving that v1 nexus gRPC calls can operate on nexuses created through the legacy API.

## Important APIs, Types, And Functions
Scenario functions cover duplicate create, destroy, list/filter, child remove/add, publish/unpublish, republish protocol checks, and crypto-key publish. Fixtures build base malloc bdevs, shared remote bdev URIs, local aio/uring/malloc child URIs, v0 and v1 nexus creators, and `find_nexus`.

## Control Flow
Fixtures create local and remote bdevs, share a remote bdev over NVMf, assemble children, create v0 nexuses via `mayastor_pb2`, then perform v1 operations through `nexus_pb2`. Step assertions inspect legacy `ListNexus` results to confirm cross-version effects.

## State And Persistence
State includes module-scoped base bdevs, temporary local files under `/tmp`, a `created_nexuses` cleanup map, and published device URIs. Teardown destroys bdevs and nexuses.

## Dependencies And Integration Points
Depends on `pytest_bdd`, legacy `mayastor_pb2`, v1 `nexus_pb2`/`common_pb2`, common and v1 Mayastor fixtures, gRPC status codes, and feature files.

## Risks
Some steps intentionally expect current legacy/v1 mismatches, such as duplicate v1 create returning INTERNAL. Duplicate Python function names for publish steps can obscure reporting, though decorators still bind at import time.

## Test Signals
Passing scenarios signal v1 API compatibility for legacy nexus identity, children, publication state, error mapping, and list filters.

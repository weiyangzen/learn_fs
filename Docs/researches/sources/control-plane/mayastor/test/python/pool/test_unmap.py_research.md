# sources/control-plane/mayastor/test/python/pool/test_unmap.py

## Purpose
Tests pool behavior around unmap/discard support.

## Important APIs, Types, And Functions
Uses Mayastor fixtures and command helpers to create backing storage, create a pool, likely issue discard/unmap-relevant IO, and compare used-space accounting.

## Control Flow
The test creates a pool on the single compose Mayastor instance, creates/writes/removes data, and checks pool usage changes to ensure unmap/discard releases space as expected.

## State And Persistence
State is the test pool, backing file/device, and pool usage counters. Cleanup destroys the pool and removes temporary artifacts.

## Dependencies And Integration Points
Depends on the `pool/docker-compose.yml` privileged container, common Mayastor fixtures, local shell tools, and io-engine pool accounting.

## Risks
Discard semantics depend on backing device support and filesystem/kernel behavior. Space accounting can be asynchronous or rounded by pool cluster size.

## Test Signals
Observed pool used-space decrease after discard/unmap is the main behavioral signal.

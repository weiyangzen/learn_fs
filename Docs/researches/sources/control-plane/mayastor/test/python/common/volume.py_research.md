# sources/control-plane/mayastor/test/python/common/volume.py

## Purpose
Convenience abstraction for creating a replicated Mayastor volume from pool URIs and a target nexus node.

## Important APIs, Types, And Functions
Class `Volume` stores `uuid`, `nexus`, `pools`, and `size`. Internal helpers `__parse_uri` and `__create_replicas` parse `pool://host/pool` URIs and create replicas. `create()` creates replicas, creates a nexus, publishes it, and returns its device URI.

## Control Flow
`create()` validates an `nvmt://host` nexus target, creates a replica on each configured pool via a fresh `MayastorHandle`, then creates and publishes a nexus on the target.

## State And Persistence
State is remote Mayastor pools, replicas, nexus, and NVMf publication. The object has no cleanup method, so callers own teardown.

## Dependencies And Integration Points
Depends on `MayastorHandle` and Python URL parsing. Used by nexus tests to model volume creation and ENOSPC behavior.

## Risks
Lack of cleanup and fresh handle creation per pool can leave resources behind on failure. It assumes `pool` and `nvmt` URI schemes and does not support v2 naming fields.

## Test Signals
Successful `Volume.create()` proves pool URI discovery, replica creation, nexus creation, and publish flow work end to end.

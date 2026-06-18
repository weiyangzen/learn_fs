# sources/control-plane/mayastor/test/grpc/test_nexus.js

## Purpose
Legacy Mocha/Chai coverage for the Mayastor nexus gRPC API. It validates nexus creation, listing, child add/remove, publish/unpublish, NVMf datapath behavior, ANA state changes, controller ID handling, and destructive/error cases across `bdev`, `aio`, `nvmf`, and conditionally `uring` children.

## Important APIs, Types, And Functions
Key helpers are `controlPlaneTest`, `doUring`, promise wrappers for `publish`, `unpublish`, `createNexus`, `createNexusV2`, `destroyNexus`, and `createNexusWithAllTypes`. It drives `client.createNexus`, `listNexus`, `addChildNexus`, `removeChildNexus`, `publishNexus`, `unpublishNexus`, `setNvmeAnaState`, and `getNvmeAnaState`, plus JSON-RPC calls such as `nexus_share` and `nvmf_subsystem_remove_ns`.

## Control Flow
The suite starts a separate NVMf target Mayastor and a primary Mayastor instance, creates malloc/aio/uring backing devices, then runs ordered tests that build a nexus, mutate children, publish over NVMf, inspect NVMe identify data, and finally exercise cleanup and invalid-argument paths. NBD tests exist but are skipped.

## State And Persistence
State lives in temporary files under `/tmp`, in two Mayastor processes, in exported NVMf namespaces, and in the single global gRPC client. Cleanup stops all Mayastor processes, restores NBD permissions, and removes temporary files.

## Dependencies And Integration Points
Depends on `test_common`, `grpc_enums`, Node `grpc`, SPDK JSON-RPC, the `initiator` helper, `nvme` CLI, root permissions, hugepages, and loop/device access. It integrates directly with Mayastor's legacy protobuf service and NVMf subsystem implementation.

## Risks
The source contains legacy fragility: skipped NBD coverage, duplicated lines in promise/NBD blocks, asynchronous `doUring` detection that can return before `exec` completes, and heavy reliance on timing, root commands, and local networking. Error-code assertions encode current implementation quirks such as oversized nexus creation returning INTERNAL.

## Test Signals
Passing tests signal that nexus child URI validation, NVMf publication, ANA reporting, controller ID assignment, namespace loss faulting, and idempotent create/destroy behavior work through the legacy gRPC surface.

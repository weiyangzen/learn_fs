<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_test.go -->
# sources/cloud-native/cri-o/server/container_create_test.go

## Purpose

This Ginkgo suite tests high-level `CreateContainer` validation and early error behavior.

## Important APIs, Types, and Functions

The tests use `sut.CreateContainer`, helper constructors for CRI container and sandbox configs, `addContainerAndSandbox`, and sandbox state mutation.

## Control Flow

Cases call `CreateContainer` with missing image, missing metadata, nil config, stopped sandbox, empty checkpoint archive, missing sandbox, invalid sandbox ID, and empty sandbox ID. They assert that responses are nil and errors occur where expected.

## State and Persistence Behavior

The suite sets up and tears down a mock server environment. The empty checkpoint archive test creates and removes a local `empty.tar`, triggering the checkpoint-detection branch when checkpoint restore is enabled by server configuration.

## Dependencies and Integration Points

It depends on the shared server test harness, CRI protobuf types, and the sandbox/container setup helpers.

## Risks and Edge Cases

This suite does not validate successful creation or deep cleanup behavior. It mostly guards request validation and sandbox lookup semantics, leaving storage/runtime/NRI/hook behavior to other integration tests.

## Test Signals

The tests confirm that bad input is rejected before expensive runtime work and that invalid checkpoint archives surface errors through the create path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_test.go -->

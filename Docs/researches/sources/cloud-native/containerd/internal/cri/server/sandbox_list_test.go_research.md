# sources/cloud-native/containerd/internal/cri/server/sandbox_list_test.go

## Purpose

This test file validates CRI sandbox conversion and filtering behavior.

## Important APIs, Types, and Functions

`TestToCRISandbox` checks metadata, labels, annotations, runtime handler, created time, and state mapping. `TestFilterSandboxes` populates a test sandbox store and verifies no filter, full ID, truncated ID, state, label, and mixed filter cases.

## Control Flow

Tests build sandbox store objects, convert them to CRI objects, insert them into the service store for ID normalization, and compare filtered slices.

## State and Persistence Behavior

Only the in-memory test sandbox store is mutated.

## Dependencies and Integration Points

It exercises `toCRISandbox`, `filterCRISandboxes`, and store-based truncated ID normalization.

## Risks and Test Signals

The tests catch user-visible list filtering regressions. They do not test concurrent store mutation or stats filter normalization separately.

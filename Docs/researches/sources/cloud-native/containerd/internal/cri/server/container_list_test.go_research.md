# sources/cloud-native/containerd/internal/cri/server/container_list_test.go

## Purpose
This test file validates container list conversion and filter semantics for the CRI server.

## Important APIs, Types, and Functions
Tests include `TestToCRIContainer`, `TestFilterContainers`, and `TestListContainers`. `containerForTest` helps create store entries with fake status.

## Control Flow, State, and Persistence
The tests populate fake sandbox and container stores, invoke either direct conversion/filter helpers or `ListContainers`, and assert returned CRI containers. In-memory store state models created, running, and exited containers through timestamp fields.

## Dependencies and Integration Points
It covers container store, sandbox store, short ID normalization, CRI states, labels, metadata, and the choice to set `ImageId` equal to stored `ImageRef` in list responses.

## Risks and Test Signals
Signals are exact output containers for no filter, ID, sandbox ID, state, label, and mixed filters. Risks include tests depending on list ordering and incomplete coverage for ambiguous short IDs or image-store lookups, which `ListContainers` intentionally avoids.

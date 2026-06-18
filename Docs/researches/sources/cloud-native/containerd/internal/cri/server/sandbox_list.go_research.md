# sources/cloud-native/containerd/internal/cri/server/sandbox_list.go

## Purpose

This file implements CRI pod sandbox listing and filtering from the in-memory sandbox store.

## Important APIs, Types, and Functions

`ListPodSandbox` converts all stored sandboxes to CRI `PodSandbox` objects and applies filters. `toCRISandbox` maps metadata/status to CRI state and fields. `normalizePodSandboxFilter` and `normalizePodSandboxStatsFilter` expand truncated IDs through the store. `filterCRISandboxes` applies ID, state, and label selectors.

## Control Flow

Listing does not query containerd. It snapshots the current store, maps ready state to `SANDBOX_READY` and all other states to `SANDBOX_NOTREADY`, normalizes IDs, and filters sequentially.

## State and Persistence Behavior

No state is mutated except the request filter ID may be normalized in place.

## Dependencies and Integration Points

It integrates with CRI runtime API, sandbox store, metrics timers, and stats filtering helpers.

## Risks and Test Signals

Risks include in-place filter mutation and not distinguishing unknown from not-ready in CRI output. Tests cover conversion, truncated IDs, state filters, label filters, and mixed filters.

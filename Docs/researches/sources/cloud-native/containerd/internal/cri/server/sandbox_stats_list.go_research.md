# sources/cloud-native/containerd/internal/cri/server/sandbox_stats_list.go

## Purpose

This file implements CRI `ListPodSandboxStats` with filtering and concurrent per-sandbox stats collection.

## Important APIs, Types, and Functions

`ListPodSandboxStats` selects sandboxes, starts one goroutine per sandbox, calls `podSandboxStats`, suppresses transient unavailable/not-found/closed errors, joins hard errors, and returns collected stats. `sandboxesForListPodSandboxStatsRequest` applies ID, label, and ready-state filtering.

## Control Flow

Filtering happens before concurrency. Each goroutine writes to its own index in `stats` and `errs`, then the response compacts non-nil stats after the wait group completes.

## State and Persistence Behavior

No state is mutated except in-place normalization of the filter ID through shared list helpers.

## Dependencies and Integration Points

It integrates with sandbox store filtering, platform stats collection, `ttrpc.ErrClosed`, errdefs, and CRI stats list API.

## Risks and Test Signals

Risks include high goroutine fan-out on many sandboxes and suppressed transient errors hiding recurring stats issues. Tests should cover filtering and joined error behavior.

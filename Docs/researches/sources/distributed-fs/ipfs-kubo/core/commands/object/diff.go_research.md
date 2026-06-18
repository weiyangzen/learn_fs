# sources/distributed-fs/ipfs-kubo/core/commands/object/diff.go

## Purpose

`object/diff.go` implements deprecated `ipfs object diff`, comparing two legacy dag-pb/IPFS objects and printing link-level changes. It remains for compatibility while directing users toward newer DAG/files APIs.

## Important APIs, Types, and Functions

`ObjectDiffCmd` emits `Changes`, a wrapper around `dagutils.Change` pointers. It accepts `obj_a`, `obj_b`, and `--verbose`. It uses `api.Object().Diff`, `cmdutils.PathOrCidPath`, Boxo `dagutils`, Boxo `path`, and request-specific CID encoding.

## Control Flow

The command obtains CoreAPI, parses both arguments as paths or CID paths, calls `api.Object().Diff`, and maps CoreAPI changes into `dagutils.Change` values. `Before` and `After` CIDs are populated only when the corresponding immutable path is non-zero. The text encoder chooses verbose prose or compact symbols: `+` for additions, `~` for modifications, and `-` for removals.

## State and Persistence Behavior

The command is read-only. It may resolve or fetch blocks through CoreAPI, but it does not mutate the DAG, blockstore, or repo.

## Dependencies and Integration Points

It integrates with the deprecated `ObjectCmd` tree and legacy dag-pb object APIs in CoreAPI. The command uses the global CID encoder so output honors request encoding options.

## Risks and Test Signals

Risks include deprecated API drift, path resolution errors, empty immutable-path detection, and output compatibility for scripts still consuming `object diff`. Tests should cover add/modify/remove changes, verbose and compact encoders, CID base selection, invalid paths, missing blocks, no-change output, and deprecation status visibility.

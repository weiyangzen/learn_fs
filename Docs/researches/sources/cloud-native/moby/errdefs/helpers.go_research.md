# sources/cloud-native/moby/errdefs/helpers.go

## Purpose
Factory helpers that wrap arbitrary errors with Moby/containerd-compatible error classes.

## Important APIs and Types
Defines wrapper structs and constructors: `NotFound`, `InvalidParameter`, `Conflict`, `Unauthorized`, `Unavailable`, `Forbidden`, `System`, `NotModified`, `NotImplemented`, `Unknown`, `Cancelled`, `Deadline`, `DataLoss`, plus `FromContext`.

## Control Flow, State, and Persistence
Each wrapper embeds an error, implements the marker method, and exposes both `Cause` and `Unwrap`. Constructors return nil unchanged and return already-classified containerd errors unchanged; otherwise they wrap. `FromContext` maps `context.Canceled` to `Cancelled`, `context.DeadlineExceeded` to `Deadline`, and other context errors to `Unknown`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `github.com/containerd/errdefs` predicates for compatibility. API handlers and storage/daemon subsystems use these helpers to preserve status semantics across wrapping. Risks include mapping a class to the wrong containerd predicate, double-wrapping custom classes, and exposing unclassified errors that become generic 500s. `helpers_test.go` checks each class, unwrap identity, `errors.Is`, and recognition through additional wrapping.

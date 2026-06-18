# sources/cloud-native/moby/errdefs/doc.go

## Purpose
Package documentation for Moby error definitions.

## Important APIs and Types
Declares package `errdefs` and documents that packages should communicate error classes by implementing one marker interface, preferably checked through helper functions.

## Control Flow, State, and Persistence
No runtime behavior or state.

## Dependencies, Integration Points, Risks, and Test Signals
The documentation frames how `defs.go` and `helpers.go` should be used across daemon, API, and client boundaries. The key risk is misuse: direct type assertions without following unwrap chains or errors that implement more than one class. Compile and documentation generation are sufficient direct signals.

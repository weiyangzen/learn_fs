# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/DelegatingJournaled.java

## Purpose
`DelegatingJournaled` is a mixin for classes that expose `Journaled` behavior through another component.

## Important APIs, Types, And Functions
Default methods forward journal processing, reset, apply-and-journal, checkpoint naming, checkpoint write/restore, and journal-entry iteration to `getDelegate`.

## Control Flow, State, Dependencies, Risks, And Tests
The delegate owns all state and persistence. This interface removes boilerplate for wrappers but makes correctness depend on stable delegation. Dependencies include `Journaled`, checkpoint classes, `CloseableIterator`, and async checkpoint APIs. Risks include `getDelegate` returning null, changing delegates mid-operation, or losing wrapper-specific state from checkpoints. Tests should verify each default forwards exactly once and that wrappers document whether delegate identity is stable.

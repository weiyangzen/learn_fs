<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.c -->
# sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.c

## Purpose
Implements `OstreeChainInputStream`, a `GInputStream` that presents a sequence of child input streams as one contiguous stream.

## Important APIs and Types
Private state stores a referenced `GPtrArray *streams` and current `index`. `ostree_chain_input_stream_new()` constructs the stream with construct-only pointer property `streams`. The class overrides `read_fn` and `close_fn`.

## Control Flow
Read checks cancellation, returns EOF if all children are consumed, otherwise reads from the current child. If a child returns EOF, it advances to the next child and retries until data or total EOF. Close iterates all children and closes each, stopping on the first close error.

## State and Persistence
State is transient read position across child streams. It does not persist data; it composes existing streams.

## Dependencies and Integration Points
Depends on GLib/GIO. `ostree-core.c` uses it to combine length-prefixed file metadata headers with optional content streams for OSTree object serialization.

## Risks
The constructor stores a referenced `GPtrArray`, but child stream ownership depends on the array's free function. Close stops at first failure, potentially leaving later children open. Zero-byte reads from unusual child streams are treated as EOF.

## Test Signals
Tests should cover multiple streams, empty child streams, cancellation, close propagation, read boundaries across children, and ownership/ref behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.c -->

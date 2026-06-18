<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.h -->
# sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.h

## Purpose
Declares the chain input stream type, hidden from GI scanner.

## Important APIs and Types
Defines GObject type/cast/check macros, `OstreeChainInputStream`, class struct with reserved padding, type getter, and `ostree_chain_input_stream_new(GPtrArray *streams)`.

## Control Flow
No runtime flow in the header.

## State and Persistence
Implementation-private state tracks stream array and current index.

## Dependencies and Integration Points
Includes `<ostree.h>` and is used by core object stream construction.

## Risks
The `streams` constructor argument is a raw `GPtrArray*`; callers must supply an array whose child lifetime semantics are correct.

## Test Signals
Compile/type checks and implementation behavior tests validate the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.h -->

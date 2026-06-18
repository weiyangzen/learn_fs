<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-private.h

## Purpose
Aggregates the private blob reader implementations into one internal include.

## Important APIs and Types
It includes `ostree-blob-reader-base64.h`, `ostree-blob-reader-pem.h`, and `ostree-blob-reader-raw.h`, making the concrete constructors and read functions available to internal libostree code.

## Control Flow
No runtime logic is present.

## State and Persistence
No state is stored.

## Dependencies and Integration Points
This is an integration header for modules that need access to all blob reader variants without including each concrete header manually.

## Risks
Because it exposes concrete internal readers together, adding a new reader here can widen internal compile dependencies. It should remain private to avoid making internal constructors a stable external contract.

## Test Signals
Compile coverage of internal users is sufficient; missing includes would surface as unknown type or prototype failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-private.h -->

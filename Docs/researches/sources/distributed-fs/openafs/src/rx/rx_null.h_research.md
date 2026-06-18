# Research: sources/distributed-fs/openafs/src/rx/rx_null.h

## sources/distributed-fs/openafs/src/rx/rx_null.h

### Purpose
`rx_null.h` is a legacy placeholder header whose comment says "Remove this file".

### Important APIs
No declarations or definitions are present in the file.

### Control Flow, State, and Dependencies
There is no runtime behavior and no state. It is included by `rx.h`, likely for historical compatibility with code expecting an RX null header.

### Risks and Edge Cases
Removing it without checking includes would break builds that include `rx_null.h` directly or transitively. Its lack of prototypes means users rely on `rx_prototypes.h` or other headers for null security declarations.

### Test Signals
Build tests should detect whether any consumers still include this header directly. A cleanup would require include-graph validation.

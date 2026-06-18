# Research: sources/distributed-fs/openafs/src/rx/rx_multi.h

## sources/distributed-fs/openafs/src/rx/rx_multi.h

### Purpose
`rx_multi.h` defines `struct multi_handle` and macros that turn the support functions in `rx_multi.c` into a structured multi-RX calling pattern.

### Important APIs and Macros
- `struct multi_handle` stores call array, ready index array, counters, ready pointers, and optional lock/cv.
- `multi_Rx(conns, nConns)` opens the multi-call block and initializes a handle.
- `multi_Body(startProc, endProc)` starts unstarted calls, flushes writes, selects ready calls, and ends calls.
- `multi_Abort` breaks from the loop.
- `multi_End` finalizes the handle.

### Control Flow
The macros implement a loop over not-yet-started calls and ready calls. They expose `multi_i`, `multi_i0`, `multi_error`, `multi_call`, and `multi_h` to the macro body. This lets rxgen-generated code run call-specific start/end procedures while sharing the same orchestration logic.

### Dependencies and Integration Points
Used with `multi_Init`, `multi_Select`, and `multi_Finalize`. It depends on caller discipline and RX call APIs. Comments document integration constraints for lock ordering and connection reuse.

### Risks and Edge Cases
- Macros introduce scoped variables with fixed names and are sensitive to body structure.
- `multi_Abort` is a simple `break`, so it only exits the macro loop.
- Heavy work inside the macro body can hold channels open longer than expected.
- Same-connection concurrent multi calls can deadlock without stable ordering.

### Test Signals
Generated-code tests should exercise macro expansion paths, early abort, all-error/all-success cases, and nested surrounding control flow.

# sources/distributed-fs/coda/coda-src/venus/venuscb.h

## Purpose
This header declares the Venus callback server vproc class and callback subsystem initialization globals.

## Important APIs, Types, and Functions
It defines `DFLT_MAXCBSERVERS` and `UNSET_MAXCBSERVERS`, declares `callbackserver : public vproc` with RPC2 request filter, handle, and packet fields, and exposes `MaxCBServers`, `cbbreaks`, and `CallBackInit()`.

## Control Flow
`CallBackInit()` is the external entry point. The private constructor starts callback server threads, and `main()` is overridden to service callback RPCs.

## State and Persistence Behavior
Declared state is transient callback server configuration and callback-break count. Persistent cache correctness is affected indirectly through callback breaks implemented in the `.cc` file.

## Dependencies and Integration Points
It depends on RPC2 and `vproc.h`. It is included by Venus startup and callback implementation code.

## Risks and Test Signals
Risks are configuration bounds and lifetime of packet buffers/handles. Build tests should verify generated callback stubs can link against the implementation and that configured `MaxCBServers` creates the expected number of vprocs.

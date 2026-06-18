# sources/distributed-fs/coda/coda-src/vcodacon/util.h

## Purpose
This header exposes the `vcodacon` utility callbacks implemented in `util.cc` to the GUI code.

## Important APIs, Types, and Functions
It declares the shared `XferLabel[3]` array plus `MainInit`, `do_clog`, `do_cunlog`, `menu_clog`, `menu_ctokens`, `menu_cunlog`, and `do_findRealm`.

## Control Flow
There is no executable flow in the header. It defines the callback and helper surface the GUI can bind to menu actions and startup initialization.

## State and Persistence Behavior
Only the external transfer-label pointer array is declared here. Authentication and token changes happen indirectly through the implementation.

## Dependencies and Integration Points
The header is included by the FLTK GUI source and any code that needs realm probing or Coda authentication menu callbacks.

## Risks and Test Signals
The main risks are untyped global callback coupling and no include guard. Compile tests should verify this header can be included in the generated GUI translation unit, and GUI smoke tests should invoke each declared callback.

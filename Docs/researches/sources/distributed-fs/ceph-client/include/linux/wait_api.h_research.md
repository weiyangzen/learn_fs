# sources/distributed-fs/ceph-client/include/linux/wait_api.h

## Purpose
`wait_api.h` is a compatibility/convenience include shim. Its entire content is `#include <linux/wait.h>`, so it exposes the full waitqueue API under an alternate header name.

## Important APIs, Types, and Functions
This file declares no independent types, functions, or macros. Consumers including `linux/wait_api.h` receive `struct wait_queue_head`, `struct wait_queue_entry`, wakeup macros, wait-event macros, and low-level wait helpers from `wait.h`.

## Control Flow
There is no runtime control flow in this header. Compile-time inclusion redirects the user to `wait.h`.

## State and Persistence
The file owns no state and has no persistence behavior. All waitqueue state semantics are inherited from `wait.h` and implementation files.

## Dependencies and Integration Points
Its only dependency and integration point is `linux/wait.h`. The header exists to support source code that wants an API-facing wait include without naming the implementation-heavy header directly.

## Risks
The main risk is assuming this file is a smaller or separate API subset; it is not. Include-order behavior is exactly that of `wait.h`. Changes to `wait.h` transitively affect all `wait_api.h` consumers.

## Test Signals
Compile tests are sufficient: any file including `linux/wait_api.h` should see the same waitqueue declarations as direct `linux/wait.h` inclusion. Include-what-you-use or dependency scanners should treat it as a forwarding header.

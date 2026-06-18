# sources/distributed-fs/ceph-client/include/linux/mm_api.h

## Purpose
This file is a one-line compatibility or API shim that includes `linux/mm.h`. It gives code a stable `mm_api.h` include name while re-exporting the full MM interface from `mm.h`.

## Important APIs, Types, And Data
The file declares no independent API, type, macro, or state. Its only content is `#include <linux/mm.h>`, so all visible symbols come from `mm.h` and its transitive includes.

## Control Flow
There is no runtime control flow. During preprocessing, including `mm_api.h` is equivalent to including `linux/mm.h`.

## State And Persistence
No state is introduced or persisted by this header.

## Dependencies And Integration Points
Its sole dependency is `linux/mm.h`. It integrates with any code that wants to depend on an MM API facade instead of including the main MM header directly.

## Risks
Because it re-exports a very large header, compile-time dependencies and rebuild scope remain as broad as direct `mm.h` inclusion. Any future attempt to narrow the API must consider all existing users that rely on transitive `mm.h` declarations.

## Test Signals
Compile any translation unit that includes `linux/mm_api.h` without separately including `linux/mm.h`. Include-what-you-use or dependency scans can identify whether the shim is serving as a stable facade or merely duplicating direct includes.

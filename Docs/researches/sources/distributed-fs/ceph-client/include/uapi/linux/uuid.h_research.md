# sources/distributed-fs/ceph-client/include/uapi/linux/uuid.h

## Purpose
Compatibility forwarding header for UUID definitions. It delegates to `<linux/mei_uuid.h>`.

## Important APIs, Types, And Constants
This file declares no local symbols. Its API surface is whatever `linux/mei_uuid.h` exports to consumers that historically include `linux/uuid.h` from this source tree.

## Control Flow, State, And Persistence
There is no control flow or state. Inclusion simply redirects compile-time type and macro availability.

## Dependencies And Integration Points
The direct dependency is `linux/mei_uuid.h`, so build success depends on that header remaining present and suitable for UAPI inclusion. Consumers relying on this include path are integrated through the preprocessor rather than runtime code.

## Risks And Test Signals
Risk is mostly header drift: if `mei_uuid.h` changes scope or disappears, `linux/uuid.h` consumers fail. Test signals are compile-only checks for representative userspace includes and ABI checks for UUID type names supplied by the included header.

# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.h

## Purpose
This header declares the optional CRW injection interface used by the CRW retrieval path when CIO injection support is enabled.

## Important APIs, Types, and Functions
Under `CONFIG_CIO_INJECT`, it includes `asm/crw.h`, declares static key `cio_inject_enabled`, and declares `stcrw_get_injected(struct crw *crw)`.

## Control Flow
The header has no runtime flow. Compile-time configuration controls whether the declarations are visible to callers.

## State and Persistence
It declares volatile test state only; no persistent storage is involved.

## Dependencies and Integration Points
It integrates `cio_inject.c` with CRW collection code and depends on the architecture CRW type. Callers must guard uses with `CONFIG_CIO_INJECT` or include this header under matching configuration.

## Risks and Test Signals
Risk areas include configuration mismatches and missing stubs for disabled builds if callers are not conditionalized. Test signals are builds with and without `CONFIG_CIO_INJECT` and runtime CRW injection through debugfs when enabled.

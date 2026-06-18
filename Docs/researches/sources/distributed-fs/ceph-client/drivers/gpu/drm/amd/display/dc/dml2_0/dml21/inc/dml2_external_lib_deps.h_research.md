# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml2_external_lib_deps.h

## Purpose
`dml2_external_lib_deps.h` is a minimal dependency bridge for DML2.1 external-library builds. It currently just includes `os_types.h` behind an include guard.

## Important APIs, types, and functions
The file declares no APIs or types of its own. Its effective export is the OS type definitions made available through `os_types.h`.

## Control flow
There is no control flow.

## State and persistence behavior
No runtime or persistent state is defined.

## Dependencies and integration points
It integrates DML2.1 headers with the surrounding AMD DC OS abstraction layer. Include order can use this header where external DML code needs basic bool/integer/platform types without pulling larger driver headers.

## Risks and edge cases
The risk is low, but if external-library builds require additional platform shims, this thin header is where missing type dependencies may surface. Over-expanding it would increase coupling.

## Test signals
Standalone DML2.1 build coverage and kernel build coverage with this include path are sufficient signals.

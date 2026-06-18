# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/printf.h

## Purpose
Defines NVIF object-scoped debug/error logging macros.

## Important APIs, Types, And Functions
Exports `NVIF_PRINT`, `NVIF_DEBUG`, `NVIF_ERROR`, and `NVIF_ERRON`. Messages include client name, object handle, and object name.

## Control Flow
Macros fetch the object's parent and call the selected logging callback. `NVIF_ERRON` logs error on nonzero condition or debug on success.

## State And Persistence
No state is stored; it reads object/client/parent state at logging time.

## Dependencies And Integration Points
Depends on `nvif/client.h` and `nvif/parent.h`; used by NVIF object, push, and driver code.

## Risks
Requires valid object, client, and parent pointers. Format strings must match arguments; debug can be compiled out through `NVIF_DEBUG_PRINT_DISABLE`.

## Test Signals
Expected log prefixes, error-path logs, and build format checking validate behavior.

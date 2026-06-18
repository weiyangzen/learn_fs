# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/unpack.h

## Purpose
Provides macros for versioned NVIF payload unpacking.

## Important APIs, Types, And Functions
Defines `nvif_unvers` for empty-version handling and `nvif_unpack` for checking size/version range, advancing data pointers, shrinking remaining size, and enforcing trailing-data rules.

## Control Flow
Macros operate only when the current return code is `-ENOSYS`. On successful match they consume a structure and optionally reject unexpected trailing bytes.

## State And Persistence
No persistent state. They mutate local `void **data`, `u32 *size`, and return-code variables.

## Dependencies And Integration Points
Used by NVKM method/object handlers that decode versioned NVIF ABI payloads.

## Risks
Macro side effects and assignment inside conditionals require careful use. Wrong version bounds can accept incompatible payloads.

## Test Signals
ABI decode tests, invalid-size/version negative tests, and object method validation logs are key signals.

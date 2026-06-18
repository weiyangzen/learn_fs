# sources/distributed-fs/openafs/src/volser/volser_prototypes.h

## Purpose

`volser_prototypes.h` is a smaller public prototype header for selected vos/Volser utility functions. It declares commonly used `UV_*` client functions, partition and host mapping helpers, and security binding helpers.

## Important APIs

Declared functions include `MapPartIdIntoName`, `MapHostToNetwork`, `UV_Bind`, `UV_SetSecurity`, `UV_CreateVolume`, `UV_DeleteVolume`, `UV_ListOneVolume`, and `UV_RestoreVolume`. Forward declarations for `struct nvldbentry` and `struct volintInfo` avoid pulling in heavier headers for users that only need these prototypes.

## Control Flow Role

This header does not implement logic. It allows client and utility code to call a compact subset of `vsprocs.c` functionality. Compared with `volser_internal.h`, it presents fewer declarations and appears oriented toward broader users that do not need the full internal orchestration surface.

## State and Persistence Behavior

The header is stateless. The declared `UV_*` functions can create, delete, list, and restore volumes, causing persistent volserver changes and possible VLDB coordination depending on implementation. `UV_SetSecurity` changes process-level client security state for later calls.

## Dependencies and Integration Points

The declarations depend on Rx types, VLDB entry types, Volser wire types, and OpenAFS integer types supplied by including translation units. It integrates utility code with the Volser RPC client layer.

## Risks and Edge Cases

Risks include divergence from `volser_internal.h` and `vsprocs.c`, exact callback signature requirements for restore writers, and undocumented ownership/allocation behavior for returned `volintInfo **`.

## Test Signals

Compile tests for utilities including this header, plus runtime vos tests for bind/security setup, create/delete, list-one-volume, and restore, provide the main validation signals.

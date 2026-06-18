# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/disp.c

## Purpose
This file constructs and destroys NVIF display objects across supported display class generations.

## Important APIs, Types, and Functions
Public functions are `nvif_disp_ctor` and `nvif_disp_dtor`.

## Control Flow
Constructor selects a supported display class from newest to oldest using `nvif_sclass`, creates the display object, then stores connector, output, and head masks returned by the backend. Destructor destroys the object.

## State and Persistence Behavior
State includes the display NVIF object and enumeration masks for connectors, outputs, and heads.

## Dependencies and Integration Points
It depends on NVIF device/object APIs, display class IDs, display ABI structures, and later connector/output/head constructors.

## Risks
Unsupported requested class returns an error before object construction. Mask interpretation must match subsequent enumeration code.

## Test Signals
Signals include display class selection on multiple GPU generations, mask correctness, object destruction, and failure for unsupported classes.

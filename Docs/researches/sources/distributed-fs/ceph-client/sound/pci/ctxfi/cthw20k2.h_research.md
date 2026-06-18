# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.h

## Purpose

This header exposes the 20k2 hardware-object lifecycle to the rest of the ctxfi driver.

## Important APIs, types, and functions

It includes `cthardware.h` and declares `create_20k2_hw_obj(struct hw **rhw)` plus `destroy_20k2_hw_obj(struct hw *hw)`. The implementation returns a heap-allocated `struct hw20k2` through its embedded `struct hw`.

## Control flow

ATC setup includes this header when selecting a hardware backend. Creation allocates and initializes a vtable preset; destruction shuts down the card if still mapped and frees the object.

## State and persistence behavior

The header owns no state. It defines the constructor boundary for the persistent `struct hw` state implemented in `cthw20k2.c`.

## Dependencies and integration points

It is coupled to `cthardware.h` and the ATC hardware selection path. Its small API hides 20k2-specific fields from generic ctxfi modules.

## Risks and test signals

The main risk is lifecycle mismatch: callers must destroy only objects created by this backend. Build coverage of 20k2 support and probe/remove tests catch signature or ownership regressions.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.h

## Purpose

`hw_factory_dce110.h` declares the DCE11.0 GPIO hardware factory initializer.

## Important APIs, Types, And Functions

The only API is `dal_hw_factory_dce110_init(struct hw_factory *factory)`.

## Control Flow

The header has no runtime logic. Consumers include it to call the initializer during GPIO service/resource setup for DCE11-class hardware.

## State, Dependencies, Risks, And Test Signals

It defines no state. The implementation initializes caller-owned `struct hw_factory` data. The declaration depends on `struct hw_factory` being visible to the including translation unit and connects generation-specific setup to shared GPIO factory code. Risks are limited to include-order or signature drift. Build coverage catches these; runtime GPIO factory tests should verify the implementation-populated function table.

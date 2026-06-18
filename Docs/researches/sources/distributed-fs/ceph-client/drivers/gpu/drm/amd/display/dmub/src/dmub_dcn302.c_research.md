# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c

## Purpose

`dmub_dcn302.c` provides the DCN 3.0.2 DMUB register table, using Dimgrey Cavefish IP offsets with DCN 3.0 generated register definitions. It has no unique runtime functions in this file.

## Important APIs, Types, And Functions

The exported object is `dmub_srv_dcn302_regs`, a `struct dmub_srv_common_regs` containing offsets, masks, and shifts for the common DMUB register/field set.

## Control Flow And Data Flow

The file constructs the table at compile time using `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`. Runtime control flow is delegated to common DMUB hardware functions that consume `dmub->regs`.

## State And Persistence Behavior

It defines immutable metadata and no runtime state.

## Dependencies And Integration Points

Dependencies are `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn302.h`, `dimgrey_cavefish_ip_offset.h`, and DCN 3.0 generated offset/mask headers. Integration is through generation-specific ASIC setup.

## Risks And Edge Cases

DCN302 uses DCN 3.0 register headers rather than a distinct 3.0.2 register header in this file. That is intentional if the register block is shared, but it is a maintenance risk if the hardware diverges.

## Test Signals

Signals include compile success against Dimgrey Cavefish offsets, link success for `dmub_srv_dcn302_regs`, and hardware boot/DMUB command execution on DCN302 ASICs.

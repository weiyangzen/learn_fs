# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c

## Purpose

`dmub_dcn21.c` provides the DCN 2.1 DMUB register table. It does not implement new hardware behavior beyond table construction; it allows the common DCN20 hardware functions to operate on DCN21/Renoir register offsets and masks.

## Important APIs, Types, And Functions

The only exported object is `dmub_srv_dcn21_regs`, a `struct dmub_srv_common_regs` initialized by expanding `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()` through generated DCN 2.1 register macros.

## Control Flow And Data Flow

At compile time, `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT` macros expand names from `dmub_dcn20.h` into DCN21-specific offset/mask/shift constants. At runtime, service code can point `dmub->regs` at `dmub_srv_dcn21_regs` and reuse common hardware functions.

## State And Persistence Behavior

The file defines immutable register metadata. It does not read or write hardware directly and does not maintain runtime state.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn21.h`, generated `dcn_2_1_0_offset.h`, generated `dcn_2_1_0_sh_mask.h`, and `renoir_ip_offset.h`. The `BASE_INNER(seg)` macro uses `DMU_BASE__INST0_SEG##seg`, reflecting this generation's base naming.

## Risks And Edge Cases

The risk is register-definition mismatch. If `DMUB_COMMON_REGS()` names a register absent from DCN21 generated headers, build fails. If an offset or mask differs from hardware expectations, common DMUB functions will program the wrong registers.

## Test Signals

Signals include clean build against Renoir/DCN21 generated headers and successful DMUB boot/mailbox operation on DCN21 hardware using the inherited common function set.

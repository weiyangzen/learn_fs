# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_regs.h

## Purpose

`tpc0_cmdq_regs.h` is the generated MMIO address map for the Goya TPC0 command queue block. It assigns `mmTPC0_CMDQ_*` symbols to command queue global, completion queue, command processor, fence, and debug registers from `0xE09000` through `0xE0930C`.

## Important APIs, Types, and Constants

The file exports register address constants. The global block includes `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, `GLBL_ERR_CFG`, captured error address/data registers, secure/non-secure property registers, and global status registers. The CQ region includes configuration, ARUSER, pointer low/high, transfer size, control, status mirror, credit/free/in-flight status, read rate limit controls, IFIFO count, and CQ buffer debug address/data registers. CP addresses include four message base address pairs, LDMA register offsets, four fence read-data/count pairs, CP status, current instruction, barrier config, and debug register.

## Control Flow

This header has no functions. Runtime flow is in the Goya driver: queue initialization writes base/size/control values, CP message base registers, LDMA offsets, and global enable/protection; reset paths write stop/flush controls and poll idle/status addresses; diagnostics read captured error and debug registers.

## State and Persistence Behavior

The file is static generated source. The mapped registers are persistent device state until hardware reset or driver reinitialization, while pointer/status/error registers mutate as the command queue executes work.

## Dependencies and Integration Points

It is consumed with `tpc0_cmdq_masks.h` and common HabanaLabs MMIO helpers. The address map aligns with the replicated TPC command queue layout used by TPC1, TPC2, and TPC3, shifted by each TPC's base address.

## Risks

Address drift breaks command submission or diagnostics. Offsets around CQ pointer/control and CP message/fence registers are high risk because writes may be accepted by hardware but target the wrong queue mechanism.

## Test Signals

Readback after initialization, successful command completion through TPC0 CMDQ, CP fence progress, idle/stop transitions during reset, and valid error-capture addresses/data after injected queue faults are the primary validation signals.

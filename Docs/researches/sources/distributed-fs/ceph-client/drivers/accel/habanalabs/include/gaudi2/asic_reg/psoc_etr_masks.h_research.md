<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_masks.h

## Purpose
`psoc_etr_masks.h` defines bit masks and shifts for the PSOC Embedded Trace Router/Trace Memory Controller style block. It pairs with `psoc_etr_regs.h`, is guarded by `ASIC_REG_PSOC_ETR_MASKS_H_`, and exports 197 macros for trace buffer sizing, status, pointers, AXI attributes, formatter/flush control, integration test signals, lock/access registers, authentication, and CoreSight identification registers.

## Important APIs, Types, And Functions
There are no functions or types. Important field groups include:

- Trace buffer controls: `RSZ`, `STS`, `RRD`, `RRP`, `RWP`, `TRG`, `CTL`, `RWD`, `MODE`, buffer levels, watermarks, and high pointer bytes.
- AXI data buffer setup: `AXICTL` protection/cache/scatter-gather/write-burst fields plus `DBALO` and `DBAHI`.
- Formatter/flush and prescaler: `FFSR`, `FFCR`, `PSCR`.
- Integration test and ATB signal registers: `ITMISCOP0`, `ITTRFLIN`, `ITATBDATA0`, `ITATBCTR*`, and `ITCTRL`.
- CoreSight management and ID: `CLAIMSET`, `CLAIMCLR`, `LAR`, `LSR`, `AUTHSTATUS`, `DEVID`, `DEVTYPE`, `PERIPHID*`, and `COMPID*`.

## Control Flow
The header is declarative. Gaudi2 CoreSight code unlocks the ETR, disables capture if active, configures trace buffer size/mode/base address/AXI attributes, sets formatter/prescaler, enables capture, later flushes and polls readiness, and reads write pointers. The masks support safe field extraction/preparation in those flows.

## State And Persistence
ETR state is hardware state: capture enable, buffer pointers, full/empty/triggered status, memory error status, formatter flush progress, lock state, and ID values. Configuration persists until reset or explicit reconfiguration; buffer pointers and levels change while tracing runs.

## Dependencies
The masks depend on `psoc_etr_regs.h`, Gaudi2 CoreSight driver code, kernel bitfield helpers, and PSOC global trace-address registers for the high address bits used by trace buffers.

## Integration Points
The file integrates with `gaudi2_coresight.c`, which programs trace capture for PSOC tracing. It also mirrors similar ETR mask usage in earlier Habana devices. PSOC global configuration provides trace ASID/AXUSER and address high bits that complement this ETR block.

## Risks
Trace capture is sensitive to ordering: enabling capture before programming buffer base/size or AXI attributes can write trace data to the wrong address. Incorrect masks for `FFCR`, `STS`, or pointer high bits can cause flush timeouts or corrupted trace dumps. AXI protection/cache fields must match MMU/security expectations.

## Test Signals
Signals include successful CoreSight enable/disable, flush completion without timeout, correct trace buffer contents and write pointer calculation, no `MEMERR`, stable lock/unlock behavior, and expected CoreSight ID register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_masks.h -->

# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_regs.h

## Purpose
`psoc_reset_conf_regs.h` is the generated address map for the Gaudi2 PSOC reset configuration block. It names the memory-mapped registers that control reset-source policy, software/unit reset assertion, and per-instance clock/reset controls.

## Important APIs, Types, And Functions
The file exports `mmPSOC_RESET_CONF_*` address macros only. It begins with repeated eight-register policy blocks per unit: `PRSTN`, `SOFT`, `FW`, `WD`, `MNL`, `FLR`, `ECC_DERR`, and `SW` reset configuration. It then defines global reset controls such as `SOFT_RST`, `SW_ALL_RST`, and `UNIT_RST_N`, per-unit reset registers such as `ROTATOR_UNIT_RST`, and per-instance `*_CLK_RST_CTRL` registers for PSOC, CPU, ARC, SIF, SRAM, PCIe, TPC dividers, HBM dividers/controllers, PLLs, MME, MSS, TPCs, HIF/HMMU, XBARs, SFT/XFT/TFT, DMA engines, ARC subsystems, rotators, sync managers, video decoders, NIC macros, NIC ports, and NIC channels.

## Control Flow
There is no code path inside the header. Driver reset flow uses these addresses to configure which reset sources propagate, to trigger software or all-unit resets, and to poll or program unit-specific reset state. The paired mask header defines the bit meanings for the same registers.

## State, Persistence, And Dependencies
The header has no in-memory state. Writes to these addresses change hardware reset and clock state and therefore persist until later register writes or hardware reset. It depends on generated Gaudi2 register naming conventions and on callers applying the matching bit masks.

## Integration Points
This block is central to device initialization, teardown, firmware reset handshakes, PCIe FLR behavior, watchdog/ECC recovery, and per-engine quiesce/reset procedures. It intersects with `gaudi2.h` instance counts and with event/error paths that decide whether reset is needed.

## Risks
Address mistakes have high blast radius because many adjacent registers control destructive resets. The repeated layout encourages computed offsets, but callers must respect holes and unit-specific instance counts. A write intended for a clock gate can accidentally select a reset source or assert reset if the wrong address family is used.

## Test Signals
Probe and warm-reset tests should verify all critical units return to usable state, FLR leaves PCIe accessible, watchdog and firmware reset paths recover, engine-specific resets do not affect neighboring instances, and readback after writes matches mask expectations.

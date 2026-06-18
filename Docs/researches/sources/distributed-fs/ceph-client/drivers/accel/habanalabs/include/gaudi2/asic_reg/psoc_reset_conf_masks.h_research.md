# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_masks.h

## Purpose
`psoc_reset_conf_masks.h` is an auto-generated Gaudi2 PSOC reset-controller bitfield catalog. It gives the driver named `SHIFT` and `MASK` constants for reset-source enable registers, unit reset registers, and per-instance clock/reset control registers.

## Important APIs, Types, And Functions
The file exports only preprocessor macros. The first large group maps reset-source enable fields for units such as PSOC, CPU, ARC, SIF, SRAM, PCIe, TPC, HBM, DMA, rotator, sync manager, video decoder, NIC, and NIC sub-blocks. Each reset source uses an `EN_SHIFT` of 0 and an `EN_MASK` sized to the unit fan-out, for example one bit for singleton units, `0x3` for two-instance blocks, `0xF` for four-instance blocks, `0x3FF` for ten video decoders, and `0xFFF` for NIC macros. Later groups expose `SW_ALL_RST`, `UNIT_RST_N`, and `<UNIT>_UNIT_RST` fields, followed by `<UNIT>_<index>_CLK_RST_CTRL_RST_SEL_MASK` and `CLK_DIS_MASK` fields.

## Control Flow
There is no executable control flow. Runtime reset flow is controlled by callers writing registers from `psoc_reset_conf_regs.h` with these masks: enable which hardware reset causes apply to each unit, assert/deassert software or unit resets, choose a reset source with `RST_SEL`, and gate clocks with `CLK_DIS`.

## State, Persistence, And Dependencies
This header stores no state. Its constants mutate persistent device state only when used by register writes. It is coupled to the generated reset address map and to the Gaudi2 hardware reset topology; the fan-out width in each mask must match the number of instances exposed elsewhere in `gaudi2.h`.

## Integration Points
The macros integrate with low-level reset, error recovery, FLR, watchdog, firmware reset, ECC double-error reset, and clock-gating paths. They also support bring-up and debug code that needs to isolate a single engine instance instead of resetting a whole unit group.

## Risks
Because the file is generated and repetitive, the main risks are stale generated masks, mismatches between instance counts and mask widths, using a group mask as a singleton bit, and confusing active-low `UNIT_RST_N` semantics with active-high reset controls. Writes to reset and clock-gating fields can stop engines, PCIe-facing blocks, memory controllers, or firmware-visible ARC blocks until a reset sequence repairs them.

## Test Signals
Useful signals are successful driver probe after reset configuration, FLR recovery, watchdog reset handling, ECC double-error reset routing, per-engine reset of TPC/DMA/rotator/NIC blocks, clock-gate toggling without hangs, and register readback showing only intended bits changed.

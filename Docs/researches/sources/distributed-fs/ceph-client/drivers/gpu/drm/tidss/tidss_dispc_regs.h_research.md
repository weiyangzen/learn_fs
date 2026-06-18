# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc_regs.h

## Purpose

`tidss_dispc_regs.h` defines the DISPC register offset and bitfield vocabulary used by `tidss_dispc.c`. It supports per-SoC common-register relocation through an enum-indexed common register map, while VID, OVR, VP, OLDI, and AM65x IO-control offsets are encoded as fixed register-relative constants.

## Important APIs, Types, and Definitions

- `enum dispc_common_regs` enumerates common-block registers whose offsets vary across K2G, AM65x, J721E, and related SoCs.
- `REG(r)` maps common-register enum entries through the file-global `dispc_common_regmap` pointer defined in `tidss_dispc.c`.
- Common register macros cover revision, reset/status, top-level IRQ registers, per-VP/per-VID IRQ register bases, writeback IRQs, MFLAG, global output/buffer, CBA, secure/FBDC, and J721E connection routing.
- VID macros define attributes, DMA base/extension addresses, FIFO thresholds, CSC/FIR registers, picture/output sizes, increments, alpha, CLUT, safety, and J721E DMA buffer size.
- OVR macros define default/transparent colors and layer position/channel/enable fields, including the J721E alternate position register.
- VP macros define config/control/timing/polarity/size/gamma/CSC/safety/OLDI registers.
- OLDI bit definitions and `enum oldi_mode_reg_val` encode LVDS mapping, clone/dual-link, polarity, reset, enable, and AM65x IO-control power-down bits.

## Control Flow

Callers set `dispc_common_regmap` to the selected feature table's `common_regs` during `dispc_init()`. After that, macros such as `DSS_SYSSTATUS` or `DISPC_IRQENABLE_SET` expand to the correct common offset for the active hardware. VID/OVR/VP offsets are applied against already mapped per-block bases. Bitfield masks are used with `FIELD_PREP`, `FIELD_GET`, and local field-modify wrappers.

## State and Persistence Behavior

The header itself holds no state, but its `REG()` indirection depends on an external global pointer. Register writes persist in hardware until reset, runtime suspend loss, or later atomic updates. OLDI and safety macros represent hardware state that may be shared with bridge setup and system-control regmaps.

## Dependencies and Integration Points

It depends on kernel bitfield/bit macros through includers and is consumed primarily by `tidss_dispc.c`, with OLDI constants also used by `tidss_oldi.c`. It is tightly coupled to the feature-table common-register arrays in `tidss_dispc.c`.

## Risks and Edge Cases

- `REG()` has no bounds or NULL protection; using common macros before `dispc_common_regmap` is initialized would dereference invalid state.
- A missing entry in a feature common register array resolves to offset zero, which may alias a real register rather than failing obviously.
- Bitfield definitions encode hardware ABI; incorrect masks can silently corrupt adjacent fields.
- The AM65x and newer OLDI power/reset definitions live near VP register definitions, so maintainers must distinguish DISPC VP registers from external control-MMR registers.

## Test Signals

Hardware bring-up should verify register dumps for each supported compatible, especially common IRQ offsets and J721E connection routing. Static review should compare masks and offsets against TRMs. Runtime tests should validate reset/status, IRQ masking, timing fields, plane DMA extension registers, gamma table programming, and OLDI enable/disable bits on target hardware.

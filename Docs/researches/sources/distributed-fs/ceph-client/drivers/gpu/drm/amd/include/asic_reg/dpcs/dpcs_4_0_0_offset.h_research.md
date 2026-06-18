# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_0_0_offset.h

## Purpose

`dpcs_4_0_0_offset.h` is a generated AMDGPU display register offset header for the DCIO/DPCS 4.0.0 register set used by DCN 4.2 display code. It gives C preprocessor names for MMIO offsets in two address blocks: `dpcssys_dcio_dcio_dispdec` and `dpcssys_dcio_dcio_chip_dispdec`. The file does not implement display logic; it is the address half of a generated register contract used by AMD display core code to build register tables for GPIO, DDC, AUX, HPD-adjacent, clock, genlock/swaplock, debug, and soft-reset controls.

The header is guarded by `_dpcs_4_0_0_OFFSET_HEADER`. Every register has a paired `reg..._BASE_IDX` macro, and every base index in this file is `2`, so consumers combine these offsets with DCN segment-2 base addresses such as `ctx->dcn_reg_offsets[2]` or `DCN_BASE__INST0_SEG2`.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or linked symbols. The exported API is a list of `#define` constants named with AMD's `reg` prefix convention:

- Global DCIO/display-decoder controls: `regDC_GENERICA`, `regDC_GENERICB`, `regDCIO_CLOCK_CNTL`, `regDC_REF_CLK_CNTL`, `regDCIO_WRCMD_DELAY`, `regDC_PINSTRAPS`, `regDCIO_SPARE`, `regINTERCEPT_STATE`, `regDCIO_PATTERN_GEN_PAT`, `regDCIO_PATTERN_GEN_EN`, `regDPCS_DCIO_TEST_CLK_SRC`, `regDCIO_DEBUG`, `regDCIO_TEST_DEBUG_INDEX`, `regDCIO_TEST_DEBUG_DATA`, `regDBG_OUT_CNTL`, `regDCIO_DEBUG_CONFIG`, and `regDCIO_SOFT_RESET`.
- Five UNIPHY link-control and lane-crossbar register pairs: `regUNIPHYA_LINK_CNTL`/`regUNIPHYA_CHANNEL_XBAR_CNTL` through `regUNIPHYE_LINK_CNTL`/`regUNIPHYE_CHANNEL_XBAR_CNTL`.
- DDC GPIO groups for DDC1 through DDC5 and DDCVGA. Each DDC line has the four standard GPIO registers `MASK`, `A`, `EN`, and `Y`, e.g. `regDC_GPIO_DDC1_MASK`, `regDC_GPIO_DDC1_A`, `regDC_GPIO_DDC1_EN`, and `regDC_GPIO_DDC1_Y`.
- Power-sequencer and pad controls: `regDC_GPIO_PWRSEQ0_EN`, `regDC_GPIO_PWRSEQ1_EN`, `regDC_GPIO_PAD_STRENGTH_1`, `regPHY_AUX_CNTL`, `regDC_GPIO_AUX_CTRL_0`, `regDC_GPIO_AUX_CTRL_1`, `regDC_GPIO_AUX_CTRL_3`, `regDC_GPIO_AUX_CTRL_4`, `regDC_GPIO_AUX_CTRL_5`, and `regAUXI2C_PAD_ALL_PWR_OK`.

Consumer macros such as `REG(reg_name)` expand these definitions by concatenation: `BASE(reg ## reg_name ## _BASE_IDX) + reg ## reg_name`. That makes names like `REG(DC_GPIO_DDC1_A)` resolve to the correct DCN 4.2 absolute register address.

## Control Flow

The file has no runtime control flow. Its only direct flow is the compile-time include guard followed by linear register definitions grouped by generated address-block comments. Runtime behavior is entirely in consumers. DCN 4.2 GPIO and resource code includes this header with `dpcs_4_0_0_sh_mask.h`, defines a `BASE()` macro over segment 2, and expands register-list macros into static tables or switch cases.

A typical DDC path is: `hw_factory_dcn42.c` expands `ddc_data_regs_dcn2(id)` or `ddc_clk_regs_dcn2(id)`, which uses `REG(DC_GPIO_DDCx_A)`, `REG(DC_GPIO_DDCx_EN)`, `REG(DC_GPIO_DDCx_Y)`, `REG(DC_GPIO_DDCx_MASK)`, `REG(PHY_AUX_CNTL)`, and `REG(DC_GPIO_AUX_CTRL_5)` to populate `struct ddc_registers`. A translation path in `hw_translate_dcn42.c` maps BIOS or GPIO offsets back to `GPIO_DDC_LINE_DDC1` through `GPIO_DDC_LINE_DDC5` and `GPIO_DDC_LINE_DDC_VGA`, then derives related `Y`, `EN`, and `MASK` offsets by adding `+2`, `+1`, and `-1` to the `A` register offset.

## State And Persistence Behavior

This header stores no software state and performs no persistence. It names hardware registers whose values represent display hardware state: GPIO output enables and readbacks, AUX/DDC pad routing, UNIPHY lane mapping and reset controls, pinstrap status, pattern generator settings, genlock/swaplock pad controls, debug windows, and power-sequencer enable bits. Those hardware values can persist across ordinary driver reads and writes, but may be reset or rewritten by firmware, display initialization, suspend/resume, GPU reset, or power-gating transitions.

Because offsets are compile-time constants, there is no locking or caching in this file. Synchronization, read-modify-write discipline, reserved-bit preservation, and reset ordering belong to the display core and hardware-sequencing code that consumes the macros.

## Dependencies

The file has no `#include` dependencies. Operationally it depends on:

- The matching generated field header `dpcs_4_0_0_sh_mask.h`, which must describe the same registers and ASIC revision.
- AMD display register helpers and table-generation macros such as `REG`, `SR`, `SRI`, `SF_DDC`, `DDC_GPIO_REG_LIST`, and `DDC_MASK_SH_LIST_DCN2`.
- Correct DCN 4.2 base selection. Local consumers define `DCN_BASE__INST0_SEG2` or use `ctx->dcn_reg_offsets[2]`; every `_BASE_IDX` here points at that segment.
- ASIC dispatch that includes this header only for hardware whose DCIO/DPCS register layout matches DPCS 4.0.0.

## Integration Points

Direct local include points are `display/dc/gpio/dcn42/hw_factory_dcn42.c`, `display/dc/gpio/dcn42/hw_translate_dcn42.c`, and `display/dc/resource/dcn42/dcn42_resource.c`. The GPIO factory uses DDC offsets to build DDC clock/data register arrays and DDC shift/mask arrays. The GPIO translator uses the same offsets to convert between register offsets and DAL GPIO identities. The resource file includes this header as part of the wider DCN 4.2 register universe used to initialize display hardware blocks.

The header also preserves compatibility with generic display-core register list patterns. DDC code expects the standard four-register GPIO layout (`MASK`, `A`, `EN`, `Y`) to be contiguous in the generated offsets, and DCN 4.2 relies on that arithmetic in `id_to_offset()`. DIO/link-encoder families use similar DCIO names such as `DCIO_SOFT_RESET` and UNIPHY crossbar controls in earlier generations, so generation skew in this file would affect common register-table assumptions even if the direct DCN 4.2 consumer is small.

## Risks And Edge Cases

The highest risk is silent MMIO misaddressing. A wrong offset or wrong base index can compile cleanly while reading or writing the wrong display register, causing failed EDID/DDC transactions, broken AUX/DDC pad selection, bad GPIO direction/readback, incorrect UNIPHY lane routing, failed soft reset sequencing, or display bring-up failures. The register values are bare integers, so the compiler cannot validate hardware correctness.

The DDC GPIO offsets are structurally important: `hw_translate_dcn42.c` assumes `A`, `EN`, `Y`, and `MASK` are adjacent with fixed relative offsets. Changing the order or adding gaps would break derived `offset_y`, `offset_en`, and `offset_mask` calculations. DCN 4.2 factory code allocates DDC1 through DDC5, a dummy sixth entry, and VGA; this header provides DDC1 through DDC5 and DDCVGA but no `DC_GPIO_DDC6_*` offsets, so any consumer trying to instantiate a real DDC6 GPIO register set from this header would fail to compile or need a different mapping.

Another risk is offset/mask skew. If this offset file is regenerated without the paired shift/mask file, table macros can combine a correct address with stale bitfields, which is especially hazardous for DDC pad mode, AUX polarity, RX select, power-good, and soft-reset bits.

## Test Signals

Static validation should build the DCN 4.2 GPIO factory, GPIO translator, resource code, DDC/AUX helpers, and any link-encoder paths that include the DPCS 4.0.0 headers. Undefined macro failures are useful for missing names, but numeric offset regressions require comparison against the authoritative ASIC register database or a generated-header diff.

Runtime signals include successful DCN 4.2 display initialization, working HPD-to-DDC translation from BIOS GPIO offsets, reliable EDID reads on DDC1 through DDC5 and VGA, correct AUX/DDC pad mode selection, suspend/resume with no stale GPIO direction or power-good failures, and absence of MMIO timeout or display-core assertion logs around `DC_GPIO_DDC*_A`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_5`, and `DCIO_SOFT_RESET` accesses.

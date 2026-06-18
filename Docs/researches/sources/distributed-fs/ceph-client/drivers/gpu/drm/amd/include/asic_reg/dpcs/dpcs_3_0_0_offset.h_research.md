# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_0_offset.h

## Purpose
`dpcs_3_0_0_offset.h` is a generated AMD DCN 3.0 DPCS register-offset map. It gives the display driver preprocessor names for DPCS transmitter (`DPCSTX`), retimer/PHY-side DPCS transmitter (`RDPCSTX`), and DPCS CR address/data registers for six link instances. The file is not executable code; its value is that every register name expands to the ASIC-specific MMIO offset used by common AMD display register helper macros.

## Important APIs, Types, And Functions
There are no C functions, structs, enums, or runtime APIs. The exported interface is 524 `#define`s: 262 register offset constants and 262 matching `_BASE_IDX` constants. Each offset macro follows AMD's generated register naming convention, such as `mmDPCSTX0_DPCSTX_TX_CLOCK_CNTL`, `mmRDPCSTX0_RDPCSTX_PHY_CNTL6`, and `mmDPCSSYS_CR0_DPCSSYS_CR_ADDR`.

The six `DPCSTXn` blocks expose core transmitter controls: TX clocking, TX control, CBUS control, interrupt control, PLL update address/data, and debug configuration. The six `RDPCSTXn` blocks expose retimer/PHY-facing controls: FIFO/control registers, clock and interrupt control, PLL update data, CR address/data windows, SRAM control, scratch/spare registers, 15 PHY control registers, PHY fuse registers, RX load values, DMCU DP alternate-mode registers, and DPALT control. `DPCSSYS_CR0` through `DPCSSYS_CR4` alias the corresponding RDPCS CR address/data registers for instances 0 through 4.

## Control Flow
The header has no branches or runtime control flow. Its compile-time flow is the include guard `_dpcs_3_0_0_OFFSET_HEADER`, then a linear sequence of generated address-block comments and macro definitions. Consumer code expands register-list macros into table initializers or switch cases by concatenating `mm`, register names, and `_BASE_IDX`; for example `BASE(mmREG_BASE_IDX) + mmREG` produces a final byte/word address in DCN30 GPIO and clock-manager code.

## State, Persistence, And Dependencies
The file stores no mutable state and has no persistence behavior. It represents hardware state indirectly by naming MMIO locations whose contents are persistent only as GPU register state across reset/power-management boundaries according to the hardware block. All `_BASE_IDX` values in this file are `2`, so consumers depend on the DCN base-address macros for segment 2 when turning an offset into an absolute MMIO address.

Its immediate dependency is the generated ASIC register ecosystem: matching bitfield definitions are in `dpcs_3_0_0_sh_mask.h`, and consumer code also includes DCN, NBIO, MMHUB, and SoC IP offset headers such as `sienna_cichlid_ip_offset.h`. The source-level dependency is preprocessor compatibility with AMD's register helper macros (`REG`, `SR`, `SRI`, `LE_SF`, `REG_GET`, `REG_UPDATE`, and related forms), not a linked symbol dependency.

## Integration Points
DCN30 IRQ, GPIO translation/factory, and clock-manager files include this header directly with the matching shift/mask header. Link encoder code uses the same DPCS and RDPCS names through per-generation register and field lists; DCN301 extends the DCN20 DPCS field list with HDMI FRL/data ordering fields and RDPCS TX clock/vboost fields. HPO and DIO link encoders read and write RDPCS PHY registers for DisplayPort alternate mode, lane power/control, MPLL programming, FIFO enablement, and PHY status.

The address layout is instance-patterned: instance 0 starts at offsets around `0x2928`, then instances 1 through 5 advance by the generated block stride visible in the comments (`0x360` base-address increments) to offsets through `0x2d8e`. This lets common display code keep one set of register names and choose the instance through generated `SRI`/array-style register tables.

## Risks
The major risk is silent hardware misaddressing: a wrong offset or wrong `_BASE_IDX` can direct register helper macros to the wrong MMIO location, causing link training failures, interrupt misconfiguration, bad clock/PLL programming, DP alternate-mode breakage, or hangs during display initialization. Because the file is generated and contains no type checking, misspelled or missing macro names usually fail at compile time, while numerically incorrect values can survive compilation.

The `DPCSSYS_CRn` macros alias `RDPCSTXn_RDPCS_TX_CR_ADDR/DATA` offsets, so changes must preserve that intentional overlap. The file defines CR aliases only for instances 0 through 4, while DPCSTX/RDPCSTX offsets exist for instance 5; any consumer assuming a CR5 alias would fail to compile. Another compatibility risk is generation skew between this offset header and `dpcs_3_0_0_sh_mask.h`: offsets and field masks must describe the same ASIC revision.

## Test Signals
Useful compile-time signals are successful builds of DCN30 IRQ, GPIO, clock-manager, DIO, and link-encoder objects that include or depend on these names, with no undefined register or bitfield macros. Runtime signals are successful display bring-up on DCN 3.0 hardware, HPD and HPD RX interrupt delivery, stable clock-manager initialization, DisplayPort/HDMI link training, DP alternate-mode enable/disable transitions, PLL programming, PHY lane enable/reset behavior, and absence of MMIO fault or timeout logs around RDPCS/DPCS register access.

For generated-register maintenance, compare the offset sequence against the authoritative ASIC register database, verify each `mm..._BASE_IDX` stays aligned with the intended DCN base segment, and cross-check that every register used by `dpcs_3_0_0_sh_mask.h` and DCN30/301 register lists has a matching offset macro.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h

## Purpose
`dpcs_2_0_0_offset.h` is a generated DCN 2.0 DisplayPort/PHY Control Subsystem register offset map. It supplies MMIO offsets and base indices for six DPCSTX/RDPCSTX transmitter instances, per-link CR address/data aliases, shared DPCSRX receiver controls, and related debug, PLL, PHY, SRAM, fuse, DPALT, and power-control registers.

## Important APIs, Types, And Functions
The file exports preprocessor macros only. For each link instance 0 through 5 it defines `mmDPCSTXn_DPCSTX_*` TX clock/control/CBUS/interrupt/PLL/debug registers, `mmRDPCSTXn_RDPCSTX_*` control/clock/interrupt/PLL/memory/debug/PHY/fuse/DPALT registers, and `mmDPCSSYS_CRn_DPCSSYS_CR_ADDR/DATA` aliases. It also defines shared `mmDPCSRX_*` receiver and indexed-access registers. All listed registers use `_BASE_IDX 2`.

## Control Flow
The header has no runtime flow. It is consumed by DCN resource setup through `DPCS_DCN2_REG_LIST(id)` in `dcn20_resource.c`. That macro expands into per-link register tables for link encoders, letting link-encoder code program clocks, TX controls, PHY lanes, PLL update data, fuses, DP alternate-mode controls, and debug registers by struct field rather than hard-coded offsets.

## State, Persistence, And Dependencies
The macros are compile-time constants. Runtime state lives in display hardware registers and persists according to DCN power, reset, and link-training flows. The header depends on the display register-helper macros `SR`, `SRI`, and link-encoder mask/shift lists, and is normally paired with `dpcs_2_0_0_sh_mask.h` for bitfield definitions.

## Integration Points
`drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` includes this file and builds `link_enc_regs[]` for six links via `DPCS_DCN2_REG_LIST(id)`. `dcn20_link_encoder.h` defines that list and names the DPCS/RDPCS fields link encoders need, including `RDPCSTX_PHY_CNTL*`, `RDPCS_TX_CR_ADDR/DATA`, `RDPCSTX_PHY_FUSE*`, `DPCSTX_TX_CLOCK_CNTL`, `DPCSTX_TX_CNTL`, `DPCSTX_DEBUG_CONFIG`, `RDPCSTX_DEBUG_CONFIG`, and DPALT registers.

## Risks
The table is large and repetitive, so instance-stride or copy/paste errors are the main risk. A wrong offset can affect link training, PHY programming, PLL updates, AUX/CBUS behavior, DP alternate mode, or debug access for a single connector. Alias registers such as `DPCSSYS_CRn` sharing RDPCS TX CR address/data offsets must remain intentional. Because every macro uses base index 2, a base-index generation error would break the whole DCN20 link-encoder register map.

## Test Signals
Useful signals include successful compilation of DCN20 resource and link-encoder code, link training across all six possible transmitter instances, hotplug and HPD tests, DP and HDMI modeset tests, DPALT/USB-C display tests where applicable, register dumps confirming per-instance strides, and comparison of offset tables against the generated ASIC register source.

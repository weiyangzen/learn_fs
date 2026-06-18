# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi_regs.h

## Purpose

`rzg2l_mipi_dsi_regs.h` defines register offsets and bitfields for the RZ/G2L and RZ/V2H MIPI DSI D-PHY and link blocks.

## Important APIs, Types, and Functions

Macro groups cover classic RZ/G2L D-PHY control/timing registers, RZ/V2H PLL/PHY reset and timing registers, link status, lane and HS clock controls, DSI receive result slots, clock-lane and LP transition timing, video-input channel programming, and sequence-channel descriptor registers for command transfer.

## Control Flow

`rzg2l_mipi_dsi.c` uses these macros during SoC-specific D-PHY initialization, PLL programming, HS clock start/stop, video timing programming, command descriptor setup, and response parsing.

## State and Persistence Behavior

No software state exists. The macros describe hardware register state that persists until reset, runtime suspend, or driver reprogramming.

## Dependencies and Integration Points

It depends on Linux `bits.h` and is consumed by the RZ/G2L MIPI DSI implementation.

## Risks and Edge Cases

- Some macros use plain shifts while others use `GENMASK`; callers must use `FIELD_PREP()` only with mask macros.
- Register offsets are interpreted relative to SoC-specific `phy_reg_offset` and `link_reg_offset`.
- Descriptor address register stores a 32-bit physical address, matching the current coherent buffer assumption.

## Test Signals

Compile checks, register trace validation for RZ/G2L and RZ/V2H startup, and descriptor command transfer tests validate this header.

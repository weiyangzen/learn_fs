# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x_reg.h

## Purpose

This header defines LAN937x register addresses, bit fields, masks, port address translation, frame-size constants, RGMII delay constants, and the DSA tag length used by `lan937x_main.c` and the Microchip KSZ common driver code. It is the hardware contract for programming global switch blocks, virtual PHY access, per-port MAC/xMII/classification/shaping controls, and LAN937x-specific port numbering.

## Important APIs, Types, And Definitions

`PORT_CTRL_ADDR(port, addr)` builds per-port register addresses by combining a block offset with the 1-based hardware port selector. Global definitions cover `REG_GLOBAL_CTRL_0`, interrupt status/mask registers, strap registers, `REG_SW_OPERATION`, LUE ageing/VLAN controls, MAC controls, ALU fields, and VPHY indirect access registers. Per-port definitions cover interrupt bits, `REG_PORT_CTRL_0`, T1/TX PHY register base offsets, xMII controls, DLL delay fields, MAC frame-size controls, priority controls, and credit increment shaping.

Key constants include `SWITCH_INT_MASK`, `SW_PHY_REG_BLOCK`, `SW_RESET`, `SW_LINK_AUTO_AGING`, `SW_AGE_CNT_M`, `SW_AGE_CNT_IN_MICROSEC`, `VPHY_IND_BUSY`, `VPHY_IND_WRITE`, `VPHY_MDIO_INTERNAL_ENABLE`, `VPHY_SPI_INDIRECT_ENABLE`, `PORT_TAIL_TAG_ENABLE`, `PORT_JUMBO_PACKET`, `PORT_MAX_FR_SIZE`, `FR_MIN_SIZE`, `PORT_TUNE_ADJ`, `PORT_DLL_RESET`, and `LAN937X_TAG_LEN`.

## Control Flow

The header has no runtime control flow, but its definitions directly shape driver sequences. Reset and interrupt masking use global operation and interrupt fields. PHY access uses the VPHY address/data/control triplet and busy bit. Port setup uses `PORT_CTRL_ADDR()` with MAC, xMII, and priority offsets. Ageing-time code splits multiplier and period values across the LUE fields. MTU code uses `FR_MIN_SIZE` and `PORT_MAX_FR_SIZE`, while CPU-port MTU adjustment uses `LAN937X_TAG_LEN`.

## State And Persistence Behavior

All definitions refer to hardware state persisted in LAN937x registers: interrupt masks/status, strap overrides, LUE state, ALU content, VPHY mode, port tail tagging, xMII delay tuning, MAC frame-size controls, priority selection, and shaper credit increments. The header itself stores no software state.

## Dependencies And Integration Points

The header assumes Linux bit helpers such as `BIT()`, `GENMASK()`, `FIELD_PREP()`, and `FIELD_GET()` are available through including C files. It integrates with `lan937x_main.c`, common KSZ register helpers, DSA tag accounting, and traffic-control CBS code. The port constants `LAN937X_RGMII_1_PORT` and `LAN937X_RGMII_2_PORT` are zero-based translations of datasheet port numbers used by delay setup.

## Risks

Incorrect bit masks or port offset calculations would cause writes to the wrong hardware block. The similar global and per-port interrupt names require careful use of `REG_SW_*` versus `REG_PORT_*`. `FR_MIN_SIZE` and `LAN937X_TAG_LEN` feed packet-size enforcement, so drift from hardware framing requirements can cause dropped frames or undersized jumbo programming. RGMII delay constants are characterization-derived values and may require board-level validation.

## Test Signals

Compile coverage should catch missing macro dependencies. Runtime signals include successful switch reset, stable VPHY indirect read/write polling, correct interrupt masking, expected MTU threshold behavior, and link stability on both RGMII ports after delay programming.

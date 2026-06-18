## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mac.h

Purpose: centralizes v2 MAC, RGMII, ICM/ECM, and MDIO management register offsets and bitfield helpers.

Important APIs, types, and functions: constants cover `MAC_CONFIG_1/2`, MII management registers, `INTERFACE_CONTROL`, station address registers, `RGMII_REG_0`, ICM/ECM registers, enable/reset bits, speed/interface fields, FIFO threshold fields, and MII busy/read controls. Inline helpers `xgene_set_reg_bits` and `xgene_get_reg_bits`, plus macros `SET_REG_BITS`, `SET_REG_BIT`, `GET_REG_BITS`, and `GET_REG_BIT`, perform field packing. It declares all `xge_mac_*` functions.

Control flow, state, and dependencies: the header carries no state but is included by `main.h`, `mac.c`, and `mdio.c`. It depends on Linux bit macros.

Integration points: MDIO and MAC code both rely on the management register definitions; mistakes affect PHY access and link setup.

Risks: field helper semantics are easy to misuse because the length parameter is passed into `GENMASK(pos + len, pos)`. Changes require hardware-register review. `GET_REG_BIT` is a raw mask test, unlike `GET_REG_BITS`.

Test signals: compile with `W=1`; validate MDIO reads/writes, 10/100/1000 speed changes, station address programming, and TX/RX enable toggles.

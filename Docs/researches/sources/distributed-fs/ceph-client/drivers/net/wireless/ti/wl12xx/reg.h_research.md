# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/reg.h

Purpose: Defines wl12xx hardware register addresses, firmware status address, OCP top-register access protocol, clock/PLL configuration bits, interrupt trigger bits, HI config, PG/fuse decoding macros, and fuse MAC register addresses.

Important APIs and types: Key constants include `REGISTERS_BASE`, `DRPW_BASE`, `FW_STATUS_ADDR`, `WL12XX_SLV_SOFT_RESET`, slave data registers, interrupt registers, ECPU/HI config, OCP registers and status bits, scratch pads, PLL/clock registers, `WL12XX_CMD_MBOX_ADDRESS`, `WL12XX_EEPROMLESS_IND`, `WL12XX_INTR_TRIG_CMD`, `WL12XX_INTR_TRIG_EVENT_ACK`, `HI_CFG_DEF_VAL`, PG version masks/macros, and fuse BD address registers.

Control flow: Header only. Its constants drive `main.c` boot, OCP read/write polling, partition register table setup, interrupt enabling, command triggering, and MAC/fuse reads.

State and persistence: Describes hardware register state and fuse contents. Fuse MAC and PG version are persistent in hardware, while most registers are volatile boot/runtime state.

Dependencies and integration points: Included by wl12xx `main.c` and any code needing chip register definitions. Values are mapped into wlcore generic register IDs through `wl12xx_rtable`.

Risks: Register values are hardware ABI. Incorrect OCP status masks or clock bits can break boot. PG version macros differ between wl127x and wl128x and must be used with the correct chip family.

Test signals: Successful chip ID and PG version reads, soft reset completion, clock/PLL programming, firmware status reads, command/event interrupt triggers, and fuse MAC extraction.

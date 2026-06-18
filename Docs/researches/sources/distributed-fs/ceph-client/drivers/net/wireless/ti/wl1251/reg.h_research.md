# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/reg.h

Purpose: Defines wl1251 target register addresses, partition sizes, ELP controls, EEPROM/chip registers, interrupt register indexes, RX filter bits, firmware boot constants, rates/modulations, and host-to-firmware interrupt trigger bits.

Important APIs and types: Important definitions include `REGISTERS_BASE`, `DRPW_BASE`, `HW_ACCESS_ELP_CTRL_REG_ADDR`, `ELPCTRL_*`, `CHIP_ID_B`, `ENABLE`, scratch-pad and mailbox pointers, `enum wl12xx_acx_int_reg`, `RX_CFG_*`, `RX_FILTER_OPTION_*`, EEPROM registers and control bits, firmware `CHUNK_SIZE`, rate enums, modulation bits, and `INTR_TRIG_*`.

Control flow: No executable control flow. These constants drive address translation, boot, firmware mailbox discovery, RX filter programming, TX/RX buffer acknowledgements, and ELP operations.

State and persistence: Describes hardware state and firmware-visible registers. Values are not stored by the driver except through reads/writes in other modules.

Dependencies and integration points: Included throughout wl1251 boot, IO, PS, RX/TX, ACX, command, event, SPI, and main files. The `enum wl12xx_acx_int_reg` is translated by `io.c` to concrete addresses.

Risks: Register constants are hardware contract values. Incorrect edits can break boot, partitioning, interrupts, EEPROM MAC reads, or data path acknowledgements. Some comments retain historical spelling and reference driver terminology; use behavior over comments when validating.

Test signals: Hardware boot, chip ID recognition, ELP wake, interrupt delivery, RX/TX acknowledgement, EEPROM read, and join/filter behavior validate this file indirectly.

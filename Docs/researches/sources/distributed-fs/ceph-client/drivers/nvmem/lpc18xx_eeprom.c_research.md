# sources/distributed-fs/ceph-client/drivers/nvmem/lpc18xx_eeprom.c

Purpose: NXP LPC18xx/LPC43xx EEPROM NVMEM provider with readable and writable word access.

Important APIs/types/functions: `struct lpc18xx_eeprom_dev` stores clock, register and memory mappings, access widths, and size. `lpc18xx_eeprom_read()` and `lpc18xx_eeprom_gather_write()` implement NVMEM callbacks; `lpc18xx_eeprom_busywait_until_prog()` polls `END_OF_PROG`; probe maps named `reg` and `mem` resources, configures clock divider/autoprogramming, powers down the EEPROM, and registers `lpc18xx_nvmem_config`.

Control flow: probe enables the EEPROM clock, asserts reset, programs the divider for roughly 1.5 MHz EEPROM operation, enables word autoprogramming, powers the block down, then exposes 4-byte stride/word NVMEM. Reads and writes power up, wait 100 us, transfer 32-bit words, and power down; writes wait for completion after each word.

State/persistence: EEPROM contents persist in hardware. Driver state is devm-managed except the prepared/enabled clock, which is disabled in remove or on probe failure. The last page is reserved for initialization data and rejected for writes.

Dependencies/integration: platform driver for `nxp,lpc1857-eeprom`; uses named memory resources, reset controller, clock framework, MMIO, and NVMEM provider core.

Risks: callbacks assume 4-byte aligned accesses supplied by NVMEM stride/word rules. Error paths during write can leave the EEPROM powered if failure occurs before the final power-down. The global static `nvmem_config` is modified at probe, which is typical for single-instance platform drivers but unsafe for unexpected multiple instances.

Test signals: validate read/write with aligned 4-byte operations, timeout behavior when `END_OF_PROG` never arrives, rejection of writes into the protected final page, and clock/reset cleanup on probe failures.

# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-nvram.c

Purpose: reads IP22 NVRAM or serial EEPROM values, primarily for MAC addresses and firmware environment-derived data.

Important APIs and control flow: bit-banged EEPROM macros control chip select, clock, data out, and protection bits. `eeprom_cmd()` shifts an 11-bit command/register sequence. `ip22_eeprom_read()` issues an EEPROM read and clocks out 16 bits. `ip22_nvram_read()` selects Microwire EEPROM on FullHouse or DS1386 BBRAM word reads on Indy.

State, persistence, and integration: no Linux state is stored, but reads persistent board EEPROM/BBRAM contents. Dependencies include initialized `hpc3c0`, board type, and stable early delay loops. Risks include busy-wait timing sensitivity, no locking for shared EEPROM control, read-only support, and direct raw access during early boot. Test signals are correct Ethernet MAC extraction and stable NVRAM values across boots.

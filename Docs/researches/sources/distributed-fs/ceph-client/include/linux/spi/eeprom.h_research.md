<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/eeprom.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/eeprom.h

Purpose: This header defines platform data for AT25-like SPI EEPROMs.

Important APIs/types/functions: `spi_eeprom` includes byte length, name, page size, flags, and opaque context. Flags select one-, two-, or three-byte addresses, read-only policy, and `EE_INSTR_BIT3_IS_ADDR` for devices that extend address space through instruction bit 3.

Control flow: Board code passes the structure as platform data; the at25 driver uses it to choose command/address formatting, write page size, device name, and write permissions.

State and persistence: Platform data is static. Persistent state is the EEPROM contents and hardware write-protect behavior.

Dependencies/integration: Depends on `linux/memory.h` and integrates with SPI EEPROM/MTD/NVMEM style users.

Risks and test signals: Risks include wrong address-width flags causing wraparound, page-size mismatch corrupting writes, accidental writes to read-only hardware, and incorrect instruction-bit addressing. Test read/write boundaries, page crossing, read-only enforcement, NVMEM/MTD registration, and device-size probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/eeprom.h -->

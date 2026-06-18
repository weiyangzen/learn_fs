# sources/distributed-fs/ceph-client/drivers/fpga/machxo2-spi.c

Purpose: FPGA manager for loading Lattice MachXO2 firmware over slave SPI using sysCONFIG programming commands. It erases/programs nonvolatile configuration pages, issues program-done and refresh commands, and reports operating state from the MachXO2 status register.

Important APIs and functions: command definitions include `ISC_ENABLE`, `ISC_ERASE`, `LSC_INITADDRESS`, `LSC_PROGINCRNV`, `ISC_PROGRAMDONE`, `LSC_REFRESH`, and `LSC_READ_STATUS`. `get_status` performs command+read SPI messages and converts big-endian status. `wait_until_not_busy` polls BUSY with a bounded loop. Manager ops are `machxo2_spi_state`, `machxo2_write_init`, `machxo2_write`, and `machxo2_write_complete`. `machxo2_cleanup` erases and refreshes after failures. Probe enforces `MACHXO2_MAX_SPEED` and registers the manager.

Control flow: write-init rejects partial reconfiguration, enables ISC, erases, waits for not busy, checks FAIL, and initializes the programming address. Write validates that the bitstream count is a multiple of the 16-byte page size and sends each page with the `LSC_PROGINCRNV` command and delay. Write-complete sends `ISC_PROGRAMDONE`, waits, verifies DONE, then repeatedly refreshes until DONE, no BUSY, and no error or until refresh-loop exhaustion. Cleanup is attempted on failed DONE/refresh checks.

State and persistence: Linux state is the SPI device pointer stored as manager private data. Hardware state includes nonvolatile configuration memory, status bits, error bits, and refresh/programming mode. The loaded image persists according to MachXO2 configuration storage.

Dependencies and integration points: depends on SPI, FPGA manager framework, OF compatible `lattice,machxo2-slave-spi`, and SPI ID `machxo2-slave-spi`.

Risks and test signals: risks include strict 16-byte alignment, limited busy/refresh loop counts, status register endian assumptions, cleanup erasing after failure, and no partial reconfiguration. Test signals are accepted SPI speed, status DONE/ERR transitions, page-count write logs under tracing, manager state operating, and failed malformed payload returning `-EINVAL`.

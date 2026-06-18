# sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-pmci.c

Purpose: DFL PMCI transport for Intel MAX 10 BMC on N6000-class FPGA devices. It implements indirect register access, flash FIFO bulk operations, flash host mux control, and registers MAX10 child devices.

Important APIs/types/functions: `m10bmc_pmci_probe()`, `indirect_reg_read()`, `indirect_reg_write()`, `m10bmc_pmci_flash_read()`, `m10bmc_pmci_flash_write()`, `m10bmc_pmci_flash_lock()`, `m10bmc_pmci_flash_unlock()`, and `m10bmc_pmci_flash_bulk_ops`.

Control flow: probe maps DFL MMIO, creates an indirect regmap over the controller command/address/data registers, initializes flash mutex state, attaches flash operations, and calls `m10bmc_dev_init()`. Register reads/writes issue commands and poll for ACK, then clear command state. Flash reads request host mux, use FIFO read commands, and release mux.

State and persistence: `flash_mutex` serializes flash reads and write sessions; `flash_busy` blocks reads during a locked write. Controller command completion is polling based; no persistent state is stored.

Dependencies and integration: depends on DFL bus, MMIO regmap custom read/write callbacks, MAX10 core, N6000 CSR constants, and child drivers `n6000bmc-hwmon` and `n6000bmc-sec-update`.

Risks: FIFO sizes, remainder handling, mux arbitration, and indirect command clearing are correctness-sensitive. Timeouts return errors but may leave hardware state needing cleanup. Write requires callers to hold the flash lock.

Test signals: DFL feature binding, regmap read/write smoke tests, flash read/write including sub-word remainders, concurrent read/write exclusion, host mux release on failures, and secure-update child flows.

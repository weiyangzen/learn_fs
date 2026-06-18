# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/subr.c

## Purpose
`subr.c` provides shared support routines for the Chelsio T1/T2 `cxgb` driver: TPI register access, MDIO access through Elmer0 MI1, board tables, EEPROM/VPD reads, link setup, slow interrupt dispatch, board initialization, and adapter software/hardware module bring-up and teardown.

## Important APIs, Types, And Functions
- `t1_wait_op_done` polls an MMIO register bit until a requested polarity appears, used for TPI transactions.
- `__t1_tpi_write`, `t1_tpi_write`, `__t1_tpi_read`, and `t1_tpi_read` implement unlocked and locked TPI access through `A_TPI_ADDR`, `A_TPI_WR_DATA`, `A_TPI_RD_DATA`, and `A_TPI_CSR`.
- `t1_link_changed` reads PHY link status, updates `struct link_config`, programs MAC speed/duplex/flow control when autonegotiation has settled, and calls the OS-specific `t1_link_negotiated`.
- `t1_pci_intr_handler`, `fpga_slow_intr`, `asic_slow_intr`, and `t1_slow_intr_handler` dispatch slow-path interrupt causes across SGE, TP, ESPI, external MAC/PHY, and PCI-X errors.
- `mi1_mdio_init`, `mi1_mdio_read/write`, and `mi1_mdio_ext_read/write` implement Clause 22 and indirect Clause 45 style MDIO over Elmer0.
- `t1_board` and `t1_pci_tbl` map PCI IDs to `board_info` entries for T110/N110/N210/T210 and optional 1G N204 boards.
- `t1_get_board_info`, `t1_seeprom_read`, `vpd_macaddress_get`, `t1_link_start`, `t1_elmer0_ext_intr_handler`, `t1_interrupts_enable/disable/clear`, `t1_get_board_rev`, `t1_init_hw_modules`, `t1_free_sw_modules`, and `t1_init_sw_modules` are the exported board/module services.

## Control Flow And State
Probe-time flow starts with board identification via `t1_pci_tbl` and `t1_get_board_info`, then `t1_init_sw_modules` stores board parameters, creates SGE/ESPI/TP state, runs `board_init`, initializes MDIO, optionally resets global PHY/MAC blocks, creates each port's `cphy` and `cmac`, obtains MAC addresses from VPD or the MAC, initializes link config, records PCI mode, and clears interrupts. Hardware module setup then runs `t1_init_hw_modules`, which prepares MC4/MC5 fallback state if no MC4 clock exists, initializes ESPI, resets/configures TP, and configures SGE.

Link start uses `t1_link_start`: if the PHY supports autonegotiation it computes pause advertisement, advertises it, then either forces speed/duplex/flow-control or enables autonegotiation. Non-autoneg PHYs are reset after MAC flow-control programming. Runtime link changes are delivered through PHY interrupt handlers into `t1_link_changed`.

Interrupt flow is split between fast SGE data interrupts elsewhere and slow causes in this file. ASIC slow interrupts are masked by `adapter->slow_intr_mask`, then fan out to SGE error handling, TP, ESPI, PCI-X, and external interrupts. External interrupts are moved to the threaded handler by setting `adapter->pending_thread_intr`, masking `F_PL_INTR_EXT`, and returning `IRQ_WAKE_THREAD`. FPGA builds use separate cause bits and quirks.

## State And Persistence Behavior
Persistent hardware state includes TPI-programmed external MAC/PHY registers, Elmer0 GPIO/TPI parameters, MDIO configuration, EEPROM/VPD contents, and PCI config interrupt/status registers. Software state includes `adapter->params`, per-port `phy`, `mac`, and `link_config`, `slow_intr_mask`, and `pending_thread_intr`. EEPROM reads are read-only and require 4-byte alignment within an 8 KiB space.

## Dependencies And Integration Points
The file depends on `common.h`, Elmer0 registers, Terminator registers, GMAC/PHY/SGE/TP/ESPI operation tables, Linux PCI config helpers, spinlocks, delays, and netdev address helpers. It integrates the board table with lower-level MAC and PHY drivers such as PM3393, VSC7326, Marvell PHYs, MY3126, SGE, TP, and ESPI. OS-specific callbacks include `t1_link_negotiated`.

## Risks And Edge Cases
TPI and MDIO operations can time out; failures are logged and sometimes returned as generic nonzero errors. PCI-X errors are treated as fatal and disable interrupts. External interrupt handling requires process context, so masking/re-enabling must remain paired. Board table values encode clocks, GPIOs, PHY base addresses, and MAC/PHY operation tables; wrong entries can misprogram hardware. VPD MAC derivation increments only the final byte, which assumes a contiguous base address range.

## Test Signals
Probe tests should cover each board ID mapping, VPD read failure handling, MAC/PHY allocation cleanup, and successful interrupt clear/enable/disable cycles. Runtime signals include MDIO reads/writes succeeding under `tpi_lock`, link up/down and autonegotiation changes reaching `t1_link_negotiated`, PCI-X error injection disabling interrupts, SGE error interrupts waking the thread, and ESPI/TP interrupt handlers being invoked only when present.

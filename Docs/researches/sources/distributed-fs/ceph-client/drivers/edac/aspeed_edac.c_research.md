# sources/distributed-fs/ceph-client/drivers/edac/aspeed_edac.c

## Purpose
This file implements an interrupt-driven EDAC memory-controller driver for Aspeed AST2400, AST2500, and AST2600 BMC SDRAM controllers. It reports recoverable and unrecoverable ECC events from the memory controller interrupt/status register and derives memory geometry from the device tree `/memory` node.

## Important APIs, Types, And Functions
The driver uses a global `struct regmap *aspeed_regmap` backed by custom `regmap_reg_read()` and `regmap_reg_write()` callbacks. Writes unlock the controller register set with `ASPEED_MCR_PROT_PASSWD`, write the target register, then lock it again. `regmap_is_volatile()` marks protection, interrupt, and error-address registers volatile.

Key functions are `aspeed_probe()`, `aspeed_remove()`, `config_irq()`, `mcr_isr()`, `count_rec()`, `count_un_rec()`, and `init_csrows()`. `count_rec()` reports all but the last recoverable error without address detail and reports the last recoverable address. `count_un_rec()` reports the first unrecoverable error with address detail and any additional unaddressed UEs.

## Control Flow
`aspeed_probe()` maps MCR registers, initializes the regmap, verifies that firmware configured ECC, sets `edac_op_state` to interrupt mode, allocates a chip-select/channel EDAC topology, fills controller capabilities, initializes csrow and DIMM metadata from `/memory` and `ASPEED_MCR_CONF`, registers the controller with EDAC, and finally requests/enables the IRQ. On interrupt, `mcr_isr()` reads `ASPEED_MCR_INTR_CTRL`, extracts recoverable and unrecoverable counters, reads the stored address registers, toggles the clear bit to clear flags/counters, and dispatches CE/UE reporting helpers.

## State And Persistence
The controller's address and count state is hardware-latched until the ISR clears it. The EDAC core stores per-DIMM and controller counters after `edac_mc_handle_error()` calls. The global regmap assumes one active Aspeed EDAC controller instance. DIMM geometry comes from the device tree memory resource and persists in `mci->csrows[0]` and its first DIMM.

## Dependencies And Integration Points
The driver depends on OF platform matching, memory-node parsing with `of_find_node_by_name()` and `of_address_to_resource()`, Linux regmap, interrupt registration, and EDAC MC APIs. It integrates with EDAC sysfs through `edac_mc_add_mc()` and with platform driver probing through `module_platform_driver()`.

## Risks
The global `aspeed_regmap` is simple but not multi-instance safe. The driver trusts firmware to have enabled ECC and returns `-EPERM` otherwise. Recoverable events only preserve the last address, while unrecoverable events only preserve the first address, so multi-error bursts necessarily lose per-event location detail. IRQ setup occurs after EDAC registration; probe error handling removes the controller if IRQ setup fails.

## Test Signals
Tests should confirm probe refusal when ECC is disabled, correct `/memory` sizing and first-page handling, IRQ handler counter extraction, clear-bit sequencing, and CE/UE count propagation in sysfs. Platform tests should verify AST2400/2500/2600 compatible strings and interrupt polarity/trigger behavior.

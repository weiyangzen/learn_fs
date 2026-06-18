# sources/distributed-fs/ceph-client/drivers/net/phy/qsemi.c

Purpose: Provides a legacy phylib driver for the Quality Semiconductor QS6612 PHY used on RPX CLLF hardware. It performs a required de-isolation/init write and supports PHY interrupt masking, acknowledgement, and handling.

Important APIs and functions: The `qs6612_driver[]` entry matches PHY ID `0x00181440` with mask `0xfffffff0` and supplies `qs6612_config_init()`, `qs6612_config_intr()`, and `qs6612_handle_interrupt()`. `qs6612_ack_interrupt()` performs the documented multi-register read sequence needed to clear latched interrupt sources.

Control flow: Config init writes `0x0dc0` to the 100BaseTx PHY control register to allow operation on boards where the PHY powers up isolated. Interrupt enable first acknowledges any stale interrupt, then writes `MII_QS6612_IMR_INIT` to the interrupt mask register. Interrupt disable clears the mask and acknowledges leftovers. The IRQ handler reads the interrupt source register, ignores unrelated sources, acknowledges active sources because the register is not self-clearing, and triggers the phylib state machine.

State and persistence: No driver-private state exists. Hardware state consists of QS6612 mode/control/interrupt registers. Interrupt status bits are latched in hardware and cleared by ordered reads of ISR, BMSR, and EXPANSION.

Dependencies and integration: Depends on phylib, MII register definitions, module PHY registration, and the MDIO device table for autoloading. The file includes older networking and architecture headers, but runtime integration is through standard `struct phy_driver` callbacks.

Risks and test signals: Risks include reliance on preliminary register values, wrong interrupt clear ordering, interrupt storms if ISR bits are left latched, and sparse hardware availability. Test probe by MDIO ID, config-init de-isolation, interrupt enable/disable, IRQ handling for masked and unmasked sources, and fallback polling behavior when interrupts are not enabled.

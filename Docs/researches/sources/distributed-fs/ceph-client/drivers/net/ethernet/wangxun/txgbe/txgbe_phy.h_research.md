# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_phy.h

Purpose: declares the TXGBE PHY-facing entry points shared by the PF driver. It is intentionally small and provides the public contract implemented by `txgbe_phy.c`.

Important APIs: `txgbe_link_irq_handler(int irq, void *data)` is the IRQ callback used by the TXGBE interrupt layer to notify phylink/XPCS of link changes. `txgbe_init_phy(struct txgbe *txgbe)` initializes the appropriate PHY path for the MAC/media type. `txgbe_remove_phy(struct txgbe *txgbe)` releases resources acquired by initialization.

Control flow and integration: the header assumes `struct txgbe` is already visible from `txgbe_type.h` or another include in consumers. The functions are consumed by the main TXGBE driver during probe, remove, and interrupt setup. It keeps phylink details hidden from the caller, allowing the source file to choose AML, external copper PHY, or SFP/XPCS behavior.

State and persistence: no state is defined here. State lives in `struct txgbe` and `struct wx`.

Risks and tests: because this is a narrow declaration header, risks are prototype drift and include-order assumptions. Build coverage with TXGBE enabled is the primary signal; runtime signals come from successful PHY init/remove and link IRQ dispatch in the implementation.

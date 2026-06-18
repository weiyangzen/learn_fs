# sources/distributed-fs/ceph-client/drivers/reset/reset-ma35d1.c

Purpose: Nuvoton MA35D1 reset controller for SoC peripheral reset bits plus chip restart.

Important APIs/types/functions: `struct ma35d1_reset_data`, `ma35d1_reset_map[]`, `ma35d1_restart_handler()`, `ma35d1_reset_update()`, assert/deassert/status ops, and `ma35d1_reset_probe()`.

Control flow: reset IDs index a static map of register offsets and bit positions. Probe maps the reset block, registers a restart handler that writes the chip reset bit, and registers the reset controller. Assert/deassert perform spinlocked read-modify-write; status reads the mapped bit.

State and persistence: reset registers are hardware state; spinlock protects concurrent RMW.

Dependencies and integration: built-in OF platform driver, dt-bindings reset IDs, sys-off restart, MMIO, reset framework.

Risks and test signals: map coverage must match `MA35D1_RESET_COUNT`; invalid IDs are guarded but should be unreachable through `nr_resets`. Test restart, representative peripheral resets, status reads, and DT node presence handling.

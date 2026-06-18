# sources/distributed-fs/ceph-client/drivers/reset/reset-ath79.c

Purpose: reset controller for Qualcomm Atheros AR71xx/ATH79 SoCs.

Important APIs/types/functions: `struct ath79_reset`, `ath79_reset_update()`, assert/deassert/status ops, `ath79_reset_restart_handler()`, and `ath79_reset_probe()`.

Control flow: probe maps one MMIO reset register, initializes a spinlock, registers 32 reset lines, and registers a restart handler. Assert sets the bit; deassert clears it; status reads the bit. Restart asserts bit 24 (`FULL_CHIP_RESET`).

State and persistence: reset register is hardware state; driver state is devm-managed except built-in lifetime. Spinlock protects read-modify-write updates.

Dependencies and integration: built-in platform driver for `qca,ar7100-reset`, reset framework, restart handler API, MMIO.

Risks and test signals: full-chip restart is hard to unit test and suppresses bind attributes. Test per-bit reset behavior, restart handler registration warnings, and boot on ATH79 defconfig.

# sources/distributed-fs/ceph-client/drivers/reset/reset-k230.c

Purpose: Canaan K230 reset controller covering CPU, flush, hardware-done, and software-done reset types with type-specific timing.

Important APIs/types/functions: `enum k230_rst_type`, `struct k230_rst_map`, `k230_resets[]`, `k230_rst_clear_done()`, `k230_rst_wait_and_clear_done()`, `k230_rst_update()`, assert/deassert/reset ops, and `k230_rst_probe()`.

Control flow: reset IDs index a static map with register offset, type, done bit, and reset bit. Assert/deassert are supported for CPU1 and SW_DONE types; CPU0, FLUSH, and HW_DONE use `.reset`. Done-capable paths clear done, request reset, poll completion, and clear done again. Delays cover maximum clock-stopped reset intervals.

State and persistence: hardware registers/done bits hold state; spinlock protects read-modify-write and write-enable bit updates.

Dependencies and integration: module platform driver, MMIO, polling, dt-bindings reset IDs, reset framework.

Risks and test signals: operation support depends on reset type; callers using unsupported assert/deassert get `-EOPNOTSUPP`. Test each reset type, done-bit timeouts, active-low SW_DONE exception for `RST_SPI2AXI`, and timing-sensitive hardware bring-up.

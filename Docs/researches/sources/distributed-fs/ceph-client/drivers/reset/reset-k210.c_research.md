# sources/distributed-fs/ceph-client/drivers/reset/reset-k210.c

Purpose: Canaan Kendryte K210 peripheral reset controller using the SYSCTL syscon.

Important APIs/types/functions: `struct k210_rst`, `K210_RST_MASK`, `k210_rst_assert()`, `k210_rst_deassert()`, `k210_rst_reset()`, `k210_rst_status()`, `k210_rst_xlate()`, and `k210_rst_probe()`.

Control flow: probe gets the parent syscon regmap and registers valid reset IDs. Xlate rejects IDs not present in `K210_RST_MASK`. Assert/deassert update `K210_SYSCTL_PERI_RESET`; reset asserts, waits 10 us, and deasserts.

State and persistence: hardware reset register holds state; driver stores regmap and controller metadata only.

Dependencies and integration: built-in OF platform driver, syscon/regmap, Canaan SYSCTL constants, reset framework.

Risks and test signals: `regmap_update_bits(..., BIT(id), 1)` writes value 1 rather than `BIT(id)`, so only bit 0 would receive a nonzero value if regmap does not mask-shift values internally. Test nonzero reset IDs, xlate mask rejection, and K210 peripheral reset behavior.

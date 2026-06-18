# sources/distributed-fs/ceph-client/drivers/reset/reset-pistachio.c

Purpose: Imagination Pistachio peripheral reset controller using a parent syscon soft-reset register.

Important APIs/types/functions: `struct pistachio_reset_data`, `pistachio_reset_shift()`, `pistachio_reset_assert()`, `pistachio_reset_deassert()`, and `pistachio_reset_probe()`.

Control flow: reset IDs are translated to non-linear bit positions by `pistachio_reset_shift()`. Probe obtains the parent regmap and registers resets up to `PISTACHIO_RESET_MAX + 1`. Assert sets the mapped bit in `PISTACHIO_SOFT_RESET`; deassert clears it.

State and persistence: parent syscon reset register holds state; driver caches regmap only.

Dependencies and integration: built-in OF platform driver, syscon/regmap, dt-bindings reset IDs, reset framework.

Risks and test signals: non-linear ID-to-bit mapping is the main maintenance risk, and invalid IDs return `-EINVAL`. Test every dt-binding ID, syscon parent lookup, and hardware peripheral recovery after reset.

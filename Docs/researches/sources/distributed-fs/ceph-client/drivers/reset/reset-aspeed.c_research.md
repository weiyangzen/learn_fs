# sources/distributed-fs/ceph-client/drivers/reset/reset-aspeed.c

Purpose: ASPEED AST2700 reset controller exposed as auxiliary devices from the clock/SCU provider.

Important APIs/types/functions: `struct ast2700_reset_signal`, `struct aspeed_reset_info`, `struct aspeed_reset`, `ast2700_reset0_signals[]`, `ast2700_reset1_signals[]`, `aspeed_reset_assert()`, `aspeed_reset_deassert()`, `aspeed_reset_status()`, and `aspeed_reset_probe()`.

Control flow: auxiliary IDs `clk_ast2700.reset0` and `.reset1` select reset signal tables. Probe uses platform data as the SCU base, sets one-cell reset translation, and registers. Most signals have dedicated set/clear registers: assert writes the bit to the base offset, deassert writes to offset+4. Non-dedicated signals use spinlocked read-modify-write.

State and persistence: register bits are hardware state; `spinlock_t lock` protects non-dedicated updates.

Dependencies and integration: auxiliary bus, dt-bindings reset IDs, MMIO, reset framework, and a parent clock/SCU driver that creates the auxiliary devices.

Risks and test signals: table holes or wrong `dedicated_clr` flags affect hardware. Test both reset domains, PCIE non-dedicated path, status polarity, and auxiliary platform data lifetime.

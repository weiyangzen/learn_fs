# sources/distributed-fs/ceph-client/drivers/clk/clk-gate.c

Purpose: generic common-clock gate implementation for clocks whose only hardware control is one register bit. It provides the reusable `clk_gate_ops` and registration/unregistration helpers used by many SoC drivers.

Important APIs, types, and functions: `struct clk_gate` is supplied by `<linux/clk-provider.h>`. `clk_gate_readl()` and `clk_gate_writel()` abstract normal vs big-endian MMIO. `clk_gate_endisable()` implements enable/disable writes, including `CLK_GATE_SET_TO_DISABLE` polarity and `CLK_GATE_HIWORD_MASK` write-mask semantics. Exported APIs include `clk_gate_is_enabled()`, `clk_gate_ops`, `__clk_hw_register_gate()`, `clk_register_gate()`, `clk_unregister_gate()`, `clk_hw_unregister_gate()`, and `__devm_clk_hw_register_gate()`.

Control flow: common clock core calls `.enable`, `.disable`, and `.is_enabled`. Registration builds `clk_init_data`, validates hiword bit indexes, allocates `struct clk_gate`, then registers either with `clk_hw_register()` or `of_clk_hw_register()` depending on the `dev`/`np` inputs. Devres registration wraps the raw registration and unregisters automatically through `devm_clk_hw_release_gate()`.

State and persistence: persistent state is the target MMIO bit and the allocated `clk_gate`; no disk or firmware state is stored. Optional spinlock serializes read-modify-write access. Hiword mode avoids read-modify-write by writing the mask in the upper halfword.

Dependencies and integration points: integrates with the Linux common clock framework, OF clock registration, device-managed resources, MMIO helpers, and optional caller-provided spinlocks. SoC drivers depend on it for simple gate leaves.

Risks and test signals: invalid hiword bit indexes are rejected, but callers must supply a valid mapped register and correct polarity flags. RMW mode can race with other fields unless a shared lock is passed. KUnit coverage is in `clk-gate_test.c` for registration, parent selection, normal/inverted gates, hiword writes, and `is_enabled()`.

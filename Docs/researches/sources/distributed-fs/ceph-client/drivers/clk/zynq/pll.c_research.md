# sources/distributed-fs/ceph-client/drivers/clk/zynq/pll.c

Purpose: implements a Xilinx Zynq-7000 PLL as a Linux common clock framework provider backed by memory-mapped PLL control and status registers.

Important APIs/types/functions: `struct zynq_pll` stores `clk_hw`, control/status register bases, a shared spinlock, and the lock-bit index. `clk_register_zynq_pll()` allocates and registers the clock. `zynq_pll_determine_rate()`, `zynq_pll_recalc_rate()`, `zynq_pll_enable()`, `zynq_pll_disable()`, and `zynq_pll_is_enabled()` form the `clk_ops`.

Control flow: registration clears the bypass qualifier bit under the caller-supplied lock, then calls `clk_register()`. Rate selection clamps feedback divider values to 13..66. Enable clears reset/powerdown and busy-waits for the PLL lock status bit; disable asserts reset and powerdown.

State and persistence: state lives in SoC registers and in the allocated `struct zynq_pll`; there is no teardown path in this file. Register access is serialized with the shared spinlock.

Dependencies and integration points: depends on CCF, `linux/clk/zynq.h`, MMIO helpers, and the parent Zynq clock controller that supplies mapped registers and lock. Consumers interact through normal clk APIs.

Risks: the enable path spins indefinitely if firmware or hardware never asserts the lock bit. Nested calls take and release the same lock only around individual reads, so callers must preserve the expected locking context. `pr_info()` on enable/disable can be noisy. `parent_rate * fbdiv` may overflow `unsigned long` on unusual inputs.

Test signals: boot on Zynq hardware, clock tree inspection, PLL rate changes near min/max dividers, lock-bit failure injection, and suspend/resume or peripheral enable tests that exercise gate users.

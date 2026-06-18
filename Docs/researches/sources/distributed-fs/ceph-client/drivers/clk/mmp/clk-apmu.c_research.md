# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-apmu.c

Purpose: This file implements simple AXI/APMU peripheral clock gates for Marvell MMP clocks controlled by enable bits in APMU registers.

Important APIs, types, and functions: The public constructor is `mmp_clk_register_apmu`. Internal state is `struct clk_apmu`, which stores `clk_hw`, MMIO base, reset mask, enable mask, and optional lock. `clk_apmu_ops` supplies `enable` and `disable` through `clk_apmu_enable` and `clk_apmu_disable`.

Control flow: Registration allocates the wrapper, fills a single-parent `clk_init_data` with `CLK_SET_RATE_PARENT`, records base and enable mask, and registers the clock. Enable reads the register, ORs `enable_mask`, and writes it back under the optional lock. Disable reads, clears `enable_mask`, and writes it back.

State and persistence behavior: Hardware register bits hold the persistent enable state. The allocated clock object stores only register metadata. The `rst_mask` field exists in the struct but is not used by this implementation.

Dependencies and integration points: It depends on MMP `clk.h`, CCF, MMIO accessors, and optional external spinlocks. SoC-specific MMP clock files use it for APMU-controlled clocks where no reset or sequencing is needed.

Risks and edge cases: Read-modify-write races are possible without a shared lock for registers containing multiple controls. Unused `rst_mask` can confuse future users expecting reset behavior. Test signals include enable/disable register traces, shared-register locking tests, and device functional tests for APMU-gated peripherals.

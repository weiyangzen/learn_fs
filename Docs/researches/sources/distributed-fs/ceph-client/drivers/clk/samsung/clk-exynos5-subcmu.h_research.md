## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5-subcmu.h

### Purpose
`clk-exynos5-subcmu.h` defines the small contract between Exynos5 SoC clock drivers and the shared sub-CMU runtime-PM helper in `clk-exynos5-subcmu.c`.

### Important APIs, Types, and Functions
`struct exynos5_subcmu_reg_dump` describes one masked register save/restore entry: `offset`, suspend `value`, bit `mask`, and runtime `save` storage. `struct exynos5_subcmu_info` describes one power-domain sub-CMU: divider clock array, gate clock array, suspend register dump array, and the power-domain `pd_name` label used to match a DT power domain. The header declares `exynos5_subcmus_init()`.

### Control Flow
The header has no executable control flow. SoC files instantiate `struct exynos5_subcmu_info` arrays and pass them to `exynos5_subcmus_init()` after main CMU clocks are registered. The implementation then defers gate lookups, creates platform devices for matching power domains, and registers the real sub-CMU clocks at runtime.

### State and Persistence Behavior
The `save` field in `struct exynos5_subcmu_reg_dump` is mutable state owned by the sub-CMU helper. The `value` and `mask` fields encode the low-power hardware policy, while `offset` ties that policy to the main clock-controller MMIO base. `struct exynos5_subcmu_info` instances are usually static data in SoC clock drivers, but their `suspend_regs` entries are modified at runtime.

### Dependencies and Integration Points
The header depends on type declarations from the Samsung clock framework, especially `struct samsung_clk_provider`, `struct samsung_div_clock`, and `struct samsung_gate_clock`, which are available because including C files include `clk.h` before this header. It integrates Exynos5250 and Exynos5420/5800 SoC-specific tables with the generic sub-CMU helper.

### Risks and Test Signals
The main risk is ABI-like coupling between table initializers and helper expectations: `pd_name` must match device-tree power-domain labels, register masks must not cover unrelated bits, and `suspend_regs` must be writable because `save` is updated. Build coverage catches missing type definitions and initializer drift. Runtime test signals come from the C helper: expected power-domain sub-CMU devices, deferred clock resolution, and suspend/resume register restoration.

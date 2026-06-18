## sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5260.h

### Purpose
`clk-exynos5260.h` defines Exynos5260 CMU register offsets used by `clk-exynos5260.c`. It is the hardware register map layer for AUD, DISP, EGL, FSYS, G2D, G3D, GSCL, ISP, KFC, MFC, MIF, PERI, and TOP clock management units.

### Important APIs, Types, and Functions
The header exports preprocessor constants only. Register groups follow a consistent naming scheme: `MUX_SEL_*`, `MUX_ENABLE_*`, `MUX_STAT_*`, `MUX_IGNORE_*`, `DIV_*`, `DIV_STAT_*`, `EN_ACLK_*`, `EN_PCLK_*`, `EN_SCLK_*`, `EN_IP_*`, PLL lock/control/frequency-detect registers, clockout registers, and a few domain-specific power/EMA/DDR controls such as `PWR_CTRL`, `ARMCLK_STOPCTRL`, `DREX_FREQ_CTRL`, and `DDRPHY_LOCK_CTRL`.

### Control Flow
There is no executable control flow. The C file includes this header and uses the offsets to build `clk_regs` save lists and mux/div/gate/PLL descriptors. The shared Samsung CCF implementation then performs actual MMIO operations using these offsets relative to each CMU node's mapped base.

### State and Persistence Behavior
The constants describe persistent hardware state, not software state. Offsets select registers that hold parent mux selections, enabled mux paths, divider ratios, divider status, secure and non-secure gate bits, PLL configuration, memory-controller timing controls, and clockout status. Because they are used in suspend save lists, any incorrect value can corrupt preservation of a whole CMU bank.

### Dependencies and Integration Points
The header is tightly coupled to `clk-exynos5260.c` and the Exynos5260 binding header. Its register names align with clock descriptor names and clock IDs used by device-tree consumers. The grouping also documents the hardware-domain boundaries that the device tree must represent as separate clock-controller nodes.

### Risks and Test Signals
Risks are mostly maintenance risks: wrong offsets compile cleanly but write the wrong hardware register, uppercase/lowercase inconsistency can invite duplicate definitions, and secure register groups are easy to confuse with ordinary gate groups. Build tests catch missing macro names, while runtime tests require domain-by-domain clock enable, rate changes, and suspend/resume. `clk_summary` plus functional tests for display, audio, FSYS, media, CPU, GPU, and memory interface are the practical signals that the register map is coherent.

# sources/distributed-fs/ceph-client/drivers/bcma/core.c

Purpose: this file implements low-level BCMA core operations for reset, enable/disable, clock mode, PLL resource requests, and DMA translation.

Important APIs, types, and functions: exported functions are `bcma_core_is_enabled`, `bcma_core_disable`, `bcma_core_enable`, `bcma_core_set_clockmode`, `bcma_core_pll_ctl`, and `bcma_core_dma_translation`. Internal `bcma_core_wait_value` polls a DMP register until masked bits match a target or timeout.

Control flow: enable first disables the core with requested flags, then writes IO control with clock and force-gated clock, clears reset, and finally leaves clock plus flags enabled. Disable waits for reset status to clear, asserts reset, then writes IO control flags. Clock mode FAST sets `FORCEHT` and waits up to roughly 15 ms for `HAVEHT`; DYNAMIC clears the force bit. PLL control sets or clears external resource request bits and waits for status when enabling.

State and persistence: state is in hardware registers (`BCMA_IOCTL`, `BCMA_RESET_CTL`, `BCMA_RESET_ST`, `BCMA_CLKCTLST`, `BCMA_IOST`). No heap state is owned here. `core->irq` is not changed in this file.

Dependencies and integration points: it depends on public BCMA accessors (`bcma_aread32`, `bcma_awrite32`, `bcma_read32`, masks/set helpers), jiffies timing, udelay/usleep, and host type information. Higher-level BCMA drivers call these helpers before touching core-specific registers.

Risks: polling timeouts indicate hardware readiness failures; wrong delays or flag values can leave cores reset, clock-gated, or over-requesting PLL resources. DMA translation depends on host type and `BCMA_IOST_DMA64`; unsupported host types log an error and return none.

Test signals: hardware bring-up logs, core enable state checks, DMA-capable device operation, and timeout warnings are primary signals. Unit-style tests would need mocked register access.

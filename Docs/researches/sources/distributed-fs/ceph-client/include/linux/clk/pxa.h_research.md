# sources/distributed-fs/ceph-client/include/linux/clk/pxa.h

Purpose: This header declares PXA clock initialization and PXA3xx frequency/ACCR update helpers.

Important APIs/types/functions: APIs are `pxa25x_clocks_init`, `pxa27x_clocks_init`, `pxa3xx_clocks_init`, `pxa3xx_get_clk_frequency_khz`, and `pxa3xx_clk_update_accr`. For non-`CONFIG_PXA3xx`, the latter two are macros returning `0` or doing nothing.

Control flow: Early PXA platform code passes mapped clock-register bases to the init functions. PXA3xx-specific code can query clock frequency in kHz and update ACCR bits through disable/enable/xclkcfg/mask arguments.

State and persistence behavior: State is in PXA clock registers and the CCF registrations created by the implementation. Non-PXA3xx builds intentionally compile out dynamic PXA3xx operations.

Dependencies and integration points: It includes compiler and type headers and integrates with ARM PXA board init, CCF registration, and SoC-specific power/clock code.

Risks: These APIs take raw `void __iomem *` register bases, so incorrect mapping is high impact. Stubbed PXA3xx helpers can hide code paths that should be conditional on `CONFIG_PXA3xx`.

Test signals: PXA25x/PXA27x/PXA3xx boot tests, rate readouts, ACCR register readback, and peripheral probe coverage validate the header contract.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.h

Purpose: PXA2xx MFP encoding helpers and common GPIO pin macros.

Important APIs/macros: defines PXA2xx-specific direction bit, wakeup bit, keep-output bit, wake edge aliases, `MFP_CFG_IN()`, `MFP_CFG_OUT()`, and common `GPIOx_GPIO` input configs. Declares `pxa2xx_mfp_config()`, `pxa2xx_mfp_set_lpm()`, and `gpio_set_wake()`.

Control flow and integration: PXA25x/PXA27x pin headers build on these macros; board files submit generated values to `mfp-pxa2xx.c`.

State and persistence: header only; encoded values drive persistent hardware register programming when applied.

Dependencies: includes generic PXA MFP definitions from `linux/soc/pxa/mfp.h`.

Risks and test signals: output pins must specify safe low-power state; misuse can increase power or cause bus contention. Compile all board pin arrays and test suspend pin levels on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.h -->

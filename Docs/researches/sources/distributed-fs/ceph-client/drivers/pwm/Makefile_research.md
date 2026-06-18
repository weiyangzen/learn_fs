# sources/distributed-fs/ceph-client/drivers/pwm/Makefile

Purpose: maps PWM Kconfig symbols to Kbuild objects for the generic PWM core and all controller drivers in `drivers/pwm`.

Important APIs/types/functions: `obj-$(CONFIG_PWM) += core.o` builds the framework core. Per-driver entries map symbols such as `CONFIG_PWM_AB8500`, `CONFIG_PWM_AXI_PWMGEN`, `CONFIG_PWM_DWC_CORE`, `CONFIG_PWM_DWC`, and `CONFIG_PWM_EP93XX` to their corresponding `.o` files. The file also includes newer entries such as `pwm_th1520.o`.

Control flow: there is no runtime flow. Kbuild evaluates each `obj-$(CONFIG_...)` assignment after Kconfig resolution and compiles/link-selects objects or modules.

State and persistence: state is build output only. This file does not own runtime data and does not persist configuration beyond the generated build graph.

Dependencies and integration: integrates with the adjacent `Kconfig`; every object here assumes its dependency set is sufficient. Shared-core split drivers rely on correct object selection, for example `PWM_DWC` selecting and building `pwm-dwc-core.o`.

Risks and test signals: object-name drift, missing new driver entries, stale entries, or mismatches with Kconfig module names cause compile or link failures. Test signals are clean builds for modular and built-in PWM configurations, plus targeted builds of split drivers like DWC and LPSS.

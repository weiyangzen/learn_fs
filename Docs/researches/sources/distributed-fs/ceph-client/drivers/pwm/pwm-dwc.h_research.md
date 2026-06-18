# sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.h

Purpose: defines the shared register map, data structures, inline MMIO helpers, and allocator prototype for Synopsys DesignWare PWM support.

Important APIs/types/functions: register macros cover load count, current value, control, interrupt, EOI, and component version offsets. Control bits define enable, free/user mode, interrupt mask, and PWM mode. `struct dwc_pwm_info`, `struct dwc_pwm_drvdata`, `struct dwc_pwm_ctx`, and `struct dwc_pwm` form the shared frontend/core contract. `to_dwc_pwm()`, `dwc_pwm_readl()`, and `dwc_pwm_writel()` are inline helpers; `dwc_pwm_alloc()` is declared for frontends.

Control flow: no runtime flow occurs in the header. It is included by both the shared core and bus frontend so they agree on register offsets and state layout.

State and persistence: declares context storage for suspend/resume snapshots and per-controller MMIO base/clock period. Actual allocation and persistence are handled by C files.

Dependencies and integration: imports namespace `dwc_pwm` and assumes Linux bitops/MMIO definitions are already available through including files. It is the internal ABI between `pwm-dwc-core.c` and `pwm-dwc.c`.

Risks and test signals: offset macros encode hardware layout; mistakes break every frontend. `DWC_TIM_LD_CNT2` lives in a separate register range, so channel indexing should be tested for all eight timers. Test signals include compile coverage of both C files, namespace import/export checks, suspend context arrays sized to `DWC_TIMERS_TOTAL`, and register write/read smoke tests.

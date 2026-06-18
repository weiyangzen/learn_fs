# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/ic_pll_regs.h

Purpose: auto-generated register-address map for the Goya IC PLL block, an instance of the generic `PLL` prototype controlling interconnect clock generation/division/stability monitoring.

Important APIs/types/functions: no functions or types. The `mmIC_PLL_*` macros cover PLL numerator/frequency/output-divide/bypass configuration (`NR`, `NF`, `OD`, `NB`, `CFG`), loss/lock interrupt and bypass registers, data-change and reset controls, slip watchdog counter, four divider factor/command/select/enable/busy channels, clock gater and relax registers, reference counter period/threshold registers, `PLL_NOT_STABLE`, and frequency calculation enable.

Control flow: declarative. Clock-management code writes factor/divider/reset/config registers, issues divider factor commands, waits for busy/lock/stability status, and configures reference threshold monitoring. This header only supplies addresses.

State and persistence: PLL configuration and divider state live in hardware registers and persist until reset or reprogramming. Lock/stability/busy registers report live hardware state. `goya_blocks.h` maps the block base as `mmIC_PLL_BASE`.

Dependencies and integration: included by `goya_regs.h` together with other PLL headers. It shares the same `PLL` layout as `mc_pll_regs.h`, `cpu_pll_regs.h`, and `tpc_pll_regs.h`, so common PLL-management code can use consistent naming patterns.

Risks: clock programming is high impact. Wrong addresses can destabilize the interconnect, hang MMIO, or cause timing-related data corruption. Divider command/busy sequencing must be respected by caller code; this header does not enforce ordering.

Test signals: clock initialization, PLL lock interrupts/status, divider factor readback, frequency calculation/stability status, suspend/resume or reset clock reprogramming, and stress tests under interconnect load.

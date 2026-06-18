# sources/distributed-fs/ceph-client/include/soc/imx/cpuidle.h

Purpose: declares i.MX6Q CPU-idle hooks used by FEC/networking paths to indicate whether Ethernet IRQs are in use.

Important APIs and types: when both `CONFIG_CPU_IDLE` and `CONFIG_SOC_IMX6Q` are enabled, `imx6q_cpuidle_fec_irqs_used()` and `imx6q_cpuidle_fec_irqs_unused()` are external functions. Otherwise they compile to no-op inline stubs.

Control flow: FEC or platform code calls the hooks when Ethernet IRQ usage changes so the i.MX6Q cpuidle implementation can avoid low-power states that would break wake/interrupt behavior.

State and persistence: state is maintained by the cpuidle implementation, likely runtime counters/flags. The header stores none.

Dependencies and integration points: integrates i.MX6Q cpuidle with FEC/network drivers while allowing builds without CPU idle or i.MX6Q support.

Risks and test signals: risks include unbalanced used/unused calls, no-op stubs hiding missing power constraints on unsupported configs, and regressions in wake from Ethernet. Test FEC open/close, suspend/idle with active Ethernet IRQs, disabled-config builds, and repeated interface up/down.

# sources/distributed-fs/ceph-client/include/linux/platform_data/cpuidle-exynos.h

Purpose: defines Exynos cpuidle platform callbacks for entering and bracketing AFTR/CPU powerdown low-power states.

Important APIs and types: `struct cpuidle_exynos_data` contains callbacks `cpu0_enter_aftr()`, `cpu1_powerdown()`, `pre_enter_aftr()`, and `post_enter_aftr()`.

Control flow: Exynos cpuidle code calls pre-enter hook, invokes CPU0 AFTR entry or CPU1 powerdown as appropriate, then calls post-enter hook on return to restore platform state.

State and persistence: the callbacks manipulate SoC PM registers and CPU state externally; this header stores no state. Low-power transitions are runtime-only.

Dependencies and integration points: integrates Exynos platform PM code, cpuidle driver, CPU hotplug/secondary CPU powerdown paths, and AFTR suspend-like state handling.

Risks and test signals: risks include callback NULL handling, failed entry leaving pre-enter state active, CPU1 powerdown coordination races, and lost wakeup state. Test idle state entry/exit, wake interrupts, CPU0/CPU1 paths, cpuidle disable/enable, and suspend/resume interactions.

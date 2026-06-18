<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Makefile -->
# sources/distributed-fs/ceph-client/kernel/power/Makefile

Purpose: Selects kernel power-management object files based on Kconfig symbols and applies debug/KASAN build flags for specific power objects.

Important APIs/types/functions: Build targets include always-built `qos.o`; conditional `main.o`, `console.o`, `process.o`, `suspend.o`, `suspend_test.o`, `hibernate.o`, `snapshot.o`, `swap.o`, `user.o`, `autosleep.o`, `wakelock.o`, `poweroff.o`, and energy-model composite `em.o`. `em-y` contains `energy_model.o`; `em-$(CONFIG_NET)` adds `em_netlink_autogen.o` and `em_netlink.o`.

Control flow: `CONFIG_DYNAMIC_DEBUG=y` adds `-DDEBUG` to `swap.o`, `snapshot.o`, and `energy_model.o`. `KASAN_SANITIZE_snapshot.o := n` disables KASAN for snapshot code. Object inclusion follows the Kconfig PM matrix, while `CONFIG_ENERGY_MODEL` builds `em.o` and optionally includes netlink support only with networking.

State and persistence: No runtime state; this file persists build graph decisions. Composite object membership affects which symbols and initcalls appear in the final kernel.

Dependencies/integration: Consumes symbols from `kernel/power/Kconfig` and connects Energy Model core to optional generic netlink support. Integrates with Kbuild composite object syntax and sanitizer/debug flag plumbing.

Risks: Misaligned Kconfig/Makefile conditions can silently omit runtime features or include code without dependencies. Energy Model netlink functions are compiled only when both `ENERGY_MODEL` and `NET` are set, matching header stubs. Disabling KASAN for snapshot is deliberate and should not be broadened casually.

Test signals: Build matrix checks for `CONFIG_PM`, `CONFIG_SUSPEND`, `CONFIG_HIBERNATION`, `CONFIG_PM_AUTOSLEEP`, `CONFIG_PM_WAKELOCKS`, `CONFIG_MAGIC_SYSRQ`, `CONFIG_ENERGY_MODEL`, and `CONFIG_NET`; verify `em.o` composition and dynamic debug flags in verbose builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Makefile -->

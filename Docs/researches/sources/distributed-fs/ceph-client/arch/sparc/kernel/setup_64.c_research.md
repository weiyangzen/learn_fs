# sources/distributed-fs/ceph-client/arch/sparc/kernel/setup_64.c

Purpose: performs SPARC64 early boot and architecture setup: PROM console/boot arguments, boot switches, runtime instruction patching for CPU/hypervisor features, sun4v hypervisor setup, hardware capability reporting, root/initrd/IP autoconfig setup, trap-block initialization, paging, and IRQ stack allocation.

Important APIs/functions: entry points include `start_early_boot()`, `setup_arch()`, `cpucap_info()`, and `sun_do_break()`. Patch helpers are `per_cpu_patch()`, `sun4v_patch_1insn_range()`, `sun4v_patch_2insn_range()`, `sun_m7_patch_2insn_range()`, `sun4v_patch()`, `popc_patch()`, and `pause_patch()`. HWCAP helpers include `mdesc_cpu_hwcap_list()`, `init_sparc64_elf_hwcap()`, and reporting functions.

Control flow: `start_early_boot()` checks Starfire, applies CPU/sun4v patches, initializes CPU poke support, records boot CPU ID, initializes early time, reports PROM, and calls `start_kernel()`. `setup_arch()` reads boot args, parses early params, processes SPARC switches (`-h`, `-p`, `-P`, etc.), optionally registers early PROM console, logs SUN4U/SUN4V, initializes IDPROM/root/initrd/IP-PNP state, initializes the boot CPU trap block, runs paging, computes ELF hardware capabilities from TLB type, sun4v chip type, and MDESC `hwcap-list`, applies popc/pause patches when supported, then allocates per-CPU hardirq and softirq stacks.

State and persistence: initializes runtime globals including `cmdline_memory_size`, `reboot_command`, `sparc64_elf_hwcap`, `stop_a_enabled`, early console flags, root device flags, IRQ stacks, and CPU trap state. HWCAPs become user ABI through ELF auxiliary vectors and `/proc/cpuinfo`.

Dependencies and integration points: depends on PROM, machine description APIs, sun4v hypervisor API init, Starfire, SMP CPU IDs, trap blocks, paging/MMU context, early console, IP autoconfig, memblock, ELF HWCAP definitions, and patch sections emitted by assembly.

Risks: runtime patching writes executable instructions and must flush each patched address. HWCAP bits are user ABI and must reflect real instruction availability. `-P` forcing P-cache taints the kernel and applies only to Cheetah. IRQ stack allocation must happen after possible CPUs are known.

Test signals: boot on sun4u and sun4v chip families, `mem=` and boot switch behavior, HWCAP output and auxv values, MDESC-based capability discovery, popc/pause/sun4v/M7 patch activation, IP-PNP PROM properties, IRQ stack allocation on all possible CPUs, and STOP-A handling.

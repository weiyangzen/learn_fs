# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pmc.c

Purpose: Installs the LEON CPU idle power-down handler, with board-specific fixups for systems that require an extra non-cacheable access around the sleep instruction.

Important APIs/types/functions: `pmc_leon_need_fixup()` compares the high half of `amba_system_id` against `pmc_leon_fixup_ids`. `pmc_leon_idle_fixup()` enables IRQs, writes `%asr19` to enter sleep, reads the IRQ controller using the LEON bypass ASI, then disables IRQs. `pmc_leon_idle()` uses only the sleep write. `leon_pmc_install()` assigns `sparc_idle` on LEON systems.

Control flow: A late initcall checks `sparc_cpu_model`, selects the fixup or normal idle callback, and logs initialization. The idle callback must temporarily enable interrupts so the CPU can wake.

State and persistence: It mutates only the global `sparc_idle` function pointer and live CPU interrupt state. Board matching depends on `amba_system_id` discovered earlier by LEON platform initialization.

Dependencies and integration points: It depends on LEON AMBA IDs, CPU model detection, IRQ controller register pointer, raw IRQ enable/disable, ASI bypass loads, and SPARC process idle infrastructure.

Risks and test signals: Running sleep with interrupts disabled can hang the CPU. The fixup path assumes IRQMP is mapped and non-cacheable through bypass ASI. Tests include idle entry/wakeup on listed and unlisted LEON systems, late init ordering after AMBA system ID discovery, and CPU hot/idle stress.

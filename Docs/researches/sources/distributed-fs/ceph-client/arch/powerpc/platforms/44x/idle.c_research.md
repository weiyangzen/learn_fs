<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/idle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/idle.c

Purpose: installs a simple PPC44x wait-mode idle loop unless booted with `idle=spin`.

Important APIs/types/functions: `ppc44x_idle()` saves MSR, sets wait-enable plus interrupt/debug/critical enable bits, executes `isync`, then restores MSR; `ppc44x_idle_init()` assigns `ppc_md.power_save`; `idle_param()` handles early `idle=spin`.

Control flow: early parameter parsing can set `mode_spin` and clear `ppc_md.power_save`. At arch init, if spin mode is not requested, the machine power-save hook is set to the wait loop. Runtime idle enters hardware wait and returns on interrupt.

State and persistence: static `mode_spin` stores boot policy; `ppc_md.power_save` persists as the architecture idle hook. Hardware MSR state is temporarily modified and restored each idle entry.

Dependencies and integration: used only when `CONFIG_PPC4xx_CPM` is not selected, because CPM has its own idle support. Depends on PowerPC MSR bits and generic idle paths calling `ppc_md.power_save`.

Risks and test signals: enabling the wrong MSR bits can affect interrupt delivery or debug behavior; CPM and simple idle are mutually exclusive in the Makefile. Test default idle, `idle=spin`, interrupt wakeups, and power-save hook selection on 44x boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/idle.c -->

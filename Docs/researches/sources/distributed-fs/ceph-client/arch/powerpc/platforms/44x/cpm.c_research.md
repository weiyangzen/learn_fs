<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/cpm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/cpm.c

Purpose: implements PPC4xx Clock and Power Management support for idle wait/doze modes, standby/mem suspend entry, sysfs idle-mode selection, and DCR-based power gating of unused units.

Important APIs/types/functions: `struct cpm` stores mapped DCR host, register offsets, masks, and feature flags; `cpm_set()` sets CPM enable/freeze/status bits; `cpm_idle_wait()`, `cpm_idle_sleep()`, and `cpm_idle_doze()` enter low-power states; `cpm_idle_show()`/`cpm_idle_store()` expose `/sys/devices/system/cpu/cpu0/idle`; `cpm_suspend_valid()` and `cpm_suspend_enter()` implement `platform_suspend_ops`; `cpm_init()` parses the `ibm,cpm` OF node.

Control flow: the `powersave=off` setup parameter disables power-save installation. Late init sets the default `ppc_md.power_save` hook, finds and maps the CPM DCR range, decides register order from `er-offset`, reads masks from OF properties, gates unused units, creates sysfs when doze is available, and registers suspend ops when standby or suspend masks exist. Runtime idle either executes wait or sets CPM masks around wait; suspend disables decrementer interrupts while sleeping.

State and persistence: global `cpm` holds DCR mapping and masks; `idle_mode[]` persists the selected idle policy; hardware CPM registers persist power-gating requests. Sysfs mutates only the idle-mode selection.

Dependencies and integration: depends on OF DCR resources/properties, native DCR access, `ppc_md.power_save`, CPU sysfs, Linux suspend core, MSR wait-enable bits, and decrementer TCR handling.

Risks and test signals: CPM register order detection treats missing `er-offset` as one layout; sysfs string matching uses input length and may accept prefixes; suspend masks are board-provided and can power down necessary units. Test idle wait/doze transitions, `powersave=off`, sysfs mode switching, standby/mem suspend resume, DCR property variants, and unused-unit gating on boards with CPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/cpm.c -->

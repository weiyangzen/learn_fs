<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-rtas.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-rtas.c

Purpose: Implements the RTAS-backed XICS Interrupt Source Controller backend for pSeries-style firmware.

Important APIs/types/functions: Entry point is `ics_rtas_init()`. IRQ chip callbacks are `ics_rtas_startup()`, `ics_rtas_mask_irq()`, `ics_rtas_unmask_irq()`, and `ics_rtas_set_affinity()`. Source-controller callbacks include `ics_rtas_check()`, `ics_rtas_mask_unknown()`, `ics_rtas_get_server()`, and `ics_rtas_host_match()`.

Control flow: Init obtains RTAS tokens for `ibm,get-xive`, `ibm,set-xive`, `ibm,int-on`, and `ibm,int-off`, patches EOI from `icp_ops`, and registers the global ICS if required tokens exist. Unmask sets server/default priority with RTAS, then enables the interrupt. Mask disables the interrupt and sets priority `0xff`. Affinity gets current XIVE, computes a target server, and updates only the server while preserving priority. Check probes firmware awareness with `ibm,get-xive`.

State and persistence: Persistent state is RTAS token integers, global `ics_rtas`, and firmware-maintained XIVE server/priority/on-off state.

Dependencies and integration points: Depends on RTAS services, XICS common type/retrigger/affinity helpers, ICP EOI callback, and OF host matching that excludes legacy `chrp,iic`.

Risks: `ibm_int_on/off` tokens are not checked for unknown service even though used. RTAS calls can fail at runtime and only log errors. Host matching intentionally matches almost everything except legacy i8259, which must stay compatible with pseries device-tree conventions.

Test signals: pSeries RTAS XICS boot, interrupt mask/unmask and affinity calls, missing RTAS token fallback, legacy i8259 exclusion, unknown interrupt masking, and CPU hotplug migration.

Source read size: 225 lines, 5538 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-rtas.c -->

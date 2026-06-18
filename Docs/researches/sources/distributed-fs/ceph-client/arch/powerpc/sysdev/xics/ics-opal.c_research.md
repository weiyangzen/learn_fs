<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-opal.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-opal.c

Purpose: Implements an OPAL-managed XICS Interrupt Source Controller backend.

Important APIs/types/functions: Entry point is `ics_opal_init()`. IRQ callbacks are `ics_opal_startup()`, `ics_opal_mask_irq()`, `ics_opal_unmask_irq()`, and `ics_opal_set_affinity()`. Source-controller callbacks are `ics_opal_check()`, `ics_opal_mask_unknown()`, `ics_opal_get_server()`, and `ics_opal_host_match()`.

Control flow: Init checks OPAL firmware, patches EOI from `icp_ops`, and registers a single global ICS. Unmask chooses an XICS server, mangles it by left-shifting for OPAL link encoding, and calls `opal_set_xive()` with default priority. Mask sets priority to `0xff`. Affinity reads the existing XIVE priority, computes a new server, and writes it back. Check and get_server call `opal_get_xive()`.

State and persistence: Persistent state is the global `ics_hal` struct and OPAL XIVE server/priority state for each hardware IRQ.

Dependencies and integration points: Depends on OPAL firmware calls, XICS common affinity/type/retrigger helpers, ICP EOI callback, and PowerNV firmware feature detection.

Risks: `ics_opal_host_match()` matches all nodes, so this backend claims broad interrupt-parent space once registered. Server mangling currently assumes no link. OPAL call failures are logged but often only return failure to generic IRQ code.

Test signals: PowerNV OPAL XICS interrupt delivery, affinity migration, mask/unmask, unknown-vector mask, OPAL get/set error handling, and MSI/device interrupts using OPAL XIVE state.

Source read size: 221 lines, 5178 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-opal.c -->

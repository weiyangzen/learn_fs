<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-native.c

Purpose: Implements a native MMIO XICS Interrupt Source Controller backend for `openpower,xics-sources`.

Important APIs/types/functions: Entry point is `ics_native_init()`. Main callbacks are `ics_native_startup()`, `ics_native_mask_irq()`, `ics_native_unmask_irq()`, `ics_native_set_affinity()`, `ics_native_check()`, `ics_native_mask_unknown()`, `ics_native_get_server()`, and `ics_native_host_match()`. Private state is `struct ics_native`.

Control flow: Init patches the irq chip EOI from `icp_ops`, scans compatible nodes, maps each source controller, reads `interrupt-ranges`, records base/count, and registers the first ICS with common XICS. Unmask computes a target server with `xics_get_irq_server()` and writes server/priority into the XIVE word. Mask writes priority `0xff`. Startup also unmasks PCI MSI at the generic MSI layer when present.

State and persistence: Persistent state includes mapped XIVE table base, OF node reference, interrupt base/count, registered `struct ics`, and XIVE register contents for server/priority.

Dependencies and integration points: Depends on XICS common ICP EOI, OF address and `interrupt-ranges`, PCI MSI mask helpers, irq affinity, and big-endian MMIO.

Risks: Only one interrupt range is supported; extra ranges are warned and ignored. Only one global ICS can be registered by common code, so multiple source controllers are limited. Out-of-range operations silently return in mask/unmask but fail in check/affinity.

Test signals: Native OpenPOWER XICS source delivery, interrupt-range parsing, PCI MSI startup unmask, affinity changes, unknown-vector masking, and multiple-source-controller DT behavior.

Source read size: 254 lines, 6156 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-native.c -->

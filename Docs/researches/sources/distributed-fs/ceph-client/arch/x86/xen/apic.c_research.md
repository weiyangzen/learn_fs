# sources/distributed-fs/ceph-client/arch/x86/xen/apic.c

Purpose: Provides Xen PV APIC and IO-APIC operation shims so the native x86 APIC framework can run in a PV guest where real APIC register access is replaced by Xen hypercalls or emulation.

Important APIs/types/functions: `xen_io_apic_read()` uses `PHYSDEVOP_apic_read` and falls back to emulated register values. `xen_apic_read()` synthesizes LVR/APIC ID and queries Dom0 CPU info when needed. `xen_apic_write()`, `xen_apic_eoi()`, and ICR helpers warn on unexpected native-style accesses, with LVTPC redirected to PMU support. `xen_pv_apic` is registered through `apic_driver()`, and `xen_init_apic()` installs Xen IO-APIC read ops.

Control flow and state: During PV boot, APIC probing succeeds only for Xen PV domains. Reads synthesize enough APIC identity/version state for x86 code and route Dom0 APIC IDs through platform ops. SMP IPI callbacks are wired to Xen send-IPI helpers. The file maintains no private mutable state.

Dependencies and integration points: It depends on APIC/IO-APIC core structures, Xen physdev/platform hypercalls, CPU topology, PMU APIC update hooks, and Xen domain predicates from `xen-ops.h`.

Risks and test signals: Unexpected native APIC writes indicate missing PV interception. Wrong APIC ID synthesis can break SMP topology, interrupt routing, or Dom0 CPU mapping. Signals include Xen PV SMP boot, IPI delivery, Dom0 platform CPU info, PMU LVTPC updates, and absence of WARNs for normal APIC paths.

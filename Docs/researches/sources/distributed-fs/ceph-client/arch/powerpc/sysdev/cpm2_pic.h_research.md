<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.h

Purpose: small public header for CPM2 interrupt-controller setup and dispatch.

Important APIs/types/functions: declarations for `cpm2_get_irq()` and `cpm2_pic_init(struct device_node *)`.

Control flow: no executable logic; platforms include this header to initialize the CPM2 PIC and retrieve pending IRQs.

State and persistence: no state. It exposes access to state owned by `cpm2_pic.c`.

Dependencies and integration points: depends on `struct device_node` from the OF subsystem. Integrated by CPM2 platform setup code.

Risks: minimal; mismatch between prototypes and implementation would break platform builds.

Test signals: compile coverage for CPM2 platforms and successful platform interrupt dispatch through these declarations validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2_pic.h -->

# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_irq.h

Purpose: UV-specific IRQ route entry layout and setup/teardown declarations.

Important APIs/types/functions: `struct uv_IO_APIC_route_entry`, affinity enum values `UV_AFFINITY_ALL`, `UV_AFFINITY_NODE`, `UV_AFFINITY_CPU`, `uv_setup_irq()`, and `uv_teardown_irq()`.

Control flow: implementation code uses the route-entry bitfield to program UV IO-APIC style destinations and uses affinity mode to target all CPUs, a node, or a specific CPU. Teardown releases the IRQ by number.

State/persistence: no state in the header. Runtime IRQ state is owned by the UV IRQ implementation and generic IRQ core.

Dependencies/integration: integrated with UV hub interrupt routing, IO-APIC semantics, Linux IRQ allocation, and platform device drivers needing UV affinity.

Risks/test signals: bitfield layout and destination semantics must match hardware. Test UV IRQ setup for all affinity modes, interrupt delivery under CPU/node hotplug, teardown leak checks, and route-entry programming against firmware/hardware documentation.

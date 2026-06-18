# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmzone.h

Purpose: provides PA-RISC NUMA/mmzone integration stubs.

Important APIs/types/functions: includes or defines minimal zone/node helpers required by generic memory management for PA-RISC configurations.

Control flow: generic page allocator code includes this header while computing zones and nodes; PA-RISC mostly relies on generic behavior here.

State and persistence: no private state; memory zones live in generic mm structures. Dependencies and integration: page allocator, sparsemem, and NUMA configuration.

Risks and test signals: low risk unless PA-RISC memory topology changes. Test with memory hotplug/sparsemem build coverage and boot memory maps.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.

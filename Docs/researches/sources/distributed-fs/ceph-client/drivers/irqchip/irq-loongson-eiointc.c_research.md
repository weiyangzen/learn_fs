<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-eiointc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-eiointc.c

## Purpose
Implements the Loongson Extended I/O Interrupt Controller, a 128/256-vector interrupt controller with CPU/node routing, virtualization support, ACPI/OF initialization, and cascaded PCH PIC/MSI setup.

## Important APIs, Types, And Functions
`struct eiointc_priv` stores node identity, vector count, node and CPU span masks, fwnode/domain, flags, parent hwirq, and per-route dispatch metadata. Key functions are `eiointc_init()`, `eiointc_router_init()`, `eiointc_irq_dispatch()`, `eiointc_domain_alloc()`, `eiointc_set_irq_affinity()`, `eiointc_acpi_init()`, `eiointc_of_init()`, and ACPI cascade parsers for PCH PIC/MSI.

## Control Flow
Initialization builds node and CPU span masks from MADT node maps or all possible CPUs, creates a linear domain for the vector count, detects KVM virtual EXTIOI CPU-encode support, stores the instance globally, optionally enables multi-IP routing, chains the parent CPU interrupt(s), programs routing and enable registers through `eiointc_router_init(0)`, and registers syscore/cpuhotplug callbacks on the first PIC. Dispatch reads ISR register ranges assigned to the parent IP, clears pending bits, and forwards vectors through the domain.

## State And Persistence
Global `eiointc_priv[]` and `nr_pics` persist all instances. Hardware state includes nodemap, IP map, route, enable, and bounce registers. Syscore resume re-runs router initialization. SMP affinity updates mask a vector, rewrite CPU/node route, then unmask it; virtual CPU-encode mode uses a different route register format.

## Dependencies And Integration Points
It depends on LoongArch IOCSR/CSR helpers, KVM paravirtual feature detection, CPU topology constants, cpuhotplug, syscore ops, ACPI MADT EIO/BIO/MSI records, OF compatibles `loongson,ls2k0500-eiointc` and `loongson,ls2k2000-eiointc`, and downstream PCH PIC/MSI initialization from `irq-loongson.h`.

## Risks
Routing is complex across physical nodes, virtual EXTIOI, CPU encode, and multi-IP hypervisor mode. Incorrect node maps can make `eiointc_index()` fail on CPU hotplug. The code assumes vector counts divisible by register sizes and route groups. Affinity updates must preserve masking around route changes to avoid delivery to stale CPUs.

## Test Signals
Test OF LS2K0500 with 128 vectors and LS2K2000 with 256 vectors, ACPI multi-node EIO PICs, CPU hotplug router reinit, interrupt affinity changes, virtual EXTIOI CPU-encode guests, multi-IP hypervisor routing, PCH PIC/MSI cascade initialization, syscore resume, and spurious dispatch when ISR ranges are empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-eiointc.c -->

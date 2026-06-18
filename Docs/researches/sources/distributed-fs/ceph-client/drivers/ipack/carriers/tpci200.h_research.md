# sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.h

Purpose: Defines TPCI200 hardware constants, BAR layout, register structures, interrupt/status bits, and private carrier data structures used by `tpci200.c`.

Important APIs/types/functions: `struct tpci200_regs`, `struct slot_irq`, `struct tpci200_slot`, `struct tpci200_infos`, `struct tpci200_board`, BAR constants, slot region offsets/sizes, control bits, status bits, PCI IDs, and PLX descriptor offsets.

Control flow: This header does not execute logic, but its layout drives all MMIO operations in the carrier. `tpci200_regs` maps revision/control/reset/status registers; slot space constants determine the child `ipack_device` memory windows.

State and persistence: Persistent runtime state is represented in `tpci200_board`: board number, mutex, register spinlock, slot array, info block, and physical bases for IPACK spaces. `slot_irq` stores a holder device and callback used by interrupt dispatch.

Dependencies/integration: Includes PCI, spinlock, IO, limits, byte-swap, and IPACK definitions. Must match TPCI200/PLX hardware register layout exactly.

Risks and test signals: Validate struct packing and endian-safe MMIO access on supported architectures, BAR indexes against hardware docs, status/control bit definitions, slot interval math, and that comments about mutex protection match the actual `regs_lock` usage in the C file.

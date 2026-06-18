## sources/distributed-fs/ceph-client/arch/mips/kvm/loongson_ipi.c

Purpose: Implements a Loongson-3 virtual IPI MMIO device for MIPS KVM guests.

Important APIs, types, and functions: `loongson_vipi_read()` and `loongson_vipi_write()` implement device register semantics. `kvm_ipi_read()` and `kvm_ipi_write()` adapt those helpers to `struct kvm_io_device_ops` with locking. `kvm_init_loongson_ipi()` registers four node MMIO windows on the KVM MMIO bus.

Control flow: MMIO address bits select core and node, producing an IPI state index. Reads expose status, enable, zero for set/clear, and buffer words. Writes update enable, OR status and inject IRQ 6 on SET, clear status bits and deassert IRQ 6 when all status is clear on CLEAR, or update buffer storage. Device registration initializes one `kvm_io_device` per node at `IPI_BASE + (node << 44)`.

State and persistence: State lives in `kvm->arch.ipi`, including a spinlock, per-VCPU/node `ipi_state` status/en/buffer fields, and IO-device wrappers. It persists for the VM lifetime.

Dependencies and integration points: Depends on KVM MMIO bus, `kvm_vcpu_ioctl_interrupt()`, Loongson CPU configuration, `interrupt.h`, and VM initialization in `mips.c` under `CONFIG_CPU_LOONGSON64`.

Risks: Uses `BUG_ON()` for alignment failures. It assumes core/node indexing maps into allocated `ipistate` entries and that `kvm_get_vcpu(kvm, id)` is valid. SET injects IRQ 6 regardless of `en`, so enable semantics may be incomplete or implemented elsewhere. Register width handling assumes len 4 or 8.

Test signals: MMIO read/write for status/en/set/clear/buffer, aligned access enforcement, IRQ assertion/deassertion behavior, multi-node address decoding, missing VCPU edge cases, and concurrent access under the spinlock.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-init.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-init.c

## Purpose
This file implements VGIC lifecycle management for arm64 KVM: early initialization, in-kernel interrupt controller creation, vCPU private interrupt allocation, distributor initialization, lazy/full init, resource mapping, teardown, CPU hotplug hooks, host GIC probing, maintenance interrupt setup, and VGIC-related ID register finalization.

## Important APIs, Types, And Functions
- `kvm_vgic_early_init()` initializes static VM VGIC state such as the LPI xarray.
- `kvm_vgic_create()` creates the in-kernel VGIC model requested by userspace or legacy irqchip creation.
- `kvm_vgic_vcpu_init()` initializes per-vCPU VGIC structures and redistributor iodev registration for GICv3.
- `vgic_init()` allocates distributor/SPIs or GICv5 state, initializes direct IRQ support, resets vCPUs, sets default routing, creates debugfs, and marks initialized.
- `kvm_vgic_map_resources()` maps/registers distributor and redistributor/MMIO resources on first vCPU run.
- `kvm_vgic_destroy()` and `kvm_vgic_vcpu_destroy()` tear down VM and vCPU VGIC resources.
- `vgic_lazy_init()` supports legacy GICv2 lazy initialization.
- `kvm_vgic_finalize_idregs()` updates VM ID registers to advertise GICv3 or GICv5 capabilities consistently.
- `kvm_vgic_hyp_init()`, `vgic_set_kvm_info()`, `kvm_vgic_init_cpu_hardware()`, `kvm_vgic_cpu_up()`, and `kvm_vgic_cpu_down()` handle host-side VGIC probing and per-CPU maintenance IRQ/hyp state.

## Control Flow
VM creation starts with `kvm_vgic_early_init()`. Userspace then creates an irqchip with `kvm_vgic_create()` under `kvm->lock`; the function locks all visible vCPUs and `config_lock`, rejects races with vCPU creation and already-run vCPUs, selects max vCPUs/model-specific state, finalizes GIC ID registers, and allocates private IRQ arrays.

`vgic_init()` runs once under `config_lock`, freezes SPI count, allocates distributor IRQs for GICv2/v3 or calls GICv5 init, initializes direct injection if supported, resets all vCPUs, installs default IRQ routing, creates debugfs, and marks the distributor initialized. `kvm_vgic_map_resources()` later registers MMIO iodevs under `slots_lock`/`config_lock` and publishes `dist->ready` with release ordering.

Host probing stores `gic_kvm_info`, probes v2/v3/v5 backends, enables the GICv3 CPU interface static branch when available, registers the maintenance IRQ, and initializes per-CPU list registers.

## State And Persistence Behavior
Persistent VM state lives in `kvm->arch.vgic`: model, in-kernel flag, initialized/ready flags, base addresses, SPI array, redistributor regions, LPI xarray, maintenance INTID, GICv5 VM state, implementation revision, and direct IRQ capability. Per-vCPU state includes private IRQ arrays, active/pending lists, redistributor iodev base, and GICv3/v5 CPU interface fields. Destruction frees SPIs, private IRQs, redistributor regions, direct IRQ/v4 state, and xarray state.

## Dependencies And Integration Points
The file integrates with KVM vCPU creation locks, KVM memory slots/iodev registration, VGIC v2/v3/v4/v5 backend helpers, arch timer PPI initialization, IRQ routing, debugfs, host GIC driver-provided `gic_kvm_info`, percpu maintenance IRQs, nested virtualization maintenance handling, and sysreg ID register helpers.

## Risks And Edge Cases
- Creation must exclude concurrent vCPU creation and vCPU ioctls; otherwise private IRQ arrays or model limits can become inconsistent.
- VGIC creation is forbidden after any vCPU has run.
- GICv2 supports lazy initialization; GICv3/GICv5 require explicit initialization.
- Resource mapping failures mark the VM dead after partial mapping errors.
- Lock ordering between `slots_lock`, `config_lock`, and vCPU teardown is explicitly managed to avoid inversions.
- GICv5 creation reinitializes arch timer PPIs because INTID assignments differ.
- ID registers must match the actual in-kernel irqchip model, especially on GICv5 hosts that can emulate legacy GICv3.

## Test Signals
KVM selftests and QEMU boots should cover GICv2 legacy irqchip, GICv3 device API, GICv5 where available, vCPU creation races, creation-after-run rejection, default IRQ routing, first-run MMIO resource mapping, VM teardown, CPU hotplug maintenance IRQ enable/disable, and ID register values before and after irqchip creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-init.c -->

# sources/distributed-fs/ceph-client/arch/loongarch/kvm/Kconfig

Purpose: declares LoongArch virtualization configuration and exposes `CONFIG_KVM` under the `VIRTUALIZATION` menu.

Important APIs, types, and functions: selects generic KVM features including dirty ring acquire/release, IRQ routing, IRQ chip, MSI, readonly memory, common KVM, dirtylog read-protect, hardware enabling, MMIO, guest-mode work transfer, scheduler info, and guest perf events when `PERF_EVENTS` is enabled.

Control flow: sources `virt/kvm/Kconfig`, presents `menuconfig VIRTUALIZATION`, and defines `config KVM` as a tristate depending on assembler LVZ support and `64BIT`.

State and persistence: affects the kernel `.config` and thereby object inclusion, exported interfaces, and runtime KVM availability.

Dependencies and integration points: tied to LoongArch LVZ hardware virtualization, 64-bit builds, generic KVM infrastructure, irqfd/ioeventfd/dirty logging capabilities, and scheduler statistics for steal time.

Risks: missing selects cause compile-time or runtime feature gaps; too-broad enables could advertise unsupported KVM capabilities. The LVZ assembler dependency must match actual toolchain support.

Test signals: Kconfig dependency resolution, allmodconfig/defconfig builds, `modprobe kvm`, and userspace KVM capability probing.

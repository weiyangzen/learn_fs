# sources/distributed-fs/ceph-client/drivers/vdpa/Kconfig

Purpose: Kconfig menu for vDPA drivers, simulators, userspace vDPA, and vendor hardware backends.

Important APIs/types/functions: defines `menuconfig VDPA` gated on `NET`; simulator options `VDPA_SIM`, `VDPA_SIM_NET`, `VDPA_SIM_BLOCK`; `VDPA_USER`; hardware drivers `IFCVF`, `MLX5_VDPA`, `MLX5_VDPA_NET`, `MLX5_VDPA_STEERING_DEBUG`, `VP_VDPA`, `ALIBABA_ENI_VDPA`, `SNET_VDPA`, `PDS_VDPA`, and `OCTEONEP_VDPA`.

Control flow: Kconfig dependency resolution controls which Makefile objects build. `MLX5_VDPA` is a selected bool support library, while `MLX5_VDPA_NET` is the user-visible tristate. `OCTEONEP_VDPA` depends on `m`, forcing module-only builds.

State and persistence: stores build configuration symbols, not runtime state.

Dependencies and integration: selects vhost/IOMMU/virtio helper libraries where needed and ties vendor directories to top-level `drivers/vdpa/Makefile`.

Risks: feature availability is compile-time; missing selects produce link or runtime capability gaps. `ALIBABA_ENI_VDPA` is X86-only and legacy virtio-pci based. Debug steering counters are separately gated.

Test signals: build matrix for built-in/module/off combinations, dependency visibility with and without PCI_MSI/MLX5_CORE/PDS_CORE, and module-only enforcement for Octeon.

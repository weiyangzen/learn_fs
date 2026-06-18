# sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Kconfig

Purpose: adds the `NVGRACE_GPU_VFIO_PCI` tristate for VFIO assignment support for NVIDIA Grace Hopper/Grace Blackwell GPU devices with coherent device memory.

Important configuration: it depends on `ARM64` or `COMPILE_TEST && 64BIT`, selects `VFIO_PCI_CORE`, and documents that the module is intended for assigning the GPU to userspace through KVM/QEMU-style VFIO flows.

Control flow and integration: selecting this config builds the `nvgrace-gpu-vfio-pci` module from the companion Makefile. It gates the specialized VFIO PCI driver that can expose ACPI-described GPU memory as fake VFIO BAR regions.

Risks: enabling on unsupported platforms is compile-test only; runtime behavior depends on ACPI/device properties and NVIDIA device IDs in `main.c`.

Test signals: Kconfig dependency resolution for ARM64 and compile-test builds, module selection, and ensuring `VFIO_PCI_CORE` is selected automatically.

# sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/Makefile

Purpose: wires the NVGrace GPU VFIO PCI module into kbuild.

Important build behavior: `obj-$(CONFIG_NVGRACE_GPU_VFIO_PCI)` emits `nvgrace-gpu-vfio-pci.o`, and the module is built from `main.o`.

Dependencies and integration: this is the build companion to the Kconfig option and has no runtime logic. It follows normal single-object module composition.

Risks and test signals: build failures will surface through missing dependencies in `main.c`; useful tests are `allyesconfig`/`allmodconfig` and ARM64 compile-test coverage.

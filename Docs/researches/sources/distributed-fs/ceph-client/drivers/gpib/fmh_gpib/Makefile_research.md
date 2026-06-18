# sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/Makefile

Purpose: builds the `fmh_gpib.o` module when `CONFIG_GPIB_FMH` is enabled. This module supports Frank Mori Hess's `fmh_gpib_core` platform device and a prototype PCI variant.

Important build API: `obj-$(CONFIG_GPIB_FMH) += fmh_gpib.o` maps the Kconfig symbol to the single adapter implementation. That object registers multiple board interface names: unaccelerated and accelerated platform variants, plus unaccelerated and FIFO-accelerated PCI variants.

Control flow and integration: the module links against common GPIB and NEC7210 helper symbols. Runtime availability is controlled by platform OF match `fmhess,fmh_gpib_core` or prototype PCI IDs in the C file, not by separate build outputs.

State and persistence: no runtime state in the Makefile. It controls whether the board types are available to `CFCBOARDTYPE`.

Dependencies: Kconfig should require GPIB common support, NEC7210 support, platform/OF support, PCI support if the PCI path is built unconditionally, MMIO, IRQ, and DMAengine APIs.

Risks: the C file contains both platform and PCI paths, so missing dependencies can surface as compile/link issues if Kconfig is incomplete. Prototype PCI IDs are bogus constants by design, so successful build does not imply discoverable PCI hardware.

Test signals: build as module and built-in, inspect modpost for GPIB/DMA/PCI dependencies, load/unload, and confirm all interface registrations occur or unwind on simulated registration failures.

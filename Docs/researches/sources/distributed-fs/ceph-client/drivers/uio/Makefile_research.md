# sources/distributed-fs/ceph-client/drivers/uio/Makefile

## Purpose
`drivers/uio/Makefile` maps UIO Kconfig symbols to object files for the UIO core and individual UIO drivers.

## Important Entries
`obj-$(CONFIG_UIO) += uio.o` builds the core. Each child config maps directly to a driver object, including `uio_cif.o`, `uio_pdrv_genirq.o`, `uio_dmem_genirq.o`, `uio_aec.o`, `uio_sercos3.o`, `uio_pci_generic.o`, `uio_netx.o`, `uio_mf624.o`, `uio_fsl_elbc_gpcm.o`, `uio_hv_generic.o`, `uio_dfl.o`, and `uio_pci_generic_sva.o`.

## Control Flow And State
There is no runtime control flow. Kbuild evaluates the `CONFIG_*` symbols and either links objects built-in, builds modules, or omits them.

## Dependencies And Integration Points
The Makefile depends on Kconfig symbol names matching object names and source files in the same directory. It integrates with the kernel build system's `obj-*` convention.

## Risks And Edge Cases
Stale entries cause build failures if the source file is absent or Kconfig symbol is renamed. Formatting is mostly standard, though the `UIO_MF624` and `UIO_PCI_GENERIC_SVA` lines use different spacing, which is harmless.

## Test Signals
Build UIO core and each module as `m` and built-in where dependencies allow. Check that every enabled Kconfig option produces the documented module object.

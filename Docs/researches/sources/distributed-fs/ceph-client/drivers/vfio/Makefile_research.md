# sources/distributed-fs/ceph-client/drivers/vfio/Makefile

## Purpose

This Makefile builds the VFIO core and dispatches to VFIO bus subdirectories. It assembles `vfio.o` from core components based on selected feature symbols and builds legacy IOMMU backends and bus drivers.

## Important APIs, Types, and Functions

The main object is `vfio.o`, always containing `vfio_main.o` when `CONFIG_VFIO` is set. Conditional pieces include `device_cdev.o`, `group.o`, `iommufd.o`, `container.o`, `virqfd.o`, and `debugfs.o`. Standalone objects include `vfio_iommu_type1.o` and `vfio_iommu_spapr_tce.o`. Subdirectories include `pci/`, `platform/`, `mdev/`, `fsl-mc/`, and `cdx/`.

## Control Flow

Kbuild includes each object or directory according to its corresponding `CONFIG_*` symbol. This mirrors the top-level Kconfig split between cdev, group, IOMMUFD, container, virqfd, debugfs, and bus support.

## State and Persistence Behavior

No runtime state exists in the Makefile. It controls the final linkage shape of built-in objects or modules.

## Dependencies and Integration Points

The object list must match symbols declared in `drivers/vfio/Kconfig` and exported functions expected by VFIO bus drivers. It is also the integration point for legacy IOMMU backend modules.

## Risks and Edge Cases

The highest risk is inconsistent feature composition. For example, building a bus driver that expects physical iommufd helpers requires `iommufd.o`; legacy group paths require `group.o` and often `container.o`. Missing conditional objects produce link failures or unavailable ABIs.

## Test Signals

Build matrix coverage should include VFIO with only cdev/IOMMUFD, with legacy group/container, with debugfs, with no-IOMMU, and with each bus subdirectory enabled as built-in and module.

# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Makefile

## Purpose
This Makefile defines the IOMMUFD object composition and conditional build products.

## Important Build Entries
`iommufd-y` contains core objects: `device.o`, `eventq.o`, `hw_pagetable.o`, `io_pagetable.o`, `ioas.o`, `main.o`, `pages.o`, `vfio_compat.o`, and `viommu.o`.

`iommufd-$(CONFIG_IOMMUFD_TEST) += selftest.o` adds selftest-only support.

`obj-$(CONFIG_IOMMUFD) += iommufd.o` builds the main module or built-in object.

`obj-$(CONFIG_IOMMUFD_DRIVER) += iova_bitmap.o` builds the IOVA bitmap helper for driver-facing functionality.

`iommufd_driver-y := driver.o` and `obj-$(CONFIG_IOMMUFD_DRIVER_CORE) += iommufd_driver.o` build the shared driver helper library.

## Control Flow
Kconfig symbols choose whether the main `/dev/iommu` implementation, selftests, IOVA bitmap helper, and shared driver core are included. `driver.o` is separated from `iommufd.o` so builtin or external users can consume shared helper exports when `IOMMUFD_DRIVER_CORE` is selected.

## State And Persistence
There is no runtime state in the Makefile. Its persistent effect is the build artifact layout and symbol availability.

## Dependencies And Integration Points
It integrates with `Kconfig`, `main.c` ioctl dispatch, IOAS/page-table code, VFIO compatibility, vIOMMU support, event queues, and the exported helper namespace from `driver.c`.

## Risks
Misconfigured object inclusion can produce missing exported symbols or include driver helpers without the rest of IOMMUFD. Test-only `selftest.o` must remain conditional. Splitting `driver.o` from the main object means namespace imports and Kconfig dependencies must stay aligned.

## Test Signals
Check `make drivers/iommu/iommufd/` under `IOMMUFD=m/y`, `IOMMUFD_TEST=y`, and driver-core-only configurations. `modinfo`/link output should expose expected `iommufd` and `iommufd_driver` artifacts.

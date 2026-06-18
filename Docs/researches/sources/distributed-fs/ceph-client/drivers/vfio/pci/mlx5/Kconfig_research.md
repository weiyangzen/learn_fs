# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Kconfig

## Purpose

This Kconfig file enables the MLX5 VFIO PCI variant driver, primarily for migration support on Mellanox/NVIDIA MLX5 devices.

## Important APIs, Types, and Functions

`MLX5_VFIO_PCI` is a tristate option depending on `MLX5_CORE`, selecting `VFIO_PCI_CORE` and `IOMMUFD_DRIVER`.

## Control Flow

When selected, the mlx5 VFIO PCI variant is built from the mlx5 subdirectory and can provide device-specific migration behavior using VFIO PCI core.

## State and Persistence Behavior

Only build-time configuration state is represented.

## Dependencies and Integration Points

It integrates MLX5 core support, VFIO PCI core, and IOMMUFD driver support.

## Risks and Edge Cases

The variant depends on MLX5 core APIs and IOMMUFD infrastructure, so mismatched dependencies would produce link or runtime feature issues.

## Test Signals

Build with `MLX5_CORE` and `MLX5_VFIO_PCI` enabled as module and built-in, and verify `IOMMUFD_DRIVER` is selected.

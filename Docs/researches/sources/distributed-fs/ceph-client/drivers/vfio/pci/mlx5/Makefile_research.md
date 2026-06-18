# sources/distributed-fs/ceph-client/drivers/vfio/pci/mlx5/Makefile

## Purpose

This Makefile builds the MLX5 VFIO PCI variant driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_MLX5_VFIO_PCI) += mlx5-vfio-pci.o` enables the aggregate object, and `mlx5-vfio-pci-y := main.o cmd.o` links the main driver and command helpers.

## Control Flow

Kbuild compiles and links the MLX5 VFIO PCI module when its Kconfig symbol is enabled.

## State and Persistence Behavior

No runtime state exists here.

## Dependencies and Integration Points

The Makefile maps MLX5 VFIO PCI Kconfig to the implementation objects and assumes those files provide the command and main-driver pieces.

## Risks and Edge Cases

Object-list drift between main and command helper files would break migration command support or symbol resolution.

## Test Signals

Build `CONFIG_MLX5_VFIO_PCI=y` and `m` and verify both `main.o` and `cmd.o` are included.

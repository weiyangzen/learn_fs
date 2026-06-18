# sources/distributed-fs/ceph-client/drivers/cdx/controller/Kconfig

## Purpose
This Kconfig file defines the CDX controller driver option under `CONFIG_CDX_BUS`.

## Important APIs, Types, and Functions
The sole symbol is `CDX_CONTROLLER`, a tristate "CDX bus controller". It depends on `HAS_DMA` and selects `REMOTEPROC` and `RPMSG`, matching the controller's firmware transport requirements.

## Control Flow
If `CDX_BUS` is enabled, the menu allows selecting the controller. When selected, the controller Makefile builds the combined `cdx-controller` object.

## State and Persistence Behavior
Selection persists in `.config` and controls whether the platform/rpmsg/MCDI controller stack is compiled. Runtime state is owned by the C files.

## Dependencies and Integration Points
The option integrates the CDX bus with a remote processor firmware path over RPMsg. `HAS_DMA` is required because exposed CDX devices and MSI programming involve DMA-capable hardware.

## Risks
Selecting `REMOTEPROC` and `RPMSG` pulls in substantial infrastructure. A kernel with `CDX_BUS` but without `CDX_CONTROLLER` can still host other controller providers, but the Versal-Net controller will not bind.

## Test Signals
Kconfig tests should confirm the option appears only under `CDX_BUS`, selects RPMsg/remoteproc, and produces `cdx-controller.o` for built-in and module builds.


# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Makefile

## Purpose

This Makefile maps Hisilicon Ethernet Kconfig symbols to the driver objects and subdirectories built by Kbuild.

## Important APIs, Types, and Functions

It builds `hix5hd2_gmac.o`, `hip04_eth.o`, `hns_mdio.o`, `hisi_femac.o`, the `hns/` and `hns3/` subdirectories, and the `hibmcge/` subdirectory according to their `CONFIG_*` symbols.

## Control Flow

There is no runtime control flow. Kbuild includes objects and subdirectories based on configuration.

## State and Persistence

The file affects build artifacts only.

## Dependencies and Integration Points

It integrates with the local Kconfig symbols and delegates composite driver construction to subdirectory Makefiles for HNS, HNS3, and HIBMCGE.

## Risks and Edge Cases

Object names must match source files and Kconfig symbols exactly. Missing subdirectory inclusion would silently omit configured drivers. Tristate combinations should be verified for module and built-in builds.

## Test Signals

Expected outputs include direct objects for selected platform MACs and recursive builds for `hns/`, `hns3/`, and `hibmcge/` when their symbols are enabled.

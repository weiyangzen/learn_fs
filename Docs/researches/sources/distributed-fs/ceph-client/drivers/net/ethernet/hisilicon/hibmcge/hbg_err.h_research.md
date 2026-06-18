
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.h

## Purpose

This header declares HIBMCGE reset/rebuild and PCI error-handler integration functions.

## Important APIs, Types, and Functions

It declares `hbg_set_pci_err_handler()`, `hbg_reset()`, `hbg_rebuild()`, and `hbg_err_reset()`.

## Control Flow

The header has no runtime control flow. Callers use the declarations from main lifecycle, ethtool, IRQ/service recovery, and PCI setup.

## State and Persistence

No state is declared here.

## Dependencies and Integration Points

It includes PCI declarations and links error recovery implementation into other HIBMCGE modules.

## Risks and Edge Cases

Prototype mismatch would break reset or AER integration at build time.

## Test Signals

Build coverage and reset/AER behavior validate the interface.

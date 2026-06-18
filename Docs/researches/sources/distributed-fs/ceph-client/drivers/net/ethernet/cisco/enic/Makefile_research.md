<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Makefile

## Purpose

This Makefile defines the ENIC composite object and its source-file membership.

## Important APIs, Types, and Functions

`obj-$(CONFIG_ENIC) := enic.o` builds the ENIC driver, and `enic-y` composes it from main netdev logic, vNIC queue/intr/dev helpers, resource setup, port-profile handling, ethtool, public API, classifier, and RX/TX queue helper files.

## Control Flow

There is no runtime flow. Kbuild links the listed objects into one `enic.o`.

## State and Persistence Behavior

No runtime state exists. The source list defines which internal symbols are available in the final module/built-in object.

## Dependencies and Integration Points

The file integrates all ENIC internal modules, including helper files not in this research subset such as `vnic_dev.c`, `enic_res.c`, `enic_rq.c`, and `enic_wq.c`.

## Risks and Edge Cases

Omitting any helper breaks link-time internal dependencies. Adding files in the wrong order generally should not matter to Kbuild, but missing object membership would prevent features such as RX page-pool handling or devcmd support.

## Test Signals

Build ENIC as module and built-in, checking that all referenced internal functions link and module metadata is emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/Makefile -->

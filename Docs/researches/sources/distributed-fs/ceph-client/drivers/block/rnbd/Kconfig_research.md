# sources/distributed-fs/ceph-client/drivers/block/rnbd/Kconfig

## Purpose
Defines Kconfig symbols for the RDMA Network Block Device subsystem and its client/server drivers.

## Important APIs, Types, And Functions
This file declares internal `BLK_DEV_RNBD`, plus user-visible tristate symbols `BLK_DEV_RNBD_CLIENT` and `BLK_DEV_RNBD_SERVER`. The client depends on `INFINIBAND_RTRS_CLIENT`, selects `BLK_DEV_RNBD` and `SG_POOL`, and describes remote block-device mapping over RTRS. The server depends on `INFINIBAND_RTRS_SERVER`, selects `BLK_DEV_RNBD`, and describes exporting local block devices over RTRS.

## Control Flow
There is no runtime flow. During kernel configuration, enabling client or server pulls in the common RNBD symbol. The parent block Kconfig sources this file so these options appear under block driver configuration.

## State And Persistence Behavior
Kconfig state is build-time configuration only. It controls whether RNBD client/server objects are built in, built as modules, or omitted. No runtime state or persistent data is defined here.

## Dependencies And Integration Points
RNBD is tied to the RTRS RDMA transport stack through `INFINIBAND_RTRS_CLIENT` and `INFINIBAND_RTRS_SERVER`. Client additionally selects scatterlist pool support. The matching `Makefile` consumes these symbols to build `rnbd-client.o` and `rnbd-server.o`.

## Risks
Dependency correctness is the main risk. If RTRS symbols or SG pool requirements change, this file must be updated or builds may fail. Because `BLK_DEV_RNBD` is a hidden bool selected by both endpoints, common code assumptions must stay compatible with either client-only or server-only builds.

## Test Signals
Signals include Kconfig dependency resolution for client-only, server-only, both, module, and built-in combinations; compile tests with and without RTRS; and module packaging checks that selected symbols produce the expected objects.

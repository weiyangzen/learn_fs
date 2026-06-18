# sources/distributed-fs/openafs/src/libadmin/test/vos.h

## Purpose

`vos.h` is the local header for VOS command support in the `afscp` libadmin test client.

## Important APIs, Types, and Functions

It includes standard headers, pthreads, RX/RX stats, `afs_Admin.h`, `afs_vosAdmin.h`, `afs_utilAdmin.h`, cell configuration, command parsing, and `common.h`. It declares `SetupVosAdminCmd(void)`.

## Control Flow

The header has no executable control flow. It exposes the command-registration function implemented by `vos.c`.

## State and Persistence Behavior

No state is stored in the header. Remote volume/VLDB state changes happen through handlers in `vos.c`.

## Dependencies and Integration Points

The file connects the test client to the public VOS admin API. Its top comment says "bos" functions, but this is stale copy text; the include set and declaration are VOS-specific.

## Risks and Test Signals

Build tests should compile this header with the VOS admin library headers available. Because the header only exports setup, integration tests should verify that all VOS commands are registered through `SetupVosAdminCmd`.

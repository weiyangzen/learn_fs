# sources/distributed-fs/openafs/src/libadmin/test/pts.h

## Purpose

`pts.h` is the local include surface for `pts.c`, the PTS command group in the `afscp` libadmin test client.

## Important APIs, Types, and Functions

It includes standard C headers, pthreads, `afs_Admin.h`, `afs_ptsAdmin.h`, `afs_utilAdmin.h`, cell configuration, command parsing, and `common.h`. It declares `SetupPtsAdminCmd(void)`.

## Control Flow

The file contains no executable logic. It supports command registration by exposing the setup function to the test-client main program.

## State and Persistence Behavior

No state is stored here. State changes occur only in `pts.c` through calls to the remote protection database APIs.

## Dependencies and Integration Points

The header couples the PTS command wrapper to the shared libadmin test harness and the OpenAFS PTS admin API. `common.h` provides shared globals and error/argument helpers.

## Risks and Test Signals

Build coverage should ensure the header remains compatible with the PTS admin headers and command package. Since only one function is exported, accidental signature drift in `SetupPtsAdminCmd` would be caught by compiling the test program.

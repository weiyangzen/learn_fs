# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpmcp.c

## Purpose
Implements minimal DPAA2 Data Path Management Command Portal command wrappers for opening and closing DPMCP objects.

## Important APIs, Types, And Functions
The file defines `dpmcp_open()` and `dpmcp_close()`. They use `struct fsl_mc_command`, `DPMCP_CMDID_OPEN`, `DPMCP_CMDID_CLOSE`, `struct dpmcp_cmd_open`, and MC token helpers.

## Control Flow
`dpmcp_open()` encodes an open command with object ID, sends it through the supplied MC portal, and reads the returned token from the response header. `dpmcp_close()` sends a close command for an existing token.

## State And Persistence
No local state is kept. The only session state is the MC token held by the caller and tracked by MC firmware.

## Dependencies And Integration Points
It depends on `linux/fsl/mc.h` and private fsl-mc command definitions. DPMCP objects are also treated as allocatable resources by the fsl-mc allocator, although generic object allocation forbids requesting DPMCP through `fsl_mc_object_allocate()`.

## Risks And Test Signals
Risks are narrow: command ID/layout mismatch, invalid object IDs, leaked tokens, or closing the wrong session. Test signals are successful portal open/close during fsl-mc bus operation and no MC firmware errors for DPMCP resource handling.

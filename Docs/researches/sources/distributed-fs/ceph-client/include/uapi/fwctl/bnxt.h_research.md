<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/bnxt.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/bnxt.h

## Purpose
Defines Broadcom BNXT-specific data carried by the generic `fwctl` firmware-control UAPI. It identifies supported BNXT command classes and the device-data shape returned by `FWCTL_INFO`.

## Important APIs, Types, And Functions
`enum fwctl_bnxt_commands` advertises inline, query, and send command categories. `struct fwctl_info_bnxt` contains `uctx_caps`, a firmware/user-context capability bitmap interpreted by the BNXT fwctl driver.

## Control Flow
Userspace first issues `FWCTL_INFO` through the generic fwctl fd, verifies `FWCTL_DEVICE_TYPE_BNXT`, reads `fwctl_info_bnxt`, then formats BNXT-specific RPC payloads for `FWCTL_RPC` according to the advertised capabilities.

## State And Persistence
The header itself defines no persistent state. Kernel state lives in the fwctl file context and BNXT firmware context; `uctx_caps` is a snapshot of allowed operations for that fd.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and the generic `fwctl.h` contract. It integrates with BNXT device firmware, fwctl security scopes, and vendor tooling that understands BNXT command payloads.

## Risks And Edge Cases
Risks are capability misinterpretation, use of commands outside the fd's granted scope, and ABI ambiguity if future bit definitions are added without keeping old zero/default behavior.

## Test Signals
Tests should validate `FWCTL_INFO` device type/data length, correct `uctx_caps` reporting, rejected unsupported command classes, and RPC error propagation for invalid or out-of-scope BNXT payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/bnxt.h -->

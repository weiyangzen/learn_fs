# sources/distributed-fs/ceph-client/include/uapi/linux/tdx-guest.h

## Purpose
Defines the Intel TDX guest driver ioctl ABI for obtaining a TDREPORT0 attestation report from `TDG.MR.REPORT`.

## Important APIs, Types, and Constants
`TDX_REPORTDATA_LEN` is 64 and `TDX_REPORT_LEN` is 1024. `struct tdx_report_req` carries caller-supplied `reportdata` and output `tdreport`. `TDX_CMD_GET_REPORT0` is an `_IOWR('T', 1, struct tdx_report_req)` ioctl.

## Control Flow, State, and Persistence
Userspace supplies nonce/report data, kernel invokes the TDX TDCALL, and returns the report. No persistent state is defined by the header, though the report binds to current TD measurements.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with the TDX guest device and remote attestation workflows.

## Risks and Test Signals
Risks include exposing uninitialized report bytes, not preserving nonce, and error mapping from TDCALL failures. Test success path in a TDX guest, invalid ioctl buffers, reportdata echo/binding through attestation verifier, and non-TDX error behavior.

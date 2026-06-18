# sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/tdx_guest_test.c

## Purpose
Kselftest harness program that verifies TDX guest report generation through `/dev/tdx_guest`. It requests a TDREPORT and checks that the returned report embeds the caller-provided report data.

## Important APIs, Types, and Functions
Defines TDX report layout structs `tdreport_type`, `reportmac`, `td_info`, and `tdreport` matching the TDX specification. Uses `struct tdx_report_req`, `TDX_REPORTDATA_LEN`, and `TDX_CMD_GET_REPORT0` from `<linux/tdx-guest.h>`. Helper `print_array_hex()` dumps buffers when `DEBUG` is enabled. The test case is `TEST(verify_report)`.

## Control Flow
The test opens `/dev/tdx_guest` read/write synchronized, fills `req.reportdata` with a byte pattern, calls `ioctl(TDX_CMD_GET_REPORT0, &req)`, optionally dumps buffers, casts `req.tdreport` to `struct tdreport`, compares the `reportmac.reportdata` field with the original input, and closes the device.

## State and Persistence Behavior
No file persistence. The driver returns an attestation report for the running TDX guest. All buffers are stack-local to the test.

## Dependencies and Integration Points
Depends on the TDX guest driver, `/dev/tdx_guest`, TDX-capable guest environment, Linux UAPI header `tdx-guest.h`, and `kselftest_harness.h`.

## Risks and Edge Cases
The test is environment-specific and will fail rather than skip if the device cannot be opened unless harness assertions are interpreted by runner policy. Struct casts assume the UAPI TDREPORT byte layout matches the locally declared spec structs. It only verifies report-data echoing, not MAC validity or measurement semantics.

## Test Signals
Signals are successful device open, successful `TDX_CMD_GET_REPORT0` ioctl, byte-for-byte match of 64-byte report data, and clean close.

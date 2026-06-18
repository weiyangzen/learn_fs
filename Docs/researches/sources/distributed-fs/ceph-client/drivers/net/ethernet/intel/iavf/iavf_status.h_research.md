# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_status.h

## Purpose
Defines the internal `enum iavf_status` error namespace used by IAVF hardware/AdminQ helpers before conversion to Linux errno values or diagnostic strings.

## Important APIs, Types, and Functions
The central type is `enum iavf_status`, with `IAVF_SUCCESS` as zero and negative driver-specific failures such as NVM, PHY, configuration, queue, AdminQ, timeout, unsupported, firmware API, and critical AdminQ errors. There are no functions in this header.

## Control Flow
No executable control flow is present. Callers return or switch on these values in lower-level AdminQ and hardware helper paths. `iavf_virtchnl.c` converts send failures with `iavf_status_to_errno` and logs names with `iavf_stat_str`.

## State and Persistence
The file owns no runtime state. The enum values are persistent ABI within the driver source and must remain coherent with status-to-string and status-to-errno translation tables elsewhere in the driver.

## Dependencies and Integration Points
Included by `iavf_type.h`, making it available to hardware structures, AdminQ code, and virtchnl send/receive handling. It also aligns conceptually with AdminQ status reporting from the shared Intel Ethernet code.

## Risks
Adding, renumbering, or deleting entries without updating conversion helpers can cause misleading logs or incorrect errno propagation. Because all failures are negative and not Linux errno values, callers must avoid returning them directly to kernel subsystems unless translated.

## Test Signals
Compile-time coverage for all status users, AdminQ failure injection, virtchnl send failure logging, timeout paths, and checks that user-visible netdev/ethtool operations receive Linux errno values rather than raw IAVF status codes.

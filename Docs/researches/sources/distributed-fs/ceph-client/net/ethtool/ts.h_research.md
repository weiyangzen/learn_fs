<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/ts.h -->
# sources/distributed-fs/ceph-client/net/ethtool/ts.h

## Purpose
Provides shared timestamping netlink declarations for ethtool timestamp information and timestamp configuration handlers.

## APIs, Types, and Functions
Defines the nested policy `ethnl_ts_hwtst_prov_policy` for `ETHTOOL_A_TS_HWTSTAMP_PROVIDER_INDEX` and `ETHTOOL_A_TS_HWTSTAMP_PROVIDER_QUALIFIER`, and declares `ts_parse_hwtst_provider()`.

## Control Flow, State, and Persistence
There is no executable control flow or mutable state in this header. It centralizes validation constraints for timestamp provider descriptors so both `tsinfo.c` and `tsconfig.c` parse the same nested attribute shape.

## Dependencies and Integration
Depends on `netlink.h` for ethtool netlink definitions and on timestamp provider UAPI constants such as `HWTSTAMP_PROVIDER_QUALIFIER_CNT`. `tsconfig.c` includes this header for provider SET parsing; `tsinfo.c` provides the implementation and uses the same policy for GET filtering.

## Risks and Test Signals
Risks are limited but include policy drift if provider attributes evolve without updating both the policy and parser contract. Test signals are malformed nested provider attributes, qualifier max-bound validation, and shared behavior between tsinfo GET filtering and tsconfig SET source selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/ts.h -->

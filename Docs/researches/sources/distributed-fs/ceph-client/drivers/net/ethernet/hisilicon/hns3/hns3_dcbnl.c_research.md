# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_dcbnl.c

## Purpose

`hns3_dcbnl.c` bridges Linux DCBNL netdevice callbacks to HNS3 backend DCB operations. It exposes IEEE ETS, PFC, application priority, and DCBX get/set operations when the handle has backend `dcb_ops` and the device is not a VF.

## Important Functions

- `hns3_dcbnl_ieee_getets()` / `hns3_dcbnl_ieee_setets()` delegate ETS get/set.
- `hns3_dcbnl_ieee_getpfc()` / `hns3_dcbnl_ieee_setpfc()` delegate PFC get/set.
- `hns3_dcbnl_ieee_setapp()` / `hns3_dcbnl_ieee_delapp()` delegate DCB application priority changes.
- `hns3_dcbnl_getdcbx()` / `hns3_dcbnl_setdcbx()` delegate DCBX mode get/set.
- `hns3_dcbnl_setup()` attaches `hns3_dcbnl_ops` to `net_device::dcbnl_ops` only when supported and not a VF.

## Control Flow

Each callback obtains the HNAE3 handle from the netdev with `hns3_get_handle()`. Mutating and query operations that can touch backend DCB state first reject NIC reset with `-EBUSY`. If the corresponding backend function pointer exists, the call is forwarded with the handle and original DCB object. Missing operations return `-EOPNOTSUPP`, except `getdcbx()` returns `0` and `setdcbx()` returns `1` to match DCBNL expectations.

## State and Persistence Behavior

This file owns no persistent hardware state. It installs a static `struct dcbnl_rtnl_ops` pointer into the netdev. Actual DCB state is owned by the backend implementation referenced by `handle->kinfo.dcb_ops` and likely persisted in firmware or driver state outside this file.

## Dependencies and Integration Points

The file depends on `hnae3.h` for `struct hnae3_handle` and DCB ops, `hns3_enet.h` for `hns3_get_handle()` and `hns3_nic_resetting()`, and Linux DCBNL structures. It integrates with netdev registration and HCLGE DCB backend code.

## Risks and Edge Cases

- `hns3_dcbnl_getdcbx()` and `setdcbx()` do not check reset state unlike the IEEE callbacks.
- The callbacks assume `h->kinfo.dcb_ops` is valid after setup; setup skips null ops, but later teardown ordering must preserve it while netdev callbacks are registered.
- VF devices are intentionally excluded, so SR-IOV behavior depends on PF-side management.
- Missing backend operations produce user-visible unsupported errors.

## Test Signals

Useful tests include DCBNL operations during normal operation and reset, PF devices with and without DCB support, VF devices confirming no DCBNL ops are installed, missing callback behavior, ETS/PFC round trips through firmware, and DCBX mode return conventions.

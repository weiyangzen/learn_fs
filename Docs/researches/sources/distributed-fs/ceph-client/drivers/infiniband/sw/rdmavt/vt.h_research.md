# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.h

## Purpose
`vt.h` is the central internal rdmavt include. It gathers subsystem headers and defines device-scoped logging macros used across rdmavt implementation files.

## Important APIs, types, and functions
It includes PD, QP, AH, MR, SRQ, multicast, mmap, CQ, and MAD headers. It defines `rvt_pr_info()`, `rvt_pr_warn()`, `rvt_pr_err()`, and `rvt_pr_err_ratelimited()` wrappers that log through `rdi->driver_f.get_pci_dev(rdi)` with the IB device name. It also defines `ibport_num_to_idx()` to convert one-based IB port numbers to zero-based arrays.

## Control flow
No direct flow is implemented. The inline port-index helper is used wherever RDMA core port numbers address `rdi->ports[]`.

## State and persistence
No state is stored here. The macros rely on provider `rvt_dev_info` state and a valid PCI device callback.

## Dependencies and integration points
The header depends on `<rdma/rdma_vt.h>`, `<linux/pci.h>`, and all local rdmavt subsystem headers. It is the common include point for files that need broad access to internal rdmavt APIs.

## Risks
Logging macros assume `get_pci_dev` is present and returns a valid device, which `vt.c` enforces during registration. `ibport_num_to_idx()` does no validation; callers must validate port numbers before indexing.

## Test signals
Build coverage across rdmavt and providers catches include-order problems. Runtime port query/modify tests with invalid port numbers should validate callers rather than this helper.

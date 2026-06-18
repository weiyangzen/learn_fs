# sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.h

## Purpose
This generated header is the internal contract between the generated DPLL netlink family table and the hand-written DPLL netlink implementation.

## Important APIs and types
It declares the shared nested attribute policy arrays, pre/post locking hooks, all DPLL device and pin netlink command handlers, the `DPLL_NLGRP_MONITOR` multicast group enum, and `extern struct genl_family dpll_nl_family`.

## Control flow and integration
`dpll_nl.c` consumes these declarations when building `dpll_nl_ops[]`; `dpll_netlink.c` provides the functions and uses `dpll_nl_family` for replies and multicast notifications.

## State, dependencies, risks, and tests
The header owns no state. It depends on netlink/genetlink headers and `uapi/linux/dpll.h`. The risk is regeneration mismatch with `dpll_nl.c` or with handler names in `dpll_netlink.c`. Compilation and YNL regeneration diffs are the main test signal.

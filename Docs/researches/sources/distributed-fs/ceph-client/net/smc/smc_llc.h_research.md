# sources/distributed-fs/ceph-client/net/smc/smc_llc.h

## Purpose
`smc_llc.h` exposes the LLC protocol constants and public link-control API used by core SMC-R code.

## Important APIs, Types, and Functions
The header defines LLC response flags, wait intervals, `enum smc_llc_reqresp`, and `enum smc_llc_msg_type` for v1 and v2 message IDs. It provides `smc_link_downing()` plus inline helpers `smc_llc_usable_link()` and `smc_llc_set_termination_rsn()`. It declares transmit APIs, link-group and link lifecycle hooks, rkey operations, flow control helpers, add/delete link entry points, and `smc_llc_init()`.

## Control Flow
Core code uses `smc_llc_lgr_init()` when creating an SMC-R group, `smc_llc_link_init()` and `smc_llc_link_active()` around RDMA link setup, and `smc_llc_link_clear()` during teardown. Link loss paths use `smc_link_downing()` to atomically transition active links to inactive. Buffer code initiates `SMC_LLC_FLOW_RKEY` before confirm/delete rkey operations. Device and core failover paths use add/delete link helpers to reconfigure groups.

## State and Persistence
The header owns no state. It defines constants and function signatures for state stored in `struct smc_link_group` and `struct smc_link`.

## Dependencies and Integration Points
It includes `smc_wr.h` and relies on core types from `smc_core.h` through inclusion order in C files. It is the main contract between `smc_core.c` and `smc_llc.c`, and it defines reason codes shared across teardown paths.

## Risks
Message type and reason code constants must match the SMC protocol. `smc_link_downing()` only transitions from `SMC_LNK_ACTIVE` to `SMC_LNK_INACTIVE`; callers using it on activating links will not act. `smc_llc_usable_link()` returns the first usable link, not necessarily sendable, so send paths must still hold and validate WR availability.

## Test Signals
Compile-time coverage should catch missing prototypes. Runtime signals include correct DELETE LINK reason propagation, no duplicate link-down processing, successful rkey flow initiation, and expected add/delete behavior when multiple links are present.

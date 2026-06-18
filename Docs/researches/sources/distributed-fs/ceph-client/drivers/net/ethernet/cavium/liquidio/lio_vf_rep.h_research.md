# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.h

## Purpose
Declares the small public interface and per-representor state used by LiquidIO VF representor support. It is the contract between `lio_vf_rep.c` and the rest of the PF driver.

## Important APIs, Types, and Functions
Constants include `LIO_VF_REP_REQ_TMO_MS` for command timeout intent and `LIO_VF_REP_STATS_POLL_TIME_MS` for periodic stats refresh. `struct lio_vf_rep_desc` stores parent and representor netdev pointers, the owning `octeon_device`, cached `lio_vf_rep_stats`, delayed stats work, atomic interface state, and firmware ifidx. `struct lio_vf_rep_sc_ctx` wraps a completion but is not used by the current C file. Public functions are `lio_vf_rep_create`, `lio_vf_rep_destroy`, `lio_vf_rep_modinit`, and `lio_vf_rep_modexit`.

## Control Flow
The header has no runtime control flow. Its declarations support module-level notifier registration, representor creation during switchdev/SR-IOV setup, and representor destruction during eswitch or device teardown.

## State and Persistence Behavior
The header defines in-memory state only. Persistent device-side representor attributes are defined in `liquidio_common.h` request/response structs and are synchronized by `lio_vf_rep.c`.

## Dependencies and Integration Points
It assumes definitions for `struct net_device`, `struct octeon_device`, `struct lio_vf_rep_stats`, `struct cavium_wk`, and `LIO_IFSTATE_RUNNING` are available through the including C file's header set. Its lifecycle functions are consumed by PF-side driver code that toggles switchdev representors.

## Risks
Because the header does not include all types it references, include order matters. The unused `lio_vf_rep_sc_ctx` is a maintenance signal. Timeout and polling constants must match firmware responsiveness and teardown expectations; an overly aggressive stats poll can amplify command latency or teardown races.

## Test Signals
Compile coverage with representor support built, switchdev enable/disable paths, stats-work cancellation, and include-order coverage from every C file that includes this header are the main signals.

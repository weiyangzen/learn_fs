# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sched.h

## Purpose

`ice_sched.h` declares the ice transmit scheduler contract shared by scheduler implementation, VSI setup, queue setup, reset replay, and bandwidth/aggregator control code. It defines topology layer constants, burst-size and rate-limit profile math constants, aggregator bookkeeping structures, and public scheduler APIs.

## Important APIs, Types, And Functions

- Layer constants define 5-layer and 9-layer layouts plus offsets for queue-group, VSI, and aggregator layers.
- Burst-size constants encode the 12-bit firmware field, 64-byte versus 1-KB granularity, and accepted minimum/maximum byte ranges.
- Rate-limit constants define profile accuracy, multipliers, fractional encoding, and supported PSM clock frequencies.
- `struct ice_aqc_rl_profile_info` wraps a firmware RL profile element with list linkage, requested bandwidth, and reference count.
- `struct ice_sched_agg_vsi_info` records VSI membership and TC/replay bitmaps for an aggregator.
- `struct ice_sched_agg_info` records aggregator ID/type, member list, active/replay TC bitmaps, and per-TC saved bandwidth type information.
- Prototypes expose firmware scheduler element calls, topology mutation, VSI configuration/removal, aggregator configuration/move/replay, queue/VSI bandwidth limits, burst sizing, and queue bandwidth replay.

## Control Flow

The header has no runtime control flow, but it describes the legal call surface for `ice_sched.c`. Callers initialize scheduler resources, configure VSIs and queues, optionally create aggregators and bandwidth limits, then call replay helpers after reset. Many declared functions require the scheduler lock even where the header does not encode that requirement in the type system.

## State And Persistence

The header defines in-memory state structures used for scheduler persistence across driver reset replay. Aggregator TC bitmaps and bandwidth type information are saved locally, while actual scheduler nodes and rate-limit profiles live in firmware and are rebuilt through the C implementation. No file-backed persistence is involved.

## Dependencies And Integration Points

It includes `ice_common.h` for hardware, port, scheduler node, VSI context, AdminQ, bandwidth, and queue context types. Consumers include core VSI/queue code, SR-IOV and subfunction VSI setup, devlink or tc bandwidth paths, and reset recovery code.

## Risks

- Constants for layer offsets assume firmware topology conventions; new topology layouts require coordinated updates in both header and implementation.
- Public prototypes do not distinguish functions that require `sched_lock` from those that take it internally.
- Aggregator replay state is compact but subtle: active TC bitmaps and replay TC bitmaps have different meanings during reset recovery.
- Burst and RL profile constants must stay aligned with firmware encoding, or valid user bandwidth requests can be rejected or misprogrammed.

## Test Signals

Compile coverage should catch prototype drift. Runtime coverage comes from `ice_sched.c` tests for layer selection, burst-size boundaries, RL profile encoding, aggregator replay, and VSI/queue setup. Static assertions for constants and structure assumptions would be useful if accepted by the driver style.

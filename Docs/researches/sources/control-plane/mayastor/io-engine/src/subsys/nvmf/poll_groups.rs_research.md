# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/poll_groups.rs

## Purpose
This file wraps SPDK NVMf poll group creation for a Mayastor reactor thread.

## Important APIs, Types, And Functions
`PollGroup` stores an `Mthread` and a `Pg` wrapper around `*mut spdk_nvmf_poll_group`. `PollGroup::new` calls `spdk_nvmf_poll_group_create`. `group_ptr` returns the raw poll group pointer.

## Control Flow
The target code creates a poll group for an SPDK target pointer and reactor thread, then stores it in thread-local NVMf poll group state.

## State, Persistence, And Dependencies
State is a raw SPDK poll group pointer associated with an `Mthread`. No persistence exists. Dependencies are SPDK NVMf target/poll-group FFI and Mayastor `Mthread`.

## Integration Points
NVMf target connection scheduling uses these poll groups to place qpairs on reactor threads.

## Risks
There is no null check after `spdk_nvmf_poll_group_create`, so allocation failure would store a null pointer. There is no explicit Drop/destructor here; lifecycle likely depends on SPDK target shutdown elsewhere.

## Test Signals
Validate non-null poll group creation, association with the expected thread, pointer access, and cleanup through the target shutdown path.

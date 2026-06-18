# sources/distributed-fs/ceph-client/drivers/hv/mshv_vtl.h

## Purpose

`mshv_vtl.h` defines the userspace-visible run structure for MSHV VTL support. It packages cancellation state, return-action sizing, exit messages, CPU context, and return actions for VTL run operations.

## Important APIs, Types, and Functions

- `struct mshv_vtl_run` contains `cancel`, `vtl_ret_action_size`, padding, `exit_message[MSHV_MAX_RUN_MSG_SIZE]`, a union containing `struct mshv_vtl_cpu_context` or a 1024-byte reserved area, and `vtl_ret_actions[MSHV_MAX_RUN_MSG_SIZE]`.

## Control Flow

This header has no executable logic. VTL device code maps or copies this structure between kernel and userspace so userspace can observe exits, provide CPU context, request cancellation, and receive VTL return actions.

## State and Persistence Behavior

Instances are per run/mapping and are ABI state shared with userspace. The reserved 1024-byte union member preserves layout room for future CPU-context growth.

## Dependencies and Integration Points

It includes UAPI `linux/mshv.h` for `MSHV_MAX_RUN_MSG_SIZE` and `mshv_vtl_cpu_context`, plus Linux integer types. It is consumed by VTL implementation files outside this subset.

## Risks and Edge Cases

Because this is syscall-note ABI layout, field order and sizes must remain stable. Padding/reserved fields should be zeroed/validated by implementation code. Consumers must honor `vtl_ret_action_size` bounds against `vtl_ret_actions`.

## Test Signals

ABI tests should assert `sizeof(struct mshv_vtl_run)`, field offsets, zero/reserved handling, max message/action bounds, and compatibility with existing userspace VTL tooling.

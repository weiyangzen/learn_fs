# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_u.h

## Purpose

`timerlat_u.h` declares the small interface used by timerlat tools to launch and control user-space timerlat workload processes.

## Important APIs, Types, and Functions

`struct timerlat_u_params` contains dispatcher control flags (`should_run`, `stopped_running`), the monitored CPU set, an optional cgroup name, and optional scheduler attributes. The only declared function is `timerlat_u_dispatcher(void *data)`, intended as a pthread entry point.

## Control Flow and Data Flow

Callers initialize the parameter structure, start the dispatcher thread, and later clear `should_run` to request teardown. The dispatcher writes back `stopped_running` after all child workload processes have exited.

## State and Persistence Behavior

The header defines shared in-process state only. The pointed-to CPU set, cgroup string, and scheduler attributes are caller-owned. Runtime persistence is limited to scheduler/cgroup effects created by `timerlat_u.c`.

## Dependencies and Integration Points

It depends on `cpu_set_t` and `struct sched_attr` being visible from included common headers in users. It is integrated by timerlat top/hist common setup when `--user-threads` or user workload mode is requested.

## Risks and Edge Cases

The structure is not internally synchronized, so callers must coordinate flag lifetime with the dispatcher thread. Pointer fields must outlive the dispatcher. Missing CPU set means the implementation treats all CPUs as candidates.

## Test Signals

Build tests should ensure the header compiles in timerlat users, and runtime tests should verify `should_run`/`stopped_running` transitions with dispatcher lifecycle.

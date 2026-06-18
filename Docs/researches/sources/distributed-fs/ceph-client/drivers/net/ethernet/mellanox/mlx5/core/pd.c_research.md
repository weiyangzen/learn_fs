# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pd.c

## Purpose

`pd.c` is a minimal mlx5 protection-domain command wrapper. It allocates and deallocates firmware PD numbers used by consumers that need hardware protection-domain isolation, such as RDMA and queue/resource objects.

## Important APIs, Types, and Functions

`mlx5_core_alloc_pd()` builds an `ALLOC_PD` command, executes it with `mlx5_cmd_exec_inout()`, and returns the firmware `pd` field through `pdn` on success. `mlx5_core_dealloc_pd()` builds a `DEALLOC_PD` command with the caller's PD number and sends it with `mlx5_cmd_exec_in()`. Both functions are exported with `EXPORT_SYMBOL`, so in-kernel mlx5 consumers outside this compilation unit can use them.

## Control Flow

There is no local state machine. Callers allocate a PD before creating dependent firmware objects and must later deallocate it after those users are destroyed. Errors propagate directly from the command interface.

## State and Persistence Behavior

State is persisted in firmware as an allocated PD handle. This file does not cache handles or refcounts; ownership is entirely caller-managed. A successful allocation mutates only the caller-provided `pdn`.

## Dependencies and Integration Points

The file depends on command opcodes and layout macros from the mlx5 interface headers and on the core command executor. It integrates with RDMA, steering, transport, and other mlx5 modules that require a PD number.

## Risks and Test Signals

The main risk is caller misuse: leaking a PD on partial setup failure or deallocating while dependent objects still exist. Tests should include command-failure fault injection, create/destroy loops for PD consumers, and teardown ordering checks during driver unload and reset recovery.

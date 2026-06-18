# sources/distributed-fs/ceph-client/include/linux/firmware/imx/ipc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/ipc.h` defines the i.MX System Controller Firmware RPC message header and IPC accessors. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

Important definitions are `IMX_SC_RPC_VERSION`, `IMX_SC_RPC_MAX_MSG`, opaque `struct imx_sc_ipc`, `enum imx_sc_rpc_svc`, `struct imx_sc_rpc_msg`, `imx_scu_call_rpc`, and `imx_scu_get_handle`. Disabled `CONFIG_IMX_SCU` builds return `-ENOTSUPP`.

## Control Flow

SCFW service shims build RPC messages with version/size/service/function fields, call `imx_scu_call_rpc()`, and optionally wait for a response. Clients can obtain the default SCU IPC handle with `imx_scu_get_handle()`.

## State and Persistence Behavior

The header owns no state. IPC state is held by the SCU driver and firmware channel; RPC messages are transient stack/buffer data.

## Dependencies and Integration Points

It integrates with i.MX SCU firmware, mailbox/IPI transport, PM/RM/MISC/IRQ service headers, and platform drivers needing SCFW services.

## Risks and Edge Cases

`IMX_SC_RPC_MAX_MSG` constrains message size. `have_resp` controls synchronous response handling. Service/function IDs must match firmware ABI.

## Test Signals

SCU RPC tests with response/no-response calls, service shim tests, firmware timeout/error injection, and disabled-config build tests.

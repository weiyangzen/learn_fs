# sources/distributed-fs/ceph-client/include/linux/firmware/mediatek/mtk-adsp-ipc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/mediatek/mtk-adsp-ipc.h` declares MediaTek ADSP mailbox IPC structures and send API. The source was read as a complete 59-line file for this report.

## Important APIs, Types, and Functions

Important exports are request/response channel and opcode constants, mailbox enum values, opaque `struct mtk_adsp_ipc`, `struct mtk_adsp_ipc_ops`, `struct mtk_adsp_chan`, `struct mtk_adsp_ipc`, data accessors `mtk_adsp_ipc_set_data/get_data`, and `mtk_adsp_ipc_send`.

## Control Flow

Clients register reply/request callbacks, store private data, and call `mtk_adsp_ipc_send()` on a channel index with request/response opcode. Mailbox callbacks deliver firmware replies or requests into the provided ops.

## State and Persistence Behavior

`struct mtk_adsp_ipc` stores two mailbox channels, device pointer, ops, and private data. State is runtime IPC/mailbox state only.

## Dependencies and Integration Points

It depends on device, types, mailbox controller, and mailbox client APIs. It integrates with MediaTek ADSP firmware, audio DSP clients, and mailbox transport drivers.

## Risks and Edge Cases

Channel/opcode mismatches can deadlock request/response flows. Callback context and mailbox ownership must be handled by clients. There are no disabled stubs, so callers require the implementation to be linked.

## Test Signals

MediaTek ADSP IPC probe tests, mailbox loopback tests, invalid channel/opcode tests, callback ordering tests, and compile/link coverage.

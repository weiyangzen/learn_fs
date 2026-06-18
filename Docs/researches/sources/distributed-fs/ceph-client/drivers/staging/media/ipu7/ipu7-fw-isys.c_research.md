# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.c

## Purpose

This file provides ISYS firmware glue: syscom queue sizing, ISYS subsystem config allocation, boot-config initialization, firmware open/close wrappers, command token submission, response access, and debug dumps for stream/buffer payloads.

## Important APIs, Types, and Functions

Public functions include `ipu7_fw_isys_init()`, `ipu7_fw_isys_release()`, `ipu7_fw_isys_open()`, `ipu7_fw_isys_close()`, `ipu7_fw_isys_simple_cmd()`, `ipu7_fw_isys_complex_cmd()`, `ipu7_fw_isys_get_resp()`, `ipu7_fw_isys_put_resp()`, `ipu7_fw_isys_dump_stream_cfg()`, and `ipu7_fw_isys_dump_frame_buff_set()`.

## Control Flow

Initialization allocates `ipu7_syscom_context`, creates queue configs for ISYS output message/log/reserved queues and input device/per-stream queues, allocates DMA-visible `ipu7_insys_config`, enables syscom logger channel, disables watchdog timers, reads current ISYS frequency through buttress, syncs config, selects message major version by hardware generation, and initializes boot config. Complex command submission optionally flushes payload cache, obtains a syscom token for `stream_handle + IPU_INSYS_INPUT_MSG_QUEUE`, fills address/handle/type/stream/flag, puts the token, and wakes IS uC. Response access gets/puts tokens from the output message queue.

## State and Persistence Behavior

`isys->subsys_config` and `adev->syscom` persist from init to release. Queue token state is shared with firmware through boot-created syscom memory.

## Dependencies and Integration Points

It depends on ISYS ABI/config ABI, IPU7 boot, DMA, syscom, buttress frequency/wakeup, and ISYS stream/video code.

## Risks and Edge Cases

Queue selection relies on stream handle bounds. `ipu7_syscom_get_token()` returning NULL maps to `-EBUSY`. Payload cache flushing is manual. Init failure must release boot/subsystem allocations. Message major version differs between IPU8 and earlier hardware.

## Test Signals

Test init/release leaks, boot open/close, queue full command failure, stream open/capture/close commands, response token parsing, and debug dump coverage for multi-pin stream configs.

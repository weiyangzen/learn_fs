# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/msgfn.h

Purpose: enumerates R535 GSP asynchronous message/event function IDs starting at `0x1000`.

Important definitions: events include `GSP_INIT_DONE`, `GSP_RUN_CPU_SEQUENCER`, `POST_EVENT`, `RC_TRIGGERED`, `MMU_FAULT_QUEUED`, `OS_ERROR_LOG`, `UCODE_LIBOS_PRINT`, `PERF_BRIDGELESS_INFO_UPDATE`, `GSP_SEND_USER_SHARED_DATA`, and others. The macro-based `E()` pattern lets includers either build the enum or reuse the list with a custom macro.

Control flow and state: `gsp.c` registers notification handlers for several of these IDs and polls for `GSP_INIT_DONE` during initialization. Message queue transport in `rpc.c` compares incoming RPC function IDs to these values.

Dependencies and integration: paired with `rpcfn.h` and the message queue ABI in `gsp.h`/`rpc.c`. Event payload layouts are defined in headers such as `event.h`, `fifo.h`, and `gsp.h`.

Risks and tests: numeric drift would route messages to the wrong handler or cause init polling to time out. Tests should verify boot completion, event fanout, RC/MMU fault logging, PMU libos print capture, and ignored/drop events not causing queue stalls.

# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-rpmsg.h

## Purpose
Protocol and shared-state header for i.MX audio RPMsg PCM. It documents the SRTM audio packet format and defines command IDs, message types, response codes, format/channel codes, packet structures, workqueue nodes, timers, and the central `rpmsg_info` state object.

## APIs, Types, and Functions
Defines `RPMSG_TIMEOUT`, TX/RX command macros from `TX_OPEN` through `RX_POINTER`, message counts, `MSG_TYPE_A/B/C`, response constants, RPMsg audio format/channel codes, category/version constants, stream aliases `TX`/`RX`, packed structs `rpmsg_head`, `param_s`, `param_r`, `rpmsg_s_msg`, `rpmsg_r_msg`, `rpmsg_msg`, plus `work_of_rpmsg`, `stream_timer`, `dma_callback`, and `struct rpmsg_info`.

## Control Flow, State, and Persistence
The header has no executable logic, but `struct rpmsg_info` is the persistent state shared between RPMsg bus callbacks and PCM operations: the parent endpoint, command completion, PM QoS request, response scratch message, per-command message array, notification cache, ordered workqueue ring, drop counters, period counts, period callbacks, send function pointer, per-stream spinlocks, workqueue spinlock, send mutex, and per-stream timers.

## Dependencies and Integration
Depends on PM QoS, interrupts/work structs, and ALSA DMA-engine headers. Included by both `imx-audio-rpmsg.c` and `imx-pcm-rpmsg.c`, and indirectly defines the ABI expected by the remote M-core firmware.

## Risks and Test Signals
Risks include packed little-endian protocol fields without explicit endian conversion, 32-bit buffer address fields limiting DMA addressability, comments with stale names/typos, command-number ABI drift with firmware, and concurrency complexity concentrated in a public struct. Test signals are compile-time struct layout compatibility, firmware command/response interoperability, correct format/channel translation, and bidirectional period notifications.

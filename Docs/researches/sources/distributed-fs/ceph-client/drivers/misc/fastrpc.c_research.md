# sources/distributed-fs/ceph-client/drivers/misc/fastrpc.c

## Purpose
Qualcomm FastRPC driver that exposes misc devices for userspace processes to invoke methods on remote DSP protection domains over rpmsg. It manages sessions, DMA buffers, dmabuf mappings, secure memory assignment, process creation, memory map/unmap RPCs, and DSP capability queries.

## Important APIs, Types, And Functions
Core state is split across `struct fastrpc_channel_ctx` for an rpmsg DSP domain, `struct fastrpc_session_ctx` for compute callbacks, `struct fastrpc_device` for misc nodes, and `struct fastrpc_user` for each open file. Invocation state lives in `struct fastrpc_invoke_ctx`; mapped buffers use `struct fastrpc_map`; driver-owned coherent buffers use `struct fastrpc_buf`. Main operations include `fastrpc_internal_invoke()`, `fastrpc_get_args()`, `fastrpc_put_args()`, `fastrpc_map_create()`, `fastrpc_req_mmap()`, `fastrpc_req_mem_map()`, process creation helpers, ioctl dispatch, rpmsg probe/remove/callback, and compute-callback platform probe/remove.

## Control Flow
Module init registers compute-callback and rpmsg drivers. Rpmsg probe reads the DSP domain label, reserved memory, VMIDs, secure-domain policy, SoC DMA settings, creates secure/non-secure misc devices, initializes IDR/list state, and populates child compute-callback nodes. Opening a misc device allocates a user, gets a channel reference, reserves an available session, and joins the channel user list. Ioctls create or attach DSP processes, allocate DMA buffers, invoke remote methods, map/unmap local or remote memory, and query DSP attributes. An invocation copies scalar descriptors from userspace, builds metadata/page lists, maps dmabufs or copies inline input into a coherent packet, sends an rpmsg, waits for callback completion, copies inline outputs back, handles returned fdlist references, and releases context state. Rpmsg callbacks look up context IDs and complete waiters.

## State, Persistence, And Dependencies
State is volatile: channel reference counts, IDR context IDs, pending invokes, per-user maps/mmaps, session allocation, cached DSP attributes, remote heap, and secure VM assignments. It depends on rpmsg, platform bus, device tree, reserved memory, DMA coherent allocation, dma-buf, scatterlists, qcom SCM hypervisor assignment, miscdevice, IDR, completions, and UAPI structs in `uapi/misc/fastrpc.h`.

## Integration Points
Device nodes are named `fastrpc-<domain>` and optionally `fastrpc-<domain>-secure`. DT labels select ADSP/MDSP/SDSP/CDSP/GDSP behavior. Compute callback children provide session devices and SIDs. Userspace interacts solely through FastRPC ioctls and returned dma-buf fds.

## Risks
This is a high-risk boundary: userspace pointers, dma-buf fds, remote DSP firmware, and hypervisor memory permissions all interact. Interrupted invokes keep contexts pending and move mmap buffers to a channel list. Secure map cleanup must return memory to HLOS; failures can leave permissions altered. Some error paths intentionally leak fds after failed `copy_to_user()` because fd installation already occurred. Session removal marks matching SIDs invalid and decrements counts, which needs care with duplicated sessions. Domain security policy must correctly reject unsigned/signed PD misuse.

## Test Signals
Test each ioctl success and failure path, interrupted invokes, rpmsg removal during pending invokes, secure and non-secure device access policy, dmabuf map/unmap reference counts, copy_from/to_user failures, DSP unsupported capability API, reserved-memory VM assignment, compute-callback session duplication, context ID reuse, and process release on file close.

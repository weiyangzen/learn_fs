# sources/distributed-fs/ceph-client/include/linux/mhi_ep.h

## Purpose
Endpoint-side MHI framework API. It describes endpoint controller configuration, host-memory access callbacks, doorbell handling, context caches, endpoint device/driver objects, and power/transfer helpers.

## Important APIs/Types
`MHI_EP_DEFAULT_MTU` defines the default MTU. `mhi_ep_channel_config` and `mhi_ep_cntrl_config` describe endpoint channels and controller limits. `mhi_ep_db_info` stores doorbell mask/status. `mhi_ep_buf_info` describes endpoint/host transfer buffers and optional async completion callback. `mhi_ep_cntrl` holds MMIO, channels/events/commands, state machine, cached host contexts and physical addresses, doorbell state, locks, workqueue/work items, slab caches, IRQ and host-memory callbacks, state, offsets, IRQ, and enabled flag. `mhi_ep_device` and `mhi_ep_driver` define endpoint bus clients.

## Control Flow
An endpoint controller registers configuration, powers up, handles host doorbells and state changes through workqueue workers, and exposes channel devices to endpoint client drivers. Clients receive UL/DL callbacks and can queue SKBs to the host.

## State And Persistence
Persistent state includes host context caches, mapped endpoint memory for host contexts, doorbell status, transition/channel lists, workqueue state, slab caches, controller state, and enabled flag. Mutexes and spinlocks serialize event, state, and list operations.

## Dependencies And Integration Points
Depends on DMA direction and host MHI definitions. Integrates with endpoint PCI-like controllers, host memory mapping/read/write callbacks, IRQ raising, MHI state machines, and endpoint channel drivers.

## Risks
Host address mapping lifetime, async callback ordering, stale context caches, doorbell-list races, channel direction confusion, and incomplete controller callback validation are the key hazards.

## Test Signals
Endpoint controller registration, power-up/down, host doorbells, command/channel ring workers, UL/DL transfers, async completions, SKB queueing, queue-empty checks, reset handling, and teardown with outstanding buffers.

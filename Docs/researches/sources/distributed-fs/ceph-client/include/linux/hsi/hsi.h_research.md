# sources/distributed-fs/ceph-client/include/linux/hsi/hsi.h

## Purpose
`hsi/hsi.h` defines the High Speed Synchronous Serial Interface core API. It models HSI controllers, ports, clients, board info, TX/RX configuration, messages, port events, and client-driver registration.

## Important APIs, Types, And Functions
Important definitions include HSI message transfer types, configuration enums for stream/frame mode, synchronized/pipelined flow, round-robin/priority arbitration, message status values, and port event IDs. Core structures are `struct hsi_channel`, `struct hsi_config`, `struct hsi_board_info`, `struct hsi_client`, `struct hsi_client_driver`, `struct hsi_msg`, `struct hsi_port`, and `struct hsi_controller`. APIs include board info registration, port event register/unregister, client-driver register/unregister, message alloc/free, controller alloc/register/unregister, client creation/removal, DT client addition, `hsi_async()`, channel-name lookup, port claim/release, setup/flush, async read/write, and start/stop TX.

## Control Flow And State
Controller drivers allocate/register controllers and ports. Board info or DT creates clients under ports. Client drivers claim a port, configure TX/RX parameters, register event handlers, allocate scatterlist-backed messages, submit async reads/writes, start/stop TX, and receive completion callbacks. Ports serialize claims with a mutex, track shared/claimed state, hold current TX/RX config, invoke controller callbacks, and notify clients through a blocking notifier chain.

## Dependencies And Integration Points
It depends on the Linux device model, mutexes, scatterlists, lists, modules, and notifier chains. It integrates HSI controller drivers, HSI client protocol drivers, platform data/DT enumeration, and DMA-capable async transfer implementations.

## Risks
Risks include submitting operations without claiming the port, incompatible shared-port configurations, message lifetime and destructor ordering during flush, scatterlist ownership mistakes, notifier callback sleepability assumptions, and concurrent start/stop TX races. Inline helpers return `-EACCES` when the port is not claimed.

## Test Signals
Test controller registration, DT/board client creation, claim/release exclusive and shared modes, setup/flush permission failures, async read/write completion/error/destructor paths, port event notification, start/stop TX, and remove while messages are queued.

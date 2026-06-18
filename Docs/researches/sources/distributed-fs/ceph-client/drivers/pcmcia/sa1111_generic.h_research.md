# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.h

Purpose: Defines the SA1111 PCMCIA wrapper type and declares generic and board-specific SA1111 socket functions.

Important APIs and types: `struct sa1111_pcmcia_socket` embeds `struct soc_pcmcia_socket`, the owning `struct sa1111_dev`, and a linked-list pointer. `to_skt()` converts from common socket to wrapper. Declarations cover `sa1111_pcmcia_add()`, `sa1111_pcmcia_socket_state()`, `sa1111_pcmcia_configure_socket()`, and board init functions.

Control flow: No executable control flow except the inline container conversion. The type is used by `sa1111_generic.c` to manage multiple sockets under one SA1111 device.

State and persistence: The wrapper is per-socket runtime state allocated during `sa1111_pcmcia_add()` and stored in the SA1111 device driver-data list.

Dependencies and integration points: Includes `soc_common.h` and `sa11xx_base.h`; depends on SA1111 device definitions visible to including files.

Risks: The linked-list ownership is manual and must be removed in tandem with `soc_pcmcia_remove_one()`. Board init declarations must match enabled implementations.

Test signals: Compile coverage for SA1111 PCMCIA configs and successful `to_skt()` use in status/configure callbacks.

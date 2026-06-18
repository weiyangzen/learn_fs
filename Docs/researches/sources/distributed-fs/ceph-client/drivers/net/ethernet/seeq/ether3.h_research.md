# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/ether3.h

Purpose: Defines the register offsets, command/status/config bits, TX/RX header/status flags, buffer memory layout, queue limits, and private state structures for the Ether3 driver.

Important APIs and types: Register macros derive addresses from `priv(dev)->seeq`, including command/status, config registers, buffer window, receive/transmit pointers, and DMA address. Command/status bits control RX/TX enablement, FIFO direction, interrupt enables/acks, and DMA/FIFO operations. TX/RX header flags describe chained local-memory packets. Buffer layout divides local RAM into TX and RX regions with 16 TX slots. `struct dev_priv` stores cached registers, ring pointers, timer, netdev, and broken flag. `struct ether3_data` distinguishes card variants by name and base offset.

State and dependencies: This header is tightly coupled to `ether3.c` and Acorn expansion-card mapping. It embeds state layout used by `netdev_priv()` and register macros used throughout the driver.

Risks and test signals: Since register macros evaluate `priv(dev)`, callers must pass a valid registered netdev with initialized private state. Buffer constants must remain compatible with TX slot sizing and RX wrap logic. Tests should validate register address calculations for Ether3/EtherB offsets, TX/RX flag interpretation, and build coverage after any private-structure changes.

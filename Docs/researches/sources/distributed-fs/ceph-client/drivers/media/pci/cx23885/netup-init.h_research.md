# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.h

Purpose: declares the NetUP board initialization hook.

Important APIs and types: exports `netup_initialize(struct cx23885_dev *dev)`.

Control flow: cx23885 board setup calls this function for NetUP cards to program A/V core PLL registers. The implementation handles I2C access internally.

State and persistence: the header has no state. Its function mutates hardware clock configuration through the parent device.

Dependencies and integration points: requires consumer visibility of `struct cx23885_dev`. It is the integration boundary for NetUP-specific AUX clock initialization.

Risks: unlike many kernel headers, it has no include guard; repeated inclusion is harmless for this single extern declaration but inconsistent with local style. The API exposes no error return even though initialization can fail at the I2C layer.

Test signals: compile coverage and board-level clock bring-up validate this declaration.

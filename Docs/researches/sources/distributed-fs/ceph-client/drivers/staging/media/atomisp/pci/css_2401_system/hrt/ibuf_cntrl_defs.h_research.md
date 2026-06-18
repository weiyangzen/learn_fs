# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/ibuf_cntrl_defs.h

Purpose: defines register indices, command/ack token fields, status fields, and command constants for the input-buffer controller.

Important APIs/types/functions: macros describe register alignment, per-process register counts, timeout bits, stream2mmio token aliasing, ack token layout, shared registers, per-process config/status registers, and commands such as initialize, store online frame, store offline frame, and false ack.

Control flow: no runtime flow; constants drive IBUF MMIO programming and state interpretation.

State and persistence: no software state. Hardware state is represented by registers named here.

Dependencies and integration: includes Stream2MMIO and DMA v2 definitions because IBUF command/ack formats bridge those blocks.

Risks and test signals: off-by-one register definitions can corrupt DMA/IBUF setup. Tests should validate online/offline store command encoding, ack token extraction, and consistency with `ibuf_ctrl_local.h` state field order.

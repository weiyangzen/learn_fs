# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl_local.h

Purpose: defines state snapshot structures for IBUF controller shared and per-process registers.

Important APIs/types/functions: `ibuf_ctrl_proc_state_t` records command/ack, item/store counts, DMA channel/command, input-buffer and destination addresses/strides/end addresses, sync/store commands, element packing, current counts/addresses, DMA command count, and FSM states. `ibuf_ctrl_state_t` stores shared recalculation/arbiter status and an array of process states.

Control flow: no direct logic; private/register-dump code fills these structs.

State and persistence: snapshot-only; hardware state remains in registers.

Dependencies and integration: depends on `ibuf_ctrl_global.h` for register definitions and `N_STREAM2MMIO_SID_ID`.

Risks and test signals: the header includes itself after `ibuf_ctrl_global.h`, which is harmless under include guards but suspicious. Tests should validate state capture layout against `_IBUF_CNTRL_*` register definitions and max SID counts.

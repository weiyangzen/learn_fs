# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_local.h

Purpose: defines the ISYS IRQ controller state snapshot structure.

Important APIs/types/functions: `isys_irqc_state_t` stores `edge`, `mask`, `status`, `enable`, and `level_no`. The write-only `clear` register is intentionally omitted/commented.

Control flow: no direct flow; private helpers populate and dump this structure.

State and persistence: snapshot-only runtime state.

Dependencies and integration: depends on `type_support.h` for `hrt_data` and is used by `isys_irq_private.h`.

Risks and test signals: reading a write-only clear register is avoided by design. Tests should confirm state capture covers readable registers and does not attempt invalid reads.

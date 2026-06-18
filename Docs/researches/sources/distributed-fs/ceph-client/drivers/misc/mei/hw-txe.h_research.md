<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.h

Purpose: declares TXE backend constants, private hardware state, helpers, and public entry points.

Important APIs and types: interrupt-cause bits map readiness, aliveness, output-doorbell, and input-ready events into a flattened mask. `struct mei_txe_hw` stores SEC/bridge BAR pointers, cached aliveness/readiness, write slots, aliveness waitqueue, and translated interrupt causes. Public functions include `mei_txe_dev_init()`, quick/thread IRQ handlers, and `mei_txe_aliveness_set_sync()`.

Control flow: PCI TXE probe code allocates a `mei_device` with TXE private state via `mei_txe_dev_init()`, maps BARs into `mem_addr`, requests IRQs using the declared handlers, and starts the common MEI core. Runtime PM can call aliveness synchronization to keep or release the SeC.

State and persistence: defines volatile per-device TXE state accessed with `to_txe_hw(dev)`. No persistent storage.

Dependencies and integration: includes IRQ return types, shared `hw.h`, and TXE register definitions. The allocation layout uses `hw_txe_to_mei()` and `to_txe_hw()` casts.

Risks: the `mem_addr` field is a pointer to a const array of BAR mappings; probe must keep that array alive for device lifetime. Cast-based embedding assumes allocation layout exactly matches `mei_txe_dev_init()`.

Test signals: compile/probe on TXE PCI devices, interrupt flattening behavior, runtime PM aliveness transitions, and KASAN coverage for BAR pointer lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.h -->

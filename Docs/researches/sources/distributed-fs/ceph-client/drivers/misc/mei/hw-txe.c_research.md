<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.c

Purpose: implements the `mei_hw_ops` backend for Intel TXE/SeC hardware, which differs from classic ME by using fixed-size IPC payload RAM, input/output doorbells, readiness/aliveness registers, and hierarchical interrupt registers across SEC and bridge BARs.

Important APIs and functions: exported functions are `mei_txe_dev_init()`, `mei_txe_irq_quick_handler()`, `mei_txe_irq_thread_handler()`, and `mei_txe_aliveness_set_sync()`. Local helpers implement SEC/bridge register access, aliveness request/response polling or waiting, readiness setup/clear/wait, interrupt clear/enable/disable/translation, payload read/write, reset/start, FW status reads, PG state reporting, and the `mei_txe_hw_ops` table.

Control flow: reset disables interrupts, reconciles aliveness request/response, clears aliveness if asserted, and clears host readiness. Start enables interrupts, waits for SeC readiness, clears stale output-doorbell status, asserts aliveness, enables input-ready interrupts, marks output ready, and sets host ready. Writes require aliveness and input-ready status, place header/data dwords into SEC input payload RAM, mark `hw->slots = 0`, and ring input doorbell. Reads consume the bridge output payload after the header and then mark output ready. The quick handler translates/acks pending high-level, bridge, and SEC interrupts into `hw->intr_cause`; the threaded handler processes readiness, aliveness, output-doorbell reads, input-ready writes, and callback completion.

State and persistence: `struct mei_txe_hw` stores BAR pointers, cached aliveness/readiness, available slots, waitqueue for aliveness responses, and `intr_cause` bits. State is volatile and rebuilt on reset/probe.

Dependencies and integration: depends on PCI config access, ktime/jiffies delays, runtime PM, common MEI client/HBM/interrupt helpers, and `hw-txe-regs.h`. Like `hw-me.c`, it plugs into common MEI core solely through `mei_hw_ops`.

Risks: TXE write path warns if `data` is NULL even when only a header is written, which differs from classic ME semantics and relies on callers providing a payload pointer. Aliveness transitions use both interrupt wait and polling depending on reset stage; missed transitions produce `-ETIME`/`-EIO`. The interrupt hierarchy must be acknowledged in correct order. The read-slot count always returns the fixed payload depth, so header length validation in common interrupt code is the main protection against malformed firmware output.

Test signals: reset/start on TXE platforms, aliveness wait/poll timeout tests, input-ready write queue drain, output-doorbell HBM/client message reception, MSI and non-MSI interrupt handling, repeated suspend/resume, and fault injection for readiness loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe-regs.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe-regs.h

Purpose: defines register offsets, bit masks, BAR indexes, firmware status offsets, timeouts, payload size, and SATT range constants for Intel TXE/SeC MEI hardware.

Important APIs and constants: BAR indexes are `SEC_BAR` and `BRIDGE_BAR`. Firmware status offsets are `PCI_CFG_TXE_FW_STS0` and `PCI_CFG_TXE_FW_STS1`. IPC registers cover input doorbell/status/payload, host interrupt status/mask, shared/output payload, high-level interrupt hierarchy, readiness, aliveness, output status, and bridge/SATT translation registers. Bit masks identify readiness, aliveness, output-doorbell, input-ready, illegal memory, crypto-key errors, and timer overflow interrupt bits. `PAYLOAD_SIZE` is 64 bytes, matching TXE fixed IPC payload size.

Control flow: no executable logic. `hw-txe.c` uses these constants to synchronize aliveness/readiness, write payloads, read output payloads, translate interrupt causes, acknowledge interrupt hierarchy, and expose firmware status.

State and persistence: no driver state here; constants map hardware state.

Dependencies and integration: includes `hw.h` for shared MEI slot sizing and bit helpers. The register map supports the TXE `mei_hw_ops` implementation.

Risks: TXE uses two BARs and hierarchical interrupts; wrong offset or acknowledgment ordering can lose interrupts or wedge IPC. `PAYLOAD_SIZE` drives buffer-depth calculations, so changing it without hardware support would corrupt message framing.

Test signals: TXE hardware probe/start, aliveness/readiness timeouts, input-ready interrupt, output-doorbell read path, firmware status sysfs output, and stress tests of repeated reset/start cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-txe-regs.h -->

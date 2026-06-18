# sources/distributed-fs/ceph-client/drivers/scsi/nsp32.h

Purpose: hardware contract and state definitions for `nsp32.c`. It defines PCI IDs/model names, normal and indexed register offsets, bit masks, SCSI bus phase encodings, DMA/autoparameter layouts, SDTR constants, timing values, and per-host/target/LUN structures.

Important APIs/types: `nsp32_sgtable`, `nsp32_sglun`, and `nsp32_autoparam` are packed little-endian structures consumed by hardware DMA. `nsp32_lunt` stores one active command and SG cursor per target/LUN. `nsp32_target` stores negotiated sync period/offset, sync register, ack width, flags, and speed limit. `nsp32_hw_data` is the full host state object. `nsp32_priv()` returns per-command status storage.

Control flow/state: `BUSMON_*`, `BUSPHASE_*`, and `SCSI_EXECUTE_PHASE` flags are the ISR's protocol vocabulary. `TO_SYNCREG()`, `ASYNC_OFFSET`, and `SYNC_OFFSET` support SDTR conversion. Defined state persists for the host lifetime: coherent SG/autoparam pools, current nexus, per-target negotiation state, message buffers, transfer method, clock, and EEPROM-derived limits.

Dependencies/integration: depends on Linux SCSI, PCI, DMA address, integer, and bit helpers and is consumed by `nsp32.c`, `nsp32_io.h`, and `nsp32_debug.c`.

Risks/test signals: register access width restrictions are explicit and must be respected. `MAX_LUN` is 8 despite newer SCSI allowing more. SG table sizing and packing must match allocation and hardware expectations. Test with build/sparse coverage, successful SG DMA, host-info register reads, SDTR negotiation, and reset behavior.

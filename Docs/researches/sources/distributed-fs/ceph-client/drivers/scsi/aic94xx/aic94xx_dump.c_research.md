# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.c

Purpose: debug-only register and frame dump implementation for AIC94xx central sequencer (CSEQ), link sequencers (LSEQ), scratch pages, mode pages, and received frames.

Important APIs/types/functions: compiled under `ASD_DEBUG`. `asd_dump_seq_state()` dumps CSEQ plus selected LSEQs. `asd_dump_cseq_state()` prints ARP2, IOP, CIO, scratch, MIP, and MDP registers. `asd_dump_lseq_state()` prints per-link sequencer state across common and mode-specific pages. `asd_print_lseq_cio_reg()` handles table-driven LSEQ CIO register widths. `asd_dump_frame_rcvd()` logs IDENTIFY/FIS frame bytes under `frame_rcvd_lock`.

Control flow: error handlers call `asd_dump_seq_state()` after DMA/sequencer failures. It always dumps CSEQ and iterates `lseq_mask` through `for_each_sequencer()` for LSEQ state. Register print macros read byte/word/dword/qword values through the normal register accessor layer.

State and persistence: no persistent state. It observes live hardware registers and PHY `frame_rcvd` buffers, then writes kernel log output.

Dependencies and integration: depends on generated register definitions, `aic94xx_reg` accessors, `aic94xx_sas` structures, debug logging macros, and ISR error paths in `aic94xx_hwi.c`.

Risks and test signals: dump routines read large numbers of hardware registers, so using them on wedged hardware can amplify faults or log volume. Width/mode tables must match silicon register layout. Signals include debug builds, forced sequencer errors, frame-received dumps for SSP/STP, and ensuring no dump code is emitted when `ASD_DEBUG` is off.

# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.c

Purpose: this file loads aic94xx sequencer firmware, downloads CSEQ/LSEQ microcode, verifies it, initializes sequencer scratch/CIO/SCB/DDB state, starts sequencers, and updates DDB 0 link maps as ports form.

Important APIs/types/functions: exported functions are `asd_init_seqs()`, `asd_start_seqs()`, `asd_release_firmware()`, and `asd_update_port_links()`. Key internals pause/unpause CSEQ/LSEQs, verify/download code (`asd_verify_cseq()`, `asd_verify_lseq()`, `asd_download_seq()`), request/parse firmware (`asd_request_firmware()`), initialize CSEQ/LSEQ scratch pages and CIO registers, initialize SCB sites, initialize DDB 0 and DDB sites, and start the sequencer program counters.

Control flow and state: `asd_init_seqs()` requests `aic94xx-seq.fw`, validates checksum/table sizes/major version, sets vector/code globals, downloads CSEQ then LSEQ code using overlay DMA (or PIO fallback), verifies downloaded RAM, and initializes all sequencer state. Setup zeros DDB/SCB sites, builds a valid SCB free list excluding invalid sites, initializes CSEQ queues/done-list DMA pointers, initializes per-link OOB/timer/interrupt state, writes SAS addresses, and sets DDB 0. `asd_start_seqs()` unpauses CSEQ and each enabled LSEQ at firmware-provided idle-loop addresses.

Persistence behavior: firmware data is cached in static globals until `asd_release_firmware()`. Hardware state includes instruction RAM, scratch RAM, SCB/DDB context memory, interrupt masks, DMA pointers, and DDB 0 port/link bits. `asd_update_port_links()` mutates DDB 0 under `ddb_lock` with retry-on-update semantics.

Dependencies and integration points: depends on Linux firmware loader, PCI device naming, DMA allocation, register helpers, `aic94xx_reg_def.h` offsets, `aic94xx_sas.h` DDB/SCB layouts, and HWI initialization order (`asd_init_seqs()` before `asd_start_seqs()`). `aic94xx_scb.c` calls `asd_update_port_links()` after port formation.

Risks: firmware ABI mismatch, checksum bugs, or offset drift can prevent probe or corrupt command execution. Static firmware globals imply shared firmware state across adapters. Overlay DMA errors must restore interrupt enable state. SCB free-list construction changes queue capacity and must respect hardware errata macros.

Test signals: missing firmware, bad checksum, bad major version, CSEQ/LSEQ verify mismatch, no enabled phys, multi-phy download fallback, successful start on all enabled phys, and port-map updates after hotplug/wide-port formation.

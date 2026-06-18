# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/lm.h

Purpose: declares PDS live-migration file state and transition helpers.

Important types and APIs: `struct pds_vfio_lm_file` captures anonymous file, lock, sizes, page memory, pages, SG table, firmware SGL, sequential lookup cache, and disabled flag. Prototypes expose the locked state-step function and save/restore file cleanup helpers.

Control flow and integration: this header connects `vfio_dev.c` migration ops to `lm.c`, and lets reset/close paths release active files.

Risks and test signals: the struct mixes file lifetime, DMA mapping metadata, and sequential read/write cache; tests should stress cleanup on partially initialized files and repeated state transitions.

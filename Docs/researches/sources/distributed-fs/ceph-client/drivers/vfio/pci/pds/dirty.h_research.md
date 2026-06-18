# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/dirty.h

Purpose: defines PDS dirty logging state and declares VFIO log-op entry points.

Important types: `struct pds_vfio_region` tracks per-region host sequence/ack bitmaps, bitmap bytes, IOVA start/size/page size, firmware SGL, DMA address, device bitmap byte offset, and SGE count. `struct pds_vfio_dirty` stores region array, count, and enabled flag.

Control flow and integration: higher layers call enable/disable helpers from migration state paths and expose VFIO log callbacks through `vfio_dev.c`. The structs are filled and freed in `dirty.c`.

Risks and test signals: consumers must hold `state_mutex` around dirty state changes. Tests should cover enabled flag transitions and cleanup after reset or close.

# sources/distributed-fs/coda/coda-src/partition/inodeops.h

Purpose: declares the legacy inode operation wrappers and direct header/list APIs for callers outside the partition backend implementation.

Important APIs: exports create/open/read/write/increment/decrement by device/inode, header get/put by `DiskPartition *`, and `ListCodaInodes` signature. It includes partition, vicetab, and inode metadata types.

Risks/integration: header couples callers to both legacy `Device` lookup and newer partition structures. The declared `ListCodaInodes` wrapper is not implemented in `inodeops.c` in this subset, so link usage must be checked. Test signal is build/link coverage and backend tests.

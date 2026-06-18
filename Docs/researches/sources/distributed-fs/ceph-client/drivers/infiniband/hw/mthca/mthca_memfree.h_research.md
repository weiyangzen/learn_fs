# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.h

Purpose: declares the mem-free context-memory and doorbell-record abstractions shared across the mthca driver.

Important APIs/types/functions: defines `MTHCA_ICM_PAGE_SHIFT`, `MTHCA_ICM_PAGE_SIZE`, `MTHCA_DB_REC_PER_PAGE`, `struct mthca_icm_chunk`, `struct mthca_icm`, `struct mthca_icm_table`, `struct mthca_icm_iter`, `struct mthca_db_page`, `struct mthca_db_table`, and `enum mthca_db_type`. It declares ICM allocation/table lookup APIs plus user and kernel doorbell mapping/allocation APIs.

Control flow: inline iterator helpers `mthca_icm_first`, `mthca_icm_last`, `mthca_icm_next`, `mthca_icm_addr`, and `mthca_icm_size` provide firmware command code with a simple page-by-page view over chunked scatterlists. Doorbell types encode firmware record meanings for CQ set-consumer-index, CQ arm, SQ, RQ, SRQ, and group separators.

State and persistence: structures describe in-memory runtime state: ICM chunks carry scatterlist pages and DMA mappings, tables carry object-to-ICM chunk mappings with mutex protection, and doorbell tables track coherent DB pages and bitmap allocation.

Dependencies and integration: included by `mthca_memfree.c`, QP/SRQ/CQ/MR setup, and UAR handling. It depends on Linux lists, mutexes, scatterlists, DMA addresses, and mthca device/uar declarations.

Risks: callers must respect object-size/chunk-size assumptions and mem-free versus Tavor behavior. `mthca_icm_table.icm[]` is a flexible array with `__counted_by(num_icm)`, so allocation size must match `num_icm`. Doorbell indices are shared with userspace ABI data and must remain stable.

Test signals: compile coverage across supported kernel configs, mem-free QP/CQ/SRQ creation, table refcount get/put tests, and sparse/lockdep checks around iterator and mutex use.

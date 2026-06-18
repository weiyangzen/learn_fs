# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.c

Purpose: maps Broadcom hardware, firmware, and qplib RoCE statistics into RDMA-core hardware stats and Performance Management Agent MAD counters.

Important APIs and functions: `bnxt_re_ib_alloc_hw_port_stats()` allocates RDMA stats descriptors. `bnxt_re_ib_get_hw_stats()` fills standard and extended RDMA counters. `bnxt_re_assign_pma_port_counters()` and `bnxt_re_assign_pma_port_ext_counters()` populate PMA MAD response payloads. Helpers `bnxt_re_copy_err_stats()`, `bnxt_re_copy_ext_stats()`, and `bnxt_re_get_ext_stat()` translate qplib structures into RDMA stats indices.

Control flow: stats allocation chooses standard versus extended counter count based on chip generation. Stats retrieval first copies L2 hardware DMA stats from `rdev->qplib_ctx.stats.dma`, then, if `BNXT_RE_FLAG_ISSUE_ROCE_STATS` is set, queries firmware RoCE error counters and optional extended stats. Query failures clear the issue flag to avoid repeated failing firmware requests. PMA assignment chooses between L2 DMA stats and RoCE-only extended stats depending on chip generation and VF status, then writes big-endian PMA fields.

State and persistence: hardware counters are read from DMA-backed qplib stats memory and firmware query results are cached in `rdev->stats.rstat.errs` and `rdev->stats.rstat.ext_stat`. RDMA stats values are snapshots supplied to callers and are not persisted by this file.

Dependencies and integration points: depends on RDMA MAD/PMA structures, `rdma_hw_stats`, qplib SP functions (`bnxt_qplib_get_roce_stats()`, `bnxt_qplib_qext_stat()`), qplib chip-generation predicates, and driver flags from `bnxt_re.h`. `ib_verbs.c` calls the PMA assignment functions from `bnxt_re_process_mad()`.

Risks: counter units differ: PMA data counters are in 32-bit words, so byte counters are divided by four. Standard PMA counters truncate to 32 or 16 bits. Extended stats availability varies by capability flags, chip generation, and VF mode. Clearing `BNXT_RE_FLAG_ISSUE_ROCE_STATS` on one query failure can hide later-recovering firmware stats.

Test signals: RDMA sysfs/hw_stats reads on P5/P7 and older chips, PF versus VF PMA counter validation, firmware error injection for RoCE and extended stat queries, endian/unit checks for MAD responses, and traffic tests that increment send, receive, CNP/ECN, atomic/read/write, and error counters.

# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.c

Purpose: converts requested mthca resource counts into an HCA context-memory layout and fills both device limits and `INIT_HCA` firmware parameters.

Important APIs/functions: exports `mthca_make_profile`; defines resource identifiers for QP, EEC, SRQ, CQ, EQP, EEEC, EQ, RDB, MCG, MPT, MTT, UAR, UDAV, and UARC. Constants set 32 EQs and 32768 PDs.

Control flow: builds a temporary resource array with entry sizes from `mthca_dev_lim` and requested counts from `mthca_profile`, scales sizes by count, enforces at least one page per mem-free resource, chooses memory base/available size for mem-free ICM or Tavor DDR, sorts resources by decreasing size, assigns packed starts, checks total size against available HCA memory, then writes per-resource bases/log sizes into `init_hca` and `dev->limits`.

State and persistence: produces runtime initialization state: resource base addresses, log table sizes, split multicast group counts, MTT/FMR reservation limits, UARC layout, and PD capacity. No persistent storage exists beyond the initialized device.

Dependencies and integration: called during device bring-up before `INIT_HCA`; uses firmware-reported entry sizes and limits, driver flags such as `MTHCA_FLAG_SINAI_OPT`, mem-free detection, and DDR/firmware layout from `dev`.

Risks: bad requested counts can overflow memory budget or produce invalid log sizes. MCG count is split in half between primary MGMs and AMGM overflow entries. Sinai memory-key throughput optimization is disabled when MPT table size is too large. 32-bit Tavor reserves FMR MTTs to avoid excessive vmalloc pressure.

Test signals: probe with Tavor and mem-free devices, vary module/profile resource requests, validate `INIT_HCA` values against firmware acceptance, and test low-memory profile rejection diagnostics.

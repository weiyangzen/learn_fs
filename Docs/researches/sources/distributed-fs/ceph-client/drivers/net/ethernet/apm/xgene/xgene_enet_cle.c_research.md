## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_cle.c

Purpose: programs the X-Gene 10G classifier/preclassifier engine for parser tree routing and RSS setup in XGMII mode.

Important APIs, types, and functions: conversion helpers pack sideband, indirection-table, database-pointer, key-node, and extended-word decision-node structures into hardware register words. `xgene_cle_dram_wr` writes CLE DRAM regions through indirect command registers and polls completion. Static `xgene_init_ptree_dn` encodes the parser tree for Ethernet/IPv4/TCP/UDP decisions. `xgene_cle_setup_node`, `xgene_cle_setup_dbptr`, and `xgene_cle_setup_ptree` write nodes and result pointers and enable the tree. RSS helpers write sideband packet RAM, random IPv4 hash secret keys, and a 128-entry indirection table that maps to RX rings and buffer pools. `xgene_enet_cle_init` builds default accept/drop DB pointers and installs `xgene_cle3in_ops`.

Control flow, state, and persistence: `xgene_enet_init_hw` configures `pdata->cle` and calls `cle_ops->cle_init` only for XGMII. CLE state is stored in hardware DRAM and in `pdata->cle` metadata such as parser count, active parser, start node, start DB pointer, and jump bytes. RSS secret keys are random at initialization and not persisted across reset.

Dependencies and integration points: uses structures and constants from `xgene_enet_cle.h`, ring IDs from `xgene_enet_main.c`, destination queue numbers from `xgene_enet_dst_ring_num`, and MMIO base `pdata->cle.base` set by resource discovery.

Risks: classifier table programming is tightly packed and difficult to validate visually. A bad DB pointer can drop all traffic or route packets to the wrong queue/buffer pool. Command polling returns `-EBUSY` on timeout, so hardware stalls block probe. RSS keys are random, complicating deterministic flow tests.

Test signals: XGMII probe should complete CLE init; multi-queue RSS traffic should distribute across RX queues; invalid command timeout tests should fail probe cleanly; non-XGMII modes should bypass CLE instead.

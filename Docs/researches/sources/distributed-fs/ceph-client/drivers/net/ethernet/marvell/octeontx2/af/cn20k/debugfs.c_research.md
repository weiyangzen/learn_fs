# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.c

Purpose: Adds CN20K-specific debugfs views for NPC MCAM allocator state and pretty-printers for CN20K NIX/NPA hardware context structures. It is observability code used by the RVU AF debugfs infrastructure.

Important APIs/types/functions: Debugfs show functions are `npc_mcam_layout_show()`, `npc_mcam_default_show()`, `npc_vidx2idx_map_show()`, `npc_idx2vidx_map_show()`, and `npc_defrag_show()`, each wrapped with `DEFINE_SHOW_ATTRIBUTE`. Public lifecycle functions are `npc_cn20k_debugfs_init()` and `npc_cn20k_debugfs_deinit()`. Public context printers are `print_nix_cn20k_sq_ctx()`, `print_nix_cn20k_cq_ctx()`, `print_npa_cn20k_aura_ctx()`, and `print_npa_cn20k_pool_ctx()`.

Control flow: Init creates debugfs files under `rvu->rvu_dbg.npc`: `mcam_layout`, `mcam_default`, `vidx2idx`, `idx2vidx`, and `defrag`. The layout view walks NPC subbanks under each subbank lock and prints occupied MCAM entries, PF ownership, and virtual index mappings for x4 or x2 key modes. Default view walks PF mappings and asks `npc_cn20k_dft_rules_idx_get()` for broadcast, multicast, promisc, and unicast default rule indices. The xarray views dump virtual-to-real and real-to-virtual MCAM mappings. Defrag view prints pending/recorded MCAM defragmentation moves under `npc_priv->lock`. Context printers emit individual bitfields from CN20K SQ/CQ/aura/pool admin-queue responses to a `seq_file`.

State and persistence: Debugfs files are transient kernel objects. The displayed state is live NPC private state: subbank bitmaps, xarrays, defrag list, and NIX/NPA context responses. No state is modified except debugfs registration/removal.

Dependencies and integration: Depends on Linux debugfs/seq_file, xarray, NPC CN20K private structures in `cn20k/npc.h`, and context struct layouts from `struct.h`. AF debugfs setup calls `npc_cn20k_debugfs_init()`, and generic debugfs code can call the context printers for CN20K AQ responses.

Risks: Debugfs readers race with allocator changes unless all relevant locks are held; subbank and defrag paths lock, but xarray dumps rely on xarray iteration semantics. Printing raw context fields can go stale if CN20K struct layouts change. `npc_cn20k_debugfs_deinit()` removes the whole NPC debugfs subtree, which must be coordinated with non-CN20K files under the same directory.

Test signals: Mount debugfs and read all created files under active MCAM allocations, virtual allocations, and defrag activity. CN20K AQ context debug output should match hardware dumps and not sleep or crash under concurrent rule changes.

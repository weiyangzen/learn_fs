# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_npc.h

Purpose: declares the small public interface exported by the core NPC implementation to sibling RVU AF modules. It exposes KPU/MKEX profile loading, KPU action programming, firmware database profile mapping, and MCAM bitmap bit updates.

Important APIs and types: `npc_enable_mask()` returns the KPU entry-disable mask used when enabling only programmed entries. `npc_load_kpu_profile()` selects and prepares the default or custom KPU parser profile in `rvu->kpu`. `npc_config_kpuaction()` writes one KPU or PKIND action pair to hardware. `npc_fwdb_prfl_img_map()` maps the firmware database profile image and returns its mapped address and size. `npc_mcam_set_bit()` and `npc_mcam_clear_bit()` are bitmap helpers used by MCAM resource allocation and reservation paths.

Control flow role: this header lets CN20K-specific code and other NPC companion files reuse common KPU action and MCAM bitmap primitives without exposing the full `rvu_npc.c` internals. The declared functions are called during parser profile initialization, MKEX/KPU profile selection, MCAM resource setup, and special-purpose entry reservation.

State and persistence: no state is stored in the header. The functions it declares mutate `rvu->kpu`, `rvu->kpu_fwdata`, `rvu->kpu_prfl_addr`, `rvu->hw->mcam` bitmaps/free counts, and NPC AF KPU/PKIND registers.

Dependencies and integration: depends on forward declarations from the including C files for `struct rvu`, `struct npc_kpu_profile_action`, and `struct npc_mcam`. It is consumed by `rvu_npc.c`, `rvu_npc_fs.c`, and CN20K NPC support code in this driver directory.

Risks: the bitmap helpers require `mcam->lock` to be held, as documented in their implementation; misuse can corrupt the forward and reverse allocation bitmaps or free count. `npc_config_kpuaction()` is a hardware ABI helper, so callers must pass profile data that matches the targeted KPU/PKIND entry layout and silicon generation. The firmware profile mapping helper returns an I/O mapping that must be unmapped by the caller or retained consistently in `rvu`.

Test signals: compile coverage should catch prototype drift. Runtime validation comes from successful KPU profile programming, CN20K parser initialization, MCAM allocation/free accounting, and no leaks from firmware database profile mapping/unmapping.

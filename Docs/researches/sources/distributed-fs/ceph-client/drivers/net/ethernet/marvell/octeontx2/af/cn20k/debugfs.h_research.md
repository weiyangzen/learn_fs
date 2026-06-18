# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.h

Purpose: Declares CN20K debugfs initialization/teardown functions and context pretty-printers for NIX and NPA admin-queue response structures.

Important APIs/types/functions: The header exposes `npc_cn20k_debugfs_init()`, `npc_cn20k_debugfs_deinit()`, `print_nix_cn20k_sq_ctx()`, `print_nix_cn20k_cq_ctx()`, `print_npa_cn20k_aura_ctx()`, and `print_npa_cn20k_pool_ctx()`. It includes `struct.h` and `../mbox.h` for CN20K context response types.

Control flow and integration: AF debugfs setup includes this header to install CN20K NPC files. Generic NIX/NPA debugfs context dumping code includes it to call the CN20K-specific formatters when the hardware generation requires CN20K layouts.

State and persistence: Header only; no runtime state. It defines access to debugfs file registration and live context rendering functions.

Dependencies: Depends on debugfs, fs, module, PCI headers, CN20K `struct.h`, and mailbox definitions. The include guard is named `DEBUFS_H`, which appears to be a typo but still prevents repeated inclusion.

Risks: Prototype changes must stay synchronized with `debugfs.c` and generic AF debugfs callers. Because printers take CN20K-specific structures, accidentally calling them with older-generation response layouts would produce invalid output.

Test signals: Build coverage with CN20K debugfs enabled and runtime reads of CN20K debugfs context dumps validate this header.

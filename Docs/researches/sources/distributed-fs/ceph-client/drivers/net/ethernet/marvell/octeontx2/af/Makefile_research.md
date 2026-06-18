# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/Makefile

Purpose: Defines the object composition for the OcteonTX2 RVU Admin Function and mailbox modules.

Important APIs/types/functions: `ccflags-y += -I$(src)` exposes local AF headers. `obj-$(CONFIG_OCTEONTX2_MBOX) += rvu_mbox.o` and `obj-$(CONFIG_OCTEONTX2_AF) += rvu_af.o` create separate composite objects. `rvu_mbox-y` includes `mbox.o` and `rvu_trace.o`. `rvu_af-y` includes core CGX/RVU/NPA/NIX/NPC/debugfs/PTP/CPT/devlink/switch/SDP/MCS/representor objects plus CN20K objects: `cn20k/mbox_init.o`, `cn20k/nix.o`, `cn20k/debugfs.o`, `cn20k/npa.o`, and `cn20k/npc.o`.

Control flow and integration: Kbuild links the listed objects into module or built-in units according to Kconfig. The Makefile is where CN20K support is integrated into the AF driver, so CN20K helpers are unavailable unless `OCTEONTX2_AF` is built.

State and persistence: Build-only file; no runtime state. It persists the compile/link contract for the AF subsystem.

Dependencies: Depends on all listed C files and their headers. The local include flag allows subfiles to include AF headers without long relative paths.

Risks: Object ordering can matter for init/linkage and exported symbols. Adding CN20K handlers here without corresponding mailbox dispatch declarations elsewhere would compile but not be reachable. Missing `rvu_trace.o` from mailbox builds would break trace references.

Test signals: AF and mailbox module builds, modpost symbol checks, and link tests with CN20K code enabled are direct validation signals.

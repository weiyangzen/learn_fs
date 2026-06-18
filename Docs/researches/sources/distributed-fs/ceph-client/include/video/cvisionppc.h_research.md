<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cvisionppc.h -->
# sources/distributed-fs/ceph-client/include/video/cvisionppc.h

Purpose: defines Phase5 CyberVisionPPC/Permedia2 framebuffer board addresses, memory configuration constants, bridge flags, and private per-board state.

Important APIs and types: `cvppc_par` stores PCI config/bridge pointers and user flags. Macros define CyberStorm PPC bridge/config base addresses, ROM/register/framebuffer apertures, framebuffer size, old/new memory config values, memory clock, bridge endian bit, and active interrupt bit.

Control flow: the Permedia2 framebuffer driver maps board-specific PCI bridge/config/register/framebuffer apertures, configures endian/interrupt behavior, and uses memory constants during initialization.

State and persistence: runtime state is board MMIO mapping, user flags, bridge configuration, and framebuffer memory. The header contains platform constants only.

Dependencies and integration points: includes `pm2fb.h` and integrates with Amiga/PowerPC CyberVisionPPC hardware and the Permedia2 fbdev driver.

Risks and test signals: risks include hard-coded physical addresses, endian bridge handling, interrupt routing, and board revision memory config differences. Test probe/map on supported hardware, endian-correct rendering, interrupts, and old/new memory config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cvisionppc.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Kconfig

Purpose: Kconfig menu for 32-bit embedded 6xx/7xx/7xxx board support, including Buffalo Linkstation, Iomega StorCenter, IBM Holly, MVME5100, Nintendo GameCube/Wii, bridge helpers, and USB Gecko debug console.

Important APIs and control flow: `EMBEDDED6xx` depends on `PPC_BOOK3S_32` and excludes SMP. Board options select required interrupt controllers, PCI forcing/indirect config, 16550 debug, FSL SoC support, or GameCube common support. `GAMECUBE_COMMON`, `TSI108_BRIDGE`, and `MPC10X_BRIDGE` are hidden dependency symbols; `USBGECKO_UDBG` is user-visible and depends on Nintendo common support.

State, dependencies, and risks: state is compile-time configuration only. Dependencies govern which platform files and helper subsystems are built. Risks are stale `BROKEN_ON_SMP` coverage, hidden bridge symbols being implied rather than required for some PCI builds, and old board help text that may not match tested hardware. Test signals are allmodconfig/defconfig coverage, dependency resolution for each board, and successful link of selected machine descriptors.

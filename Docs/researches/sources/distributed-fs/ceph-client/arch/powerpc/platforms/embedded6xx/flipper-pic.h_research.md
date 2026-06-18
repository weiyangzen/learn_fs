# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.h

Purpose: local declarations for Flipper interrupt, quiesce, reset, and reset-button helpers used by GameCube and Wii board code.

Important APIs and control flow: declares `flipper_pic_get_irq`, `flipper_pic_probe`, `flipper_quiesce`, `flipper_platform_reset`, and `flipper_is_reset_button_pressed`. The header has no logic; inclusion binds board files to `flipper-pic.c`.

State, dependencies, and risks: state is external to the header and held by `flipper-pic.c`. Dependencies are `__init` annotations and local include ordering. Risks are build/link failures if `GAMECUBE_COMMON` is not selected with board files. Test signals are compile coverage and correct linkage for GameCube/Wii machine descriptors.

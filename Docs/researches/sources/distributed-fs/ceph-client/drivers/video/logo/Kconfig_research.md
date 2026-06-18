# sources/distributed-fs/ceph-client/drivers/video/logo/Kconfig

Purpose: Kconfig menu for boot logo generation and selection. It controls whether framebuffer/console boot logos are built, which color-depth variants are available, and which source PNM files are converted into generated C logo data.

Important APIs, types, and functions: config symbols include `LOGO`, `FB_LOGO_EXTRA`, `LOGO_LINUX_MONO`, `LOGO_LINUX_MONO_FILE`, `LOGO_LINUX_VGA16`, `LOGO_LINUX_VGA16_FILE`, `LOGO_LINUX_CLUT224`, and `LOGO_LINUX_CLUT224_FILE`.

Control flow: selecting `LOGO` opens nested logo options. Per-logo file symbols default to architecture-specific logo assets for some architectures and to generic Linux logo assets otherwise. The 224-color logo defaults to enabled.

State and persistence: Kconfig state persists in the kernel build configuration and drives generated object inclusion; no runtime state is created here.

Dependencies and integration points: `LOGO` depends on `FB_CORE` or `SGI_NEWPORT_CONSOLE`. File symbols are consumed by `drivers/video/logo/Makefile`, which invokes `pnmtologo`. Logo objects are consumed by `logo.c` and framebuffer console/display code.

Risks: invalid custom PNM paths or wrong palette/color count fail at build time. `LOGO_LINUX_CLUT224` defaulting to yes increases generated asset inclusion whenever `LOGO` is enabled.

Test signals: menuconfig visibility under fbdev and SGI Newport configs; build with default and custom logo file paths; verify mono, VGA16, and CLUT224 conversion commands run and generated objects link.

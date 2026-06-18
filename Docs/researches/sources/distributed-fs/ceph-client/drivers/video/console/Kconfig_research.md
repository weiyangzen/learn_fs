# sources/distributed-fs/ceph-client/drivers/video/console/Kconfig

Purpose: Kconfig menu for text console display drivers: VGA, MDA, SGI Newport, dummy console, framebuffer console options, and HP STI console.

Important APIs/types/functions: symbols include `VGA_CONSOLE`, `MDA_CONSOLE`, `SGI_NEWPORT_CONSOLE`, `DUMMY_CONSOLE`, `DUMMY_CONSOLE_COLUMNS`, `DUMMY_CONSOLE_ROWS`, `FRAMEBUFFER_CONSOLE`, `FRAMEBUFFER_CONSOLE_LEGACY_ACCELERATION`, `FRAMEBUFFER_CONSOLE_DETECT_PRIMARY`, `FRAMEBUFFER_CONSOLE_ROTATION`, `FRAMEBUFFER_CONSOLE_DEFERRED_TAKEOVER`, and `STI_CONSOLE`.

Control flow: this file does not execute runtime code; it determines which console source objects and dependencies are enabled. VGA is architecture-gated and selects aperture helpers when needed. MDA depends on VGA console and ISA. Newport depends on SGI IP22 and MMIO. Dummy console defaults on when VT, VGA, or fbcon exists. Fbcon depends on `FB_CORE` and not UML and selects VT hardware binding, CRC32, and font support. STI is PARISC-only and selects STI core/font/CRC32.

State and persistence: configuration choices persist in kernel build configuration and influence compiled code and defaults such as dummy console dimensions.

Dependencies and integration: kernel Kconfig, architecture symbols, DRM/fb/vfio aperture coordination, VT/fbcon/STI/font subsystems.

Risks: dependency changes here can alter boot console takeover ordering and early display behavior across architectures. Test signals are build matrix checks for representative x86, PARISC, SGI IP22, and no-fb configurations, plus validation that selected objects match intended symbols.

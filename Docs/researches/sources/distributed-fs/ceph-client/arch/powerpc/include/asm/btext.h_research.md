# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/btext.h

Purpose: declares early boot text console helpers used to draw diagnostics on PowerPC framebuffers before normal console drivers are available.

Important APIs/types/functions: declares display discovery/setup/update functions, `btext_prepare_BAT()` on PPC32, `btext_map()`, `btext_unmap()`, character/string/hex/text drawing functions, and screen/line flush/clear helpers.

Control flow: early boot code finds or sets up a framebuffer, maps it, draws text/hex diagnostics, flushes lines or screen, and later unmaps it.

State and persistence: display state is maintained in the implementation file. Framebuffer contents persist on screen until overwritten or the display mode changes.

Dependencies and integration points: integrates BootX/Open Firmware display discovery, early panic/debug output, and PPC32 BAT mapping setup.

Risks: early mapping runs before normal MM is ready; invalid physical framebuffer parameters can crash or corrupt memory. PPC64 has no BAT preparation path.

Test signals: early boot with `btext` enabled, panic-before-console scenarios, framebuffer mode changes, and PPC32 BAT mapping checks.

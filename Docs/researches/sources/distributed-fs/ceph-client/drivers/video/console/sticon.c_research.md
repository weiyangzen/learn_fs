# sources/distributed-fs/ceph-client/drivers/video/console/sticon.c

Purpose: HP PA-RISC STI firmware console driver. It renders text through STI firmware operations rather than direct framebuffer manipulation.

Important APIs/types/functions: `sti_con` implements `struct consw`. Global `sticon_sti` points to the selected `struct sti_struct`. Runtime operations call `sti_putc()`, `sti_bmove()`, `sti_clear()`, `sti_set()`, and STI font conversion helpers. Font state is stored as `struct sti_cooked_font *font_data[MAX_NR_CONSOLES]`.

Control flow: module init obtains ROM 0 with `sti_get_rom()`, initializes all consoles to the firmware default font, logs device identity, and takes over consoles under console lock. Putcs/cursor skip rendering when blanked, graphics mode is active, or the VC is not text. Scroll delegates block moves/clears to STI. Font setting validates dimensions, builds a low-memory STI ROM font, converts it, deduplicates by CRC, clears old geometry, swaps references, resizes the VC, and repaints when geometry is unchanged.

State and persistence: global graphics-mode flag, font references/refcounts, and selected STI device persist for the module lifetime. Hardware/firmware state persists outside the driver.

Dependencies and integration: PARISC STI core, VT console, font and CRC32 helpers, PAGE0 console class to choose takeover behavior.

Risks: custom font memory/refcounting is delicate, especially deduplication and default reset. Rendering is skipped during graphics/blank states, so stale screen contents depend on redraws. Tests should cover font validation/dedup/free, blank mode switching, cursor restore, scroll directions, init takeover behavior, and fallback when no STI ROM exists.

# sources/distributed-fs/ceph-client/arch/m68k/68000/bootlogo-vz.h

## Purpose

`bootlogo-vz.h` embeds a raw monochrome boot splash framebuffer for 68VZ328 based m68k/68000 systems that initialize the LCD very early. It is not a normal declaration header: including it emits storage for `bootlogo_bits` and dimension macros. The selection happens in `arch/m68k/68000/m68328.c` when `CONFIG_INIT_LCD && CONFIG_M68VZ328` are enabled, and early startup assembly in `arch/m68k/68000/head.S` programs the LCD start-address register to the `bootlogo_bits` symbol under `CONFIG_INIT_LCD`.

## Important APIs, Types, and Data

- `#define splash_width 640` and `#define splash_height 480` describe the encoded image geometry for the VZ path.
- `unsigned char __aligned(16) bootlogo_bits[]` is the exported object. The `__aligned(16)` annotation comes from `<linux/compiler.h>` and gives the boot display buffer a predictable boundary for early hardware access.
- The bitmap contains 38400 byte literals, matching `640 * 480 / 8`, so the payload is a 1-bit-per-pixel frame buffer sized exactly for the declared geometry.
- The symbol name is intentionally the same as the smaller logo in `bootlogo.h`; build-time preprocessor selection ensures only one definition is included into `m68328.o`.

## Control Flow and Integration

There is no executable control flow in this file. Its behavior is entirely at compile and link time:

1. Kconfig selects the 68VZ328 platform and optional LCD initialization.
2. `m68328.c` includes this file instead of `bootlogo.h` for the 68VZ328 LCD case.
3. `head.S` declares `.global bootlogo_bits` when `CONFIG_PILOT || CONFIG_INIT_LCD` is active.
4. The ROM startup LCD path writes the address of `bootlogo_bits` into the LCD start-address register (`LSSA`) and programs LCD timing registers for the non-Pilot path.

The header therefore couples C compilation, early assembly, and memory-mapped LCD hardware. Because the object is emitted from a header, any additional include site would create duplicate `bootlogo_bits` definitions.

## State and Persistence Behavior

The data is static kernel image content. It has no runtime mutation in this file and no persistence beyond being compiled into the kernel image. At boot, the hardware may read it repeatedly through the LCD controller. The image occupies kernel memory and can remain present after initialization unless link-time garbage collection or later memory layout rules discard it, which typical early m68k startup paths do not imply here.

## Dependencies

- `<linux/compiler.h>` for `__aligned`.
- `CONFIG_INIT_LCD`, `CONFIG_M68VZ328`, and the m68328 include logic that makes this the selected logo for VZ LCD initialization.
- `head.S` early LCD setup, which assumes `bootlogo_bits` exists and points at a hardware-consumable bitmap.
- 68VZ328 LCD controller register geometry configured outside this file.

## Risks and Edge Cases

- The file is a definition-bearing header. Accidentally including it in more than one translation unit will produce duplicate global storage for `bootlogo_bits`.
- The macro prefix is `splash_` rather than `bootlogo_`, unlike `bootlogo.h`. Current startup code does not consume these macros directly, but code that expects `bootlogo_width` or `bootlogo_height` would not work for this file without adaptation.
- LCD register setup in `head.S` must match the payload shape and scan format. A mismatch can display shifted or corrupted output while still compiling cleanly.
- The large static array is about 37.5 KiB of image payload before C syntax overhead. That is material for small no-MMU m68k images.
- Because the bitmap is open-coded hex, visual regressions are hard to review without byte-count checks or rendering tools.

## Test Signals

- Build a 68VZ328 configuration with `CONFIG_INIT_LCD=y`; compilation should produce exactly one `bootlogo_bits` definition and no duplicate symbol error.
- Verify the byte count equals `splash_width * splash_height / 8`; the current file has 38400 byte literals for 640x480.
- Inspect `nm` or the final map for 16-byte alignment of `bootlogo_bits`.
- On hardware or an emulator with compatible LCD behavior, early boot should show the full 640x480 monochrome splash without line wrapping or tearing caused by an incorrect stride.

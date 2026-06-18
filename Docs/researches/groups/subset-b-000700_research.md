# Research: subset-b-000700

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/bootlogo-vz.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/bootlogo-vz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/bootlogo.h -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/bootlogo.h

## Purpose

`bootlogo.h` embeds the default small monochrome boot logo for 68000-core m68k boards that use the Pilot path or generic `CONFIG_INIT_LCD` path outside the 68VZ328-specific large splash. It is included by `arch/m68k/68000/m68328.c` when `CONFIG_PILOT` is enabled or when LCD initialization is enabled without selecting the VZ-specific logo. Like `bootlogo-vz.h`, this header emits storage and is part of early display bring-up rather than a reusable image API.

## Important APIs, Types, and Data

- `#define bootlogo_width 160` and `#define bootlogo_height 160` declare the 160x160 image geometry.
- `unsigned char __aligned(16) bootlogo_bits[]` defines the bitmap object used by early assembly and LCD setup.
- The array contains 3200 byte literals, matching `160 * 160 / 8`, which identifies it as a 1-bit-per-pixel packed framebuffer.
- The bitmap object is global and non-`static`, because `head.S` references `bootlogo_bits` directly when early LCD initialization is compiled in.

## Control Flow and Integration

This file contributes no functions. Its integration path is compile-time and early boot:

1. `m68328.c` includes `bootlogo.h` under `CONFIG_PILOT || CONFIG_INIT_LCD` unless the VZ-specific branch selects `bootlogo-vz.h`.
2. `head.S` declares `bootlogo_bits` global for Pilot or LCD builds.
3. For `CONFIG_PILOT`, `head.S` performs Pilot-specific LCD sequencing and then points `LSSA` at `bootlogo_bits` while setting width and height registers around the 160x160 geometry.
4. For non-Pilot LCD builds that do not use the VZ splash branch, the same symbol name is available for early display address programming.

Because this is a header with a definition, the include graph must preserve the current single-translation-unit pattern.

## State and Persistence Behavior

The bitmap is immutable kernel image data. The file does not allocate dynamically, read from storage, or persist state. Runtime state arises only when the LCD controller is configured elsewhere to scan from the array's address. The array remains part of the image and can contribute to memory pressure on no-MMU systems.

## Dependencies

- `<linux/compiler.h>` for `__aligned`.
- `m68328.c` preprocessor selection.
- `head.S` early LCD setup and the `bootlogo_bits` global symbol contract.
- LCD register programming for the selected board, especially the Pilot 160x160 path.

## Risks and Edge Cases

- Duplicate inclusion in multiple C objects would create multiple definitions of `bootlogo_bits`.
- This file and `bootlogo-vz.h` intentionally use the same array symbol. A Kconfig or include-order mistake that includes both would fail at compile or link time.
- The pixel format is implicit. Consumers must know it is packed monochrome data with a hardware-specific bit order.
- Reviewers can easily miss an accidental byte insertion or deletion in the long literal list. A byte-count test is a useful guard.
- The dimensions are declared but are not the only source of truth; `head.S` also hard-codes LCD setup values. Both must stay consistent.

## Test Signals

- Build representative `CONFIG_PILOT` and generic `CONFIG_INIT_LCD` configurations and check that `bootlogo_bits` resolves once.
- Verify the byte count equals `bootlogo_width * bootlogo_height / 8`; the current file has 3200 byte literals for 160x160.
- Confirm the final object keeps `bootlogo_bits` 16-byte aligned.
- Hardware smoke testing should show the logo during early LCD initialization before later framebuffer or console code takes over.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/bootlogo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/dragen2.c -->
# sources/distributed-fs/ceph-client/arch/m68k/68000/dragen2.c

## Purpose

`dragen2.c` contains DragonEngine II board support for the no-MMU m68k 68000/68VZ328 platform. It supplies board-specific reset handling, chip-select setup, CS8900 Ethernet control-pin setup, IRQ enablement, and optional LCD/backlight initialization. The object is built by `arch/m68k/68000/Makefile` under `CONFIG_DRAGEN2`, and `config_BSP()` in `m68328.c` calls `init_dragen2()` for that board.

## Important APIs, Types, and Functions

- `static void dragen2_reset(void)`: board reset callback installed into `mach_reset`. It disables interrupts, optionally shuts down LCD/backlight state, issues the 68k `reset` instruction, reloads the stack pointer and reset vector from address `0x04000000`, and jumps to the board firmware entry point.
- `void __init init_dragen2(char *command, int size)`: DragonEngine II board initialization hook called during BSP configuration. The arguments are currently unused, matching the board-init function signature declared in `m68328.h`.
- `mach_reset`: architecture machine-dependency hook from `<asm/machdep.h>` assigned to `dragen2_reset`.
- Hardware register macros such as `SCR`, `CSGBB`, `CSB`, `PKSEL`, `PKDIR`, `PKDATA`, `PFSEL`, `PFDIR`, `PFDATA`, `PDPOL`, `PDIQEG`, `PDIRQEN`, `LSSA`, `LVPW`, `LXMAX`, `LYMAX`, `LCKCON`, `PCPDEN`, `PCSEL`, and `PWMR` come from `<asm/MC68VZ328.h>` and `"m68328.h"`.
- Pin helper macros `PK(3)`, `PF(5)`, and `PD(1)` build bit masks for specific GPIO lines.
- `screen_bits` from `"screen.h"` is used as the LCD framebuffer when `CONFIG_INIT_LCD` is enabled.

## Control Flow

`init_dragen2()` first replaces the generic m68328 reset hook with `dragen2_reset`. If `CONFIG_DIRECT_IO_ACCESS` is enabled, it writes `SCR = 0x10` to allow user-mode access to internal registers. It then configures chip select group B with `CSGBB = 0x4000` and `CSB = 0x1a1`.

The CS8900 Ethernet initialization follows a direct GPIO sequence. PK3 is selected as GPIO output and driven high to keep the hardware sleep function inactive. PF5 is selected as GPIO output and driven low, then pulsed high with a busy-wait loop of 32000 iterations, then driven low again for the Ethernet hardware reset. INT1 is configured as an active-high interrupt source by clearing the PD1 polarity and edge bits and setting `PDIRQEN`.

When `CONFIG_INIT_LCD` is enabled, the function programs the LCD controller to scan from `screen_bits`, sets line width, display extents, pixel clock, pixel format, polarity, and clock enable registers, enables LCD pins, enables the LCD controller through PK2, enables the CCFL backlight circuit through PB5, and sets the PWM contrast register.

`dragen2_reset()` is the opposite path. It disables local interrupts, optionally disables CCFL and the LCD controller, clears `LCKCON`, executes the CPU reset instruction, reads initial SP and PC words from the firmware vector table at `0x04000000`, and transfers control there. It does not return.

## State and Persistence Behavior

All persistent effects are hardware register writes. No heap objects, files, or long-lived kernel data structures are allocated. The only kernel-level state mutation is assigning `mach_reset`. Hardware state persists across the remainder of the boot until another driver or reset path reprograms the same registers. The busy-wait reset pulse is timing-sensitive but has no recorded state. `command` and `size` are ignored, so boot arguments are neither parsed nor modified here.

## Dependencies

- `CONFIG_DRAGEN2` selects the object and also selects `M68VZ328` in Kconfig.
- `CONFIG_DIRECT_IO_ACCESS` controls the `SCR` user-access write.
- `CONFIG_INIT_LCD` controls both LCD shutdown during reset and LCD/backlight initialization during board setup.
- `screen.h` must define `screen_bits` when `CONFIG_INIT_LCD` is enabled; it is included in this translation unit.
- The board must expose the expected DragonEngine II wiring: CS8900 sleep on PK3, CS8900 reset on PF5, CS8900 IRQ on PD1/INT1, LCD enable on PK2, and CCFL backlight on PB5.

## Integration Points

- `arch/m68k/68000/Makefile` adds `dragen2.o` via `obj-$(CONFIG_DRAGEN2)`.
- `m68328.c::config_BSP()` calls `init_dragen2(command, len)` after setting default scheduler, RTC, and reset hooks.
- `m68328.h` declares `init_dragen2()`.
- `timers.c` has conditional behavior for `CONFIG_DRAGEN2`.
- The global `mach_reset` hook is consumed by common m68k reset and reboot paths.

## Risks and Edge Cases

- Register values are hard-coded and board-specific. Running this on non-DragonEngine II wiring can drive the wrong pins or corrupt device state.
- The Ethernet reset delay is a compiler-visible empty loop with no explicit barrier or timer source. Optimization behavior and CPU speed can affect pulse duration.
- `SCR = 0x10` under `CONFIG_DIRECT_IO_ACCESS` deliberately weakens register protection for user space.
- `dragen2_reset()` assumes a valid firmware vector table at `0x04000000`. If the boot map differs or flash is unavailable, reset can jump into invalid memory.
- LCD setup assumes `screen_bits` geometry and controller register values stay aligned. Inconsistent `screen.h` contents or panel wiring can produce a blank or corrupted screen.
- The function does not report errors; failures are visible only as missing hardware behavior, interrupt issues, or boot/reset hangs.

## Test Signals

- Build an m68k no-MMU `CONFIG_DRAGEN2=y` configuration, with and without `CONFIG_INIT_LCD`, to cover both conditional blocks.
- Inspect the final image or boot logs to confirm `init_dragen2()` is reached through `config_BSP()`.
- On board hardware, verify CS8900 reset sequencing, INT1 delivery, and network device probe behavior after initialization.
- With LCD enabled, verify `screen_bits` is scanned correctly, PK2 enables the controller, PB5 enables the backlight, and PWM contrast is usable.
- Exercise reboot/reset and confirm interrupts are disabled, LCD/backlight are quiesced, and control transfers to the firmware vector at `0x04000000`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/dragen2.c -->

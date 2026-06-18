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

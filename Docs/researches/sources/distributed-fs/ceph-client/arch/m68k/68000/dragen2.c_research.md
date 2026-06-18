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

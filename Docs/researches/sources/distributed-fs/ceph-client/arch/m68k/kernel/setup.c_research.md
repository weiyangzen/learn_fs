# sources/distributed-fs/ceph-client/arch/m68k/kernel/setup.c

## Purpose

`setup.c` is a configuration dispatcher wrapper. It includes either the MMU or no-MMU implementation of m68k setup and optionally exports the m68k beep hook.

## Important APIs, Types, and Functions

When `CONFIG_MMU` is enabled it includes `setup_mm.c`; otherwise it includes `setup_no.c`. Under `CONFIG_INPUT_M68K_BEEP`, it defines and exports `void (*mach_beep)(unsigned int, unsigned int);`.

## Control Flow

The file itself has no function bodies beyond the optional global hook. The included file supplies `setup_arch()`, `cpuinfo_op`, and related setup helpers.

## State and Persistence Behavior

The included setup implementation owns most boot state. The optional `mach_beep` function pointer persists as a machine hook for input/audio drivers.

## Dependencies and Integration Points

It depends on Kconfig selecting exactly one setup implementation. The beep hook integrates with m68k input/beeper support and platform code that may assign the function pointer.

## Risks and Edge Cases

Including `.c` files means this wrapper determines the translation-unit context. Duplicate definitions or missing config guards in the included implementations would surface here. The `mach_beep` hook is only present when the input beep option is enabled, so callers must be Kconfig-aligned.

## Test Signals

Build one MMU and one no-MMU m68k configuration. With `CONFIG_INPUT_M68K_BEEP`, confirm `mach_beep` is exported and can be assigned by platform code.

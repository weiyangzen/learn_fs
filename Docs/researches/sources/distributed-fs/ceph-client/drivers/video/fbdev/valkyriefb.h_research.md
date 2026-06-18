# sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.h

## Purpose
`valkyriefb.h` contains the register layout and mode initialization tables used by `valkyriefb.c`. It translates the sparse, padded Valkyrie MMIO layout into C structures and maps supported Mac `VMODE_*` entries to mode register values, pixel-clock programming bytes, pitch values, and visible resolution.

## Important APIs, Types, And Data
`VALKYRIE_REG_PADSIZE` encodes the different register spacing used by m68k Mac versus other platforms. `struct cmap_regs` describes the color-map address/data pair. `struct vpreg` models a padded one-byte register, and `struct valkyrie_regs` groups mode, depth, status, interrupt, and monitor-sense registers. `struct valkyrie_regvals` records one mode's control byte, three clock parameters, color-mode indexed pitches, and resolution. `valkyrie_reg_init[]` indexes supported modes by `VMODE_MAX` position.

## Control Flow
The header has no executable control flow, but `valkyriefb.c` uses the table as the central decision point for mode validation and programming. The selected `valkyrie_regvals` drives VRAM size calculation, `fix.line_length`, mode/depth writes, and clock programming. Unsupported modes have `NULL` entries, and unsupported 16 bpp modes use a zero pitch entry.

## State And Persistence
The table is static kernel data. It persists for the lifetime of the module/kernel and is treated as immutable mode capability data. It does not allocate resources or store runtime state.

## Dependencies And Integration Points
The header expects Mac mode constants from `macmodes.h` via the including source. It is tightly coupled to `valkyriefb.c` and the underlying Valkyrie register map. Some 1024x768 modes are only compiled for non-CONFIG_MAC builds.

## Risks
Mode accuracy depends on hard-coded historical timing and clock parameter values. Incorrect pitch or clock bytes can produce an unusable display. The table shape assumes `CMODE_8` and `CMODE_16` indexing as used by the Mac mode helpers; changes there would break lookup semantics. The lack of include guards means repeated inclusion would be unsafe, though this local driver includes it once.

## Test Signals
Tests should validate that each non-NULL mode can round-trip through `mac_vmode_to_var()` and `valkyrie_var_to_par()`, that pitch zero blocks unsupported color depths, that VRAM calculations match expected line length times height, and that CONFIG_MAC versus non-CONFIG_MAC builds expose the intended mode set.

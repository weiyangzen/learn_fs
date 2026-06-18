# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_reg.h

## Purpose
`si_reg.h` is a compact SI register-definition header focused on display hotplug GPIO and primary graphics surface control. It supplies the register addresses and bitfield packing macros used by Radeon display code to program SI scanout format, tiling, bank, tile-split, macro-tile, array-mode, and pipe-configuration fields.

## Important APIs, types, and definitions
- Hotplug GPIO registers: `SI_DC_GPIO_HPD_MASK`, `SI_DC_GPIO_HPD_A`, `SI_DC_GPIO_HPD_EN`, and `SI_DC_GPIO_HPD_Y`.
- Main display surface control register: `SI_GRPH_CONTROL`.
- Field packers for `SI_GRPH_CONTROL`: `SI_GRPH_DEPTH`, `SI_GRPH_NUM_BANKS`, `SI_GRPH_Z`, `SI_GRPH_BANK_WIDTH`, `SI_GRPH_FORMAT`, `SI_GRPH_BANK_HEIGHT`, `SI_GRPH_TILE_SPLIT`, `SI_GRPH_MACRO_TILE_ASPECT`, `SI_GRPH_ARRAY_MODE`, and `SI_GRPH_PIPE_CONFIG`.
- Enumerated field values cover 8/16/32 bpp surface formats, bank counts, bank width/height, tile split sizes from 64 bytes through 4 KiB, macro-tile aspect, linear and tiled array modes, and several SI pipe configurations.

## Control flow and integration points
The file contains only preprocessor definitions. It is included by `radeon_reg.h`, making these SI display definitions available to the broader Radeon driver. Display modeset, framebuffer, and scanout programming paths compose values with these macros before writing `SI_GRPH_CONTROL` or the hotplug GPIO registers.

## State and persistence behavior
All state represented by this file is hardware register state. Writes using these macros persist in the display engine until another modeset, framebuffer update, power transition, or reset overwrites them. The header itself owns no runtime state and performs no validation.

## Dependencies and constraints
The macros assume callers pass already-normalized field values. Each macro masks only the local field width and shifts into the SI register layout; it does not verify that the chosen depth/format/tiling/pipe combination is valid for the active framebuffer, ASIC, or memory layout. Consumers must pair these values with the correct surface address, pitch, tiling metadata, and display mode.

## Risks and test signals
Incorrect bit definitions or caller misuse can produce corrupted scanout, blank screens, hotplug failures, memory tiling mismatches, or display underruns. Test signals include SI modeset tests, framebuffer format coverage across 8/16/32 bpp where supported, tiled and linear scanout, hotplug detection, suspend/resume display restoration, and register readback comparison against expected modeset programming.

# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/PixelGen_SysBlock_defs.h

Purpose: defines generated register indices, widths, enable values, and magic constants for the pixel generator system block.

Important APIs/types/functions: register index macros cover common enable, PRBS reset values, sync generator configuration/status, and TPG mode/mask/delta/color registers. Width macros document bit widths. Enable values distinguish PRBS, TPG, sync generator, and FIFO enables.

Control flow: no executable flow. Host register access code uses these indices for MMIO.

State and persistence: none in software; constants describe hardware register layout.

Dependencies and integration: included by `pixelgen_private.h` and any pixelgen configuration code.

Risks and test signals: comments include generated/HSS placeholders and typos, so the header should be treated as hardware ABI. Tests should compare register indices against hardware documentation or emulator traces and validate generated test-pattern output.

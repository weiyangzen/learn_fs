# sources/distributed-fs/ceph-client/include/sound/hda_register.h

Source read summary: 368 lines, HD-audio controller register and bitfield map.

Purpose: centralizes Intel/HD-audio controller MMIO offsets, stream descriptor fields, CORB/RIRB constants, interrupt masks, buffer limits, and enhanced capability register layouts for standard and extended HDA links.

Important APIs, types, and functions: defines global registers such as `AZX_REG_GCAP`, `GCTL`, `INTCTL`, `CORB*`, `RIRB*`, immediate command/response, DMA position buffers, stream descriptor registers `AZX_REG_SD_*`, and stream control/status bits. It also defines hardware limits (`AZX_MAX_BDL_ENTRIES`, `AZX_MAX_BUF_SIZE`, CORB/RIRB entries), interrupt masks, SPIB/GTS/PP/ML capability IDs and offsets, multi-link bits such as `AZX_ML_LCTL_SPA/CPA`, synchronization fields, processing-pipe controls, and vendor-specific Intel offsets.

Control flow: controller code uses these constants to reset the controller, allocate/program CORB/RIRB and BDLs, start/stop stream DMA, service interrupts, parse extended capabilities, set stream sync and link power, and access multi-link HDA/SoundWire style registers.

State and persistence behavior: no software state is stored here; constants describe volatile MMIO state. Values written through these registers control DMA engine state, interrupt enablement, stream tags, FIFO/position tracking, and link power until reset or suspend.

Dependencies and integration points: uses generic bit helpers (`BIT`, `GENMASK`) and `HDA_MAX_CODECS` from HDA core users. It is consumed by `hdaudio.h` register-access macros and HDA controller implementations.

Risks and edge cases: incorrect offsets or masks can corrupt DMA, lose interrupts, or hang controller reset. Enhanced capability offsets differ by platform, and 32/64-bit address split registers require ordering discipline.

Test signals: controller reset and stream DMA tests on multiple Intel generations, interrupt mask validation, CORB/RIRB command tests, SPIB/position-buffer accuracy, multi-link capability parsing, and suspend/resume restoring registers.

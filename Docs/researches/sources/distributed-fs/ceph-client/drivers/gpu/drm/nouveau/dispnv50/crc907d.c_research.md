<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc907d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc907d.c

### Purpose
`crc907d.c` implements the CRC hardware callback table for the 907D display core class. It programs `NV907D` CRC control methods, binds legacy CTXDMA notifier contexts, reads output CRC entries, and detects notifier completion and overflow.

### Key APIs And Functions
The file defines a packed `crc907d_notifier` with 255 entries and implements `crc907d_set_src()`, `crc907d_set_ctx()`, `crc907d_get_entry()`, and `crc907d_ctx_finished()`. The exported `crc907d` table sets a flip threshold of `CRC907D_MAX_ENTRIES - 10`, `num_entries` to 255, and `notifier_len` to the notifier size.

### Control Flow And State
`set_src` builds `HEAD_SET_CRC_CONTROL` arguments from the generic source type, binds the notifier CTXDMA before enabling CRC, and clears the control before clearing CTXDMA on disable. `get_entry` reads the first output CRC word for an entry. `ctx_finished` waits for the notifier status done bit and logs specific overflow engine names when status bits are set.

### Dependencies And Integration
It depends on `cl907d`, `push507c`, `disp.h`, `core.h`, `head.h`, and the generic CRC abstraction. `crc.c` calls this table for Fermi/Kepler-class heads selected by the core function table.

### Risks And Test Signals
The source switch supports SOR, PIOR, DAC, RG, SF, and none; incorrect OR IDs or source mapping would capture the wrong tap. Tests should exercise all supported output types, notifier overflow paths, context flip timing, and CRC disable ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc907d.c -->

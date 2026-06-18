<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/init.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/init.c

### Purpose

VBIOS init-script interpreter. It executes NVIDIA BIOS opcodes for early device/display/memory initialization, including MMIO, indexed VGA IO, I2C/AUX, PLL programming, conditions, loops, macros, RAM-restrict groups, GPIO, and nested script calls.

### Important APIs, types, and functions

Public entry points are `nvbios_exec()` and `nvbios_post()`. Internal helpers include execution-state controls, `init_nvreg()`, MMIO/VGA/I2C/AUX wrappers, condition table readers, RAM strap translation, many `init_*` opcode handlers, and the `init_opcode[]` dispatch table.

### Control flow

Posting enumerates init script pointers from BIT `I` or BMP tables and executes each script, then an optional unknown script. `nvbios_exec()` increments nesting, reads the opcode at `init->offset`, dispatches to a handler, and stops when an opcode sets offset to zero. Handlers advance offsets, toggle execute state for conditional blocks, recurse for repeats/subscripts, and only touch hardware when `init_exec()` is true.

### State and persistence behavior

`struct nvbios_init` carries transient interpreter state: offset, nesting, execute mask, repeat bounds, selected output/head/OR/link, cached RAMCFG, and subdevice context. Hardware register writes, PLL changes, GPIO updates, and I2C/AUX side effects persist after execution.

### Dependencies and integration points

Depends on BIOS BIT/BMP/DCB/connector/DP/GPIO/RAMCFG parsers, devinit MMIO/PLL helpers, I2C/AUX, VGA IO, and NVKM logging. Device init and display init code provide context such as output/head/OR.

### Risks

This is high risk: malformed scripts, unknown opcodes, bad register mangling, or wrong execute-state nesting can program unsafe MMIO. Output/head/OR context is mandatory for many display opcodes. Delays and polling affect boot reliability.

### Test signals

Source read size: 2347 lines, 56328 bytes. Trace-mode script replay, boot/post tests across old BMP and modern BIT VBIOS, suspend/resume script execution, display mode-set init paths, I2C/AUX failure injection, unknown-opcode handling, and comparison with known-good register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/init.c -->

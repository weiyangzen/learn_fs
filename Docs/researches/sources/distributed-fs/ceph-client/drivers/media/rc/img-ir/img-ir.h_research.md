# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir.h

Purpose: central private header for the ImgTec IR platform driver. It defines the MMIO register map and bit masks for the PowerDown Controller IR block, composes raw and hardware decoder private state into `struct img_ir_priv`, and provides inline MMIO accessors.

Important APIs, types, and functions: register offsets include control, status, data low/high, symbol timing registers, power modulation registers, interrupt message filters, IRQ enable/status/clear, and core identification/revision registers. Bit masks define control fields, status validity/length/level bits, symbol timing field packing, free-time length fields, power modulation fields, IRQ sources, and core ID/revision fields. `struct img_ir_priv` stores the platform device, IRQ, input clocks, MMIO base, spinlock, `raw` decoder state, and `hw` decoder state. `img_ir_write()` and `img_ir_read()` wrap `iowrite32()` and `ioread32()`.

Control flow: `img-ir-core.c` uses this header to initialize the platform device and dispatch IRQs. `img-ir-raw.c` and `img-ir-hw.c` use the register constants and accessors to program or sample the hardware. The private struct is the shared state object passed through all ImgTec IR submodules.

State and persistence behavior: defines runtime state only. `reg_base` anchors all register access; `lock` serializes register and private-state manipulation across interrupt, timer, PM, and userspace protocol/filter paths.

Dependencies and integration points: includes Linux I/O and spinlock APIs plus `img-ir-raw.h` and `img-ir-hw.h`. It is the integration boundary between the platform core, raw rc-core receive path, and hardware scancode receive path.

Risks and edge cases: bit masks and shifts directly encode hardware ABI. Parenthesization of register field macros matters when callers combine shifts and masks. All accessors assume `reg_base` is valid and mapped. Shared locking must cover multi-register updates in submodules to avoid inconsistent IRQ/filter/timing state.

Test signals: platform probe should report sensible core ID/revision, IRQ clear/enable should affect the expected sources, and both raw and hardware decoder builds should compile against the same private struct.

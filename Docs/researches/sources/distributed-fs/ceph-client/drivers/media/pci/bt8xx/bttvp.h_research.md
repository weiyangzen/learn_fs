# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttvp.h

## Purpose
`bttvp.h` is the private bttv implementation header. It centralizes internal constants, structures, function prototypes, debug macros, hardware register access macros, and the full `struct bttv` device state used by the driver files.

## Important APIs, Types, And Functions
Important types include `struct bttv_tvnorm`, `struct bttv_format`, `struct bttv_ir`, `struct bttv_geometry`, `struct bttv_buffer`, `struct bttv_buffer_set`, `struct bttv_vbi_fmt`, `struct bttv_crop`, `struct bttv_pll_info`, `struct bttv_suspend_state`, and `struct bttv`. It declares internal functions for VBI, RISC, GPIO, input, I2C, resource allocation, and IRQ register initialization. Register macros are `btwrite()`, `btread()`, `btand()`, `btor()`, and `btaor()`.

## Control Flow
The header describes how companion files interlock: queue callbacks use `struct bttv_buffer`, RISC code uses `RISC_SLOT_*` constants, resource checks use `RESOURCE_*`, VBI code uses `VBI_BPL`/`VBI_DEFLINES`, and IRQ/DMA paths manipulate `struct bttv.curr`, `cvbi`, `loop_irq`, and `timeout`. `to_bttv()` converts from `struct v4l2_device` to the enclosing driver object.

## State And Persistence
`struct bttv` is the authoritative in-memory state object. It contains PCI/MMIO identity, card configuration, GPIO/I2C/subdevice state, V4L2 device nodes, control handlers, remote state, locks, frequencies, norm/crop/format state, buffer queues, active DMA state, timeout/watchdog state, suspend snapshot, and statistics. No persistent state is defined.

## Dependencies And Integration Points
The header includes kernel PCI/I2C/input/mutex/scatterlist/device headers, V4L2 controls/fh/common, videobuf2 DMA-SG, tveeprom, rc-core, `ir-kbd-i2c`, TEA575x, and local `bt848.h`, `bttv.h`, and `btcx-risc.h`. It is intentionally private to bttv implementation files and should not be used by unrelated modules.

## Risks
Because this header defines the core state shape, changes have wide blast radius across video, VBI, I2C, IRQ, GPIO, and input paths. Register access macros assume a local variable named `btv`; using them in the wrong scope is error-prone. Locking expectations are documented in comments but not enforced by types, especially around RISC state and crop/resource fields.

## Test Signals
Compile and sparse-style checking catch many header breakages. Runtime signals include successful probe/remove, stable capture, no lockdep complaints around documented locks, working suspend/resume state restoration, and correct interaction between video and VBI queues.

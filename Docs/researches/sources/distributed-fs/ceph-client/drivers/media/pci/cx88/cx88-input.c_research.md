# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-input.c

## Purpose
`cx88-input.c` implements remote-control input support for cx2388x boards. It handles GPIO-polled scancode remotes, raw IR sampling through the chip's IR sample FIFO, and I2C-attached IR receiver discovery.

## Important APIs, Types, And Functions
`struct cx88_IR` stores the `rc_dev`, core pointer, user count, GPIO masks, polling interval, hrtimer, and last GPIO sample. Public functions are `cx88_ir_init()`, `cx88_ir_fini()`, `cx88_ir_start()`, `cx88_ir_stop()`, `cx88_ir_irq()`, and `cx88_i2c_init_ir()`. Key helpers include `cx88_ir_handle_key()`, `cx88_ir_work()`, `cx88_ir_open()`, `cx88_ir_close()`, and `get_key_pvr2000()`.

## Control Flow
`cx88_ir_init()` allocates an rc-core device, switches on `core->boardnr`, and configures board-specific key maps, GPIO registers, key masks, polling periods, or raw-sampling addresses. Polling remotes start an hrtimer that repeatedly calls `cx88_ir_handle_key()`. Raw-sampling remotes enable `PCI_INT_IR_SMPINT`, program `MO_DDS_IO` from `ir_samplerate`, enable `MO_DDSCFG_IO`, and feed pulse/space durations from `MO_SAMPLE_IO` in `cx88_ir_irq()`. GPIO decoding normalizes special board layouts, extracts masked bits, and emits rc-core key events. `cx88_i2c_init_ir()` probes known I2C receiver addresses with read-style SMBus transactions.

## State, Persistence, And Dependencies
State is in `core->ir`, the rc-core device, hrtimer state, `core->pci_irqmask`, and `core->init_data` for I2C IR. The driver does not persist learned codes. It depends on rc-core, `ir_extract_bits()`, I2C SMBus, cx88 GPIO/sample registers, and board ID constants from `cx88.h`.

## Integration Points
The video driver starts/stops IR during suspend/resume and final removal. Core interrupt handling routes IR sample interrupts to `cx88_ir_irq()`. I2C IR setup depends on the primary I2C adapter from `cx88-i2c.c`. Userspace sees standard rc-core input devices with board-specific key maps.

## Risks
Most behavior is board-table-driven; incorrect masks or polling intervals cause missing or repeated keys. `cx88_ir_fini()` unregisters then explicitly frees `ir->dev`, which is a lifetime-sensitive rc-core pattern. Polling timers must be cancelled on last close and suspend. Sample decoding assumes 32-bit sample layout and fixed samplerate math. I2C receiver probing avoids quick writes deliberately.

## Test Signals
Test representative raw-sampling Hauppauge/TBS/TeVii boards, GPIO-polled WinFast/PixelView/PowerColor boards, and Leadtek PVR2000 I2C IR. Check open/close user counts, suspend/resume restart, `ir-keytable` events, NECX scancodes, no hrtimer activity after close, and no interrupt storm when raw sampling is disabled.

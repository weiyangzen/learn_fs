# sources/distributed-fs/ceph-client/drivers/comedi/drivers/comedi_8255.c

Purpose: Implements reusable Comedi support for 8255 programmable peripheral interface digital I/O chips. It lets parent drivers expose a 24-channel DIO subdevice backed by I/O ports, MMIO registers, or a custom callback.

Important APIs/types/functions: The private state is `struct subdev_8255_private`, storing callback context and I/O callback. Exported initializers are `subdev_8255_io_init()`, `subdev_8255_mm_init()`, `subdev_8255_cb_init()`, and `subdev_8255_regbase()`. Core handlers are `subdev_8255_insn()`, `subdev_8255_insn_config()`, and `subdev_8255_do_config()`. Built-in callbacks are `subdev_8255_io()` and `subdev_8255_mmio()`.

Control flow: Initialization allocates subdevice private storage, records the callback/context, configures the subdevice as readable/writable 24-bit DIO, installs instruction handlers, and writes the initial 8255 control word. Bit instructions update Comedi DIO state from `data[0]/data[1]`, write only the affected 8-bit ports, then read ports A/B/C and return a 24-bit value. Config instructions map the requested channel to one of four direction groups: A, B, C-low, or C-high; they call the generic Comedi DIO config helper with that mask and rewrite the 8255 mode-0 control word.

State and persistence: State lives in Comedi `s->state` and `s->io_bits`, plus callback context in `s->private`. Hardware port directions and output latches persist until rewritten or reset. Only 8255 mode 0 is supported; no durable state is stored.

Dependencies and integration points: Depends on `linux/comedi/comedidev.h` and `linux/comedi/comedi_8255.h`. It is used by multiple board drivers in this work item, including `cb_pcidda`, `cb_pcimdas`, `cb_pcimdda`, `cb_pcidas64`, and `daqboard2000`.

Risks: Direction masks must match 8255 grouping rules; individual-bit direction changes are widened to hardware banks. Callback users must implement port numbering and write/read return semantics correctly. I/O-port support is conditional on `CONFIG_HAS_IOPORT`, while MMIO/callback paths remain available. Test signals include all four direction groups, partial-bit writes preserving other ports, port readback after output writes, callback-backed 8255 devices, and parent-driver attach paths.

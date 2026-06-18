# Research: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.c

Purpose: rc-core input integration for boards whose IR receiver is represented as a V4L2 IR subdevice. It translates raw IR measurements into Linux remote-control events and manages open/close power state.

Important APIs/types/functions: `cx23885_input_init()` creates and registers `struct rc_dev`, selecting protocol mask and keymap by board. `cx23885_input_fini()` stops hardware and unregisters the RC device. `cx23885_input_rx_work_handler()` processes IR notifications. Internal helpers `cx23885_input_process_measurements()`, `cx23885_input_ir_start()`, `cx23885_input_ir_stop()`, `cx23885_input_ir_open()`, and `cx23885_input_ir_close()` configure and drain the IR subdevice.

Control flow: after the core installs IRQ handling and initializes IR subdevices, it calls input init. Supported boards allocate `cx23885_kernel_ir`, create names/physical path, set rc-core IDs, and register raw IR decoding. On rc open, board-specific receiver parameters are sent via `rx_s_parameters`. Notification work reads arrays of `struct ir_raw_event` from `sd_ir` until empty, stores them to rc-core, handles overflow, and restarts hardware after FIFO overrun. Close and fini set a shutdown flag, disable interrupts, and flush related work.

State and persistence: state is volatile in `dev->kernel_ir`, `rc_dev`, allocated name strings, `dev->ir_input_stopping`, and IR subdevice parameters. No persistent keymap storage is written by this file.

Dependencies/integration: rc-core, V4L2 subdev IR ops, workqueues initialized in core/IR files, board IDs and keymap constants. It depends on `dev->sd_ir` already being populated by card/IR setup.

Risks: only explicitly listed boards are enabled; overrun recovery races are mitigated but still depend on subdevice honoring `shutdown`; `cx23885_input_fini()` calls stop even when no IR exists; keymap assignments for some boards are documented guesses.

Test signals: `/sys/class/rc/rc*` device appears with expected keymap; opening the rc device starts receiver; `ir-keytable -t` sees raw events; FIFO overrun recovers without repeated interrupts; unload during open/close does not leave scheduled work or freed `kernel_ir` access.

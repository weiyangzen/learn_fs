# sources/distributed-fs/ceph-client/lib/logic_pio.c

Purpose: manages logical PIO token ranges and translates between firmware/hardware addresses and Linux logical I/O port addresses, including indirect PIO callbacks.

Important APIs/types/functions: `logic_pio_register_range()`, `logic_pio_unregister_range()`, `find_io_range_by_fwnode()`, `logic_pio_to_hwaddr()`, `logic_pio_trans_hwaddr()`, `logic_pio_trans_cpuaddr()`, and generated `logic_in*/logic_out*/logic_ins*/logic_outs*` when indirect PIO is enabled.

Control flow: registration validates range data, rejects duplicate firmware nodes, checks CPU MMIO overlap, assigns an `io_start` either below `MMIO_UPPER_LIMIT` or in indirect space, and links the range with RCU. Translation functions find ranges by firmware node, logical token, or CPU address. I/O helpers route low tokens to direct `_in/_out` or PCI_IOBASE access and high tokens to range-provided indirect ops.

State/persistence: global RCU-protected `io_range_list` guarded by `io_range_mutex` for writes. Registered range objects are owned by callers.

Dependencies/integration: used by host bridge and PCI I/O setup code. Depends on firmware nodes, RCU list traversal, resource sizes, indirect PIO ops, and `PCI_IOBASE`.

Risks: duplicate fwnode returns `-EEXIST` and is documented as success-like for callers. Registration mutates oversized CPU MMIO ranges down to 64K. Range lifetime must outlive RCU readers after unregister.

Test signals: expected tests cover duplicate registration, overlap rejection, token translation, indirect callback dispatch, and unregister grace-period safety.

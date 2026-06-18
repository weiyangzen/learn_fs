# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.c

## Purpose
`agilent_82357a.c` implements the Agilent/Keysight 82357A and 82357B USB-to-GPIB adapters. It bridges the linux-gpib interface to vendor USB bulk, interrupt, and control messages and manages hotplug independently from GPIB board attach.

## Important APIs, Types, and Functions
Private state is `struct agilent_82357a_priv`, defined in the header. USB transfer helpers are `agilent_82357a_send_bulk_msg()`, `agilent_82357a_receive_bulk_msg()`, `agilent_82357a_receive_control_msg()`, `agilent_82357a_write_registers()`, `agilent_82357a_read_registers()`, and `agilent_82357a_abort()`. GPIB data paths are `agilent_82357a_read()`, `agilent_82357a_generic_write()`, `agilent_82357a_write()`, and `agilent_82357a_command()`. Setup and lifecycle functions include `agilent_82357a_setup_urbs()`, `agilent_82357a_init()`, `agilent_82357a_attach()`, `agilent_82357a_detach()`, USB probe/disconnect/suspend/resume, and module init/exit.

## Control Flow
Module init registers a USB driver and one GPIB interface. USB probe only records an available interface in a global table protected by `agilent_82357a_hotplug_lock`; GPIB attach later selects an unclaimed interface by optional device path or serial number, sets endpoints according to product ID, starts the interrupt URB, initializes firmware registers, and marks the board attached. Disconnect clears the global table entry, kills active URBs, and nulls `bus_interface` under allocation locks so later operations return `-ENODEV`.

Bulk helper functions allocate one URB at a time, serialize allocation and protocol transfers with mutexes, use a timer to complete timed-out URBs, and kill/free URBs on cleanup. Writes send a protocol header plus payload, wait for a write-complete interrupt or board timeout, then read a vendor control status block for byte count. Reads send a read command, receive payload plus trailing flags, abort and drain on timeout, set END on EOI/EOS flags, and force ATN to refresh status. Register reads and writes are short bulk protocols with response validation. Suspend aborts transfers, idles firmware, and kills URBs; resume restarts the interrupt URB, reinitializes firmware, restores system-controller and REN state, and toggles IFC when master.

## State and Persistence
State includes a global array of up to 128 USB interfaces, per-board mutexes, bulk and interrupt URBs, timer/completion context, endpoint numbers, EOS settings, hardware control bits, interrupt flags, CIC and REN state. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on USB core, GPIB common core, TMS9914 register definitions, wait queues, timers, completions, and userspace board configuration matching by path or serial.

## Risks and Test Signals
Some error paths in register helpers return without freeing `in_data` after response validation failures. Detach locks allocation mutexes and then frees private state without unlocking them, which is safe only because the object is destroyed but is unusual and should be reviewed with lockdep expectations. Global interface matching allows hotplug and attach to be decoupled but limits devices to 128 and requires careful disconnect races. Tests should cover A and B endpoint selection, attach before firmware-loaded IDs are present, serial/path matching, read timeout abort and drain, write no-listener detection, interrupt URB resubmit, suspend/resume restoration, disconnect during blocked transfer, and module unload with attached boards.

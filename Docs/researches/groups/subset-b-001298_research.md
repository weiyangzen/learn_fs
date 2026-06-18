# subset-b-001298 Research

This grouped research report covers the GPIB driver subset requested for `subset-b-001298`. Each section is delimited for reconciliation into one source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/hp_82341.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/hp_82341.c

## Purpose

`hp_82341.c` is the board driver for HP/Agilent 82341 ISA/ISA-PnP GPIB boards. It registers two linux-gpib interfaces: `hp_82341_unaccel`, which delegates reads and writes directly to the shared TMS9914 core, and `hp_82341`, which uses the board FIFO and transfer counter for accelerated data movement while still relying on the TMS9914 core for command, addressing, status, control-line, EOS, serial-poll, parallel-poll, and T1-delay semantics.

The driver also owns board-specific Xilinx firmware upload, ISA PnP discovery for 82341D boards, fixed I/O-region allocation for 82341C boards, IRQ setup, event-status aggregation, and teardown.

## Important APIs, Types, and Functions

- `hp_82341_accel_read()` and `hp_82341_accel_write()` implement FIFO-backed read/write paths around a TMS9914 controller. They use region 3 buffer ports, region 1 transfer counters, event interrupts, and `board->wait`.
- `hp_82341_read()`, `hp_82341_write()`, `hp_82341_command()`, and the other wrapper functions adapt the `gpib_interface` callbacks to `tms9914_*` helpers.
- `hp_82341_attach()` allocates `struct hp_82341_priv`, selects 82341C versus 82341D configuration, claims four I/O regions, loads firmware, requests the IRQ, programs interrupt/event enables, resets the TMS9914, and brings it online.
- `hp_82341_detach()` disables interrupts, resets the TMS9914, frees the IRQ, releases I/O regions, detaches ISA PnP state, and frees private data.
- `hp_82341_interrupt()` reads board event bits, write-clears board event sources, records FIFO/terminal-count events in `event_status_bits`, and delegates TMS9914 status handling to `tms9914_interrupt_have_status()`.
- `hp_82341_load_firmware()`, `hp_82341_load_firmware_array()`, `clear_xilinx()`, `xilinx_ready()`, `xilinx_done()`, and `set_xilinx_not_prog()` implement the 82341C/82341D Xilinx configuration protocol.

## Control Flow

Attach starts by clearing `board->status`, allocating private data, wiring the embedded `tms9914_priv` byte accessors, and deciding hardware version. With `config->ibbase == 0`, the code searches for ISA PnP ID `HWP1411`, activates it, and treats the board as 82341D with compact region spacing. Otherwise it uses configured ISA base/IRQ and treats the board as 82341C with 0x400 spacing. It requests four 8-byte I/O regions, points the TMS9914 base at region 2, configures ISA PnP GPIO direction for 82341D, clears and uploads firmware, validates IRQ compatibility, installs `hp_82341_interrupt()`, programs IRQ select bits, enables board interrupt routing, resets/initializes the TMS9914, enables event interrupts, clears pending events, then calls `tms9914_online()`.

Accelerated read disables the board FIFO, performs an initial one-byte TMS9914 read for corner cases, switches to holdoff-on-EOI mode, flushes the FIFO, then loops over blocks up to `hp_82341_fifo_size`. For each block it sets the transfer counter, enables the GPIB-to-host buffer, restarts the stream if needed, waits for terminal count, buffer end, device clear, or timeout, disables the buffer, drains words from the FIFO port into the caller buffer, and handles END/timeout/device-clear state. If no END was seen, it finishes with a normal TMS9914 read to preserve final-byte holdoff behavior.

Accelerated write optionally reserves the final byte for EOI, clears board events, flushes the FIFO, writes each block as 16-bit words to the board FIFO, enables the output buffer, restarts a halted stream once NRFD allows it, waits for terminal count or error events, and accounts bytes by reading the transfer counter residue. If EOI is requested, the final byte is sent through the non-accelerated `hp_82341_write()` path with `send_eoi=1`.

## State and Persistence Behavior

Persistent runtime state lives in `struct hp_82341_priv`: embedded `tms9914_priv`, selected IRQ, shadowed board control bits, accumulated event bits, optional `pnp_dev`, four I/O bases, I/O spacing, and hardware-version tag. Firmware is not persisted by the driver; it must already be loaded or be supplied through `config->init_data` at attach time. Transfer state is transient and stored in hardware counters, `event_status_bits`, TMS9914 state bits, and `board->status`.

`read_and_clear_event_status()` protects `event_status_bits` with `board->spinlock`, allowing accelerated transfer wait predicates to consume interrupt events without directly touching the hardware register. TMS9914 status and data-ready state remain in the embedded TMS9914 core.

## Dependencies and Integration Points

The file depends on `hp_82341.h`, the TMS9914 core, linux-gpib core registration (`gpib_register_driver()`/`gpib_unregister_driver()`), ISA PnP helpers, I/O port helpers, kernel IRQ APIs, sleep/wait APIs, and `struct gpib_board_config` firmware/configuration data. It integrates with gpib-common through `struct gpib_interface` callback tables and with userspace configuration through `ibbase`, `ibirq`, and firmware `init_data`.

## Risks and Test Signals

Several attach failure paths return directly after private allocation or resource acquisition; correctness depends on the core invoking detach after failed attach, otherwise private data, PnP attachment, I/O regions, or IRQs can leak. Accelerated reads explicitly bypass FIFO mode when EOS receive detection is active because hardware cannot compare EOS in FIFO mode. FIFO restart depends on line-status polling and sleep loops, so timeout, device-clear, and signal-interrupt paths are key test cases. The driver has no direct self-tests; practical signals are kernel build coverage, module load/unload, firmware-length validation for 82341C/82341D, IRQ delivery, successful `gpib_config` attach/detach, command/read/write transfers with and without EOI, EOS read fallback, timeout propagation, and device-clear handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/hp_82341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/hp_82341.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/hp_82341.h

## Purpose

`hp_82341.h` declares board-private state, hardware version tags, firmware sizes, FIFO size, I/O-region geometry, and register/bit definitions for the HP 82341 board family. It is consumed by `hp_82341.c` to keep magic offsets and control-bit meanings centralized.

## Important APIs, Types, and Constants

- `enum hp_82341_hardware_version` distinguishes unknown, 82341C, and 82341D variants.
- `struct hp_82341_priv` is the `gpib_board.private_data` shape. It embeds `struct tms9914_priv`, IRQ number, board control shadows, latched event bits, optional `struct pnp_dev`, four I/O bases, region spacing, and hardware-version state.
- `hp_82341_region_iosize`, `hp_82341_num_io_regions`, `hp_82341_fifo_size`, `hp_82341c_firmware_length`, and `hp_82341d_firmware_length` define board geometry and firmware validation.
- Register enums define offsets for region 0 control/status, region 1 ID and transfer count, and region 3 FIFO/buffer registers.
- Bit enums define IRQ selection, Xilinx ready/done, mode control, monitor flags, interrupt/event enable/status bits, stream restart status, buffer direction/enable, and 82341D ISA-PnP GPIO bits.
- `IRQ_SELECT_BITS()` maps supported ISA IRQ numbers to the board encoding.

## Control Flow and Integration

The header has no executable control flow beyond `IRQ_SELECT_BITS()`. Its constants drive attach-time firmware handling, interrupt routing, transfer-counter programming, FIFO data movement, and board event decoding in `hp_82341.c`.

## State and Persistence Behavior

The header defines the in-memory shadow fields that persist for the lifetime of an attached board. Hardware shadow fields must stay synchronized with writes to `CONFIG_CONTROL_STATUS_REG` and `MODE_CONTROL_STATUS_REG`. `event_status_bits` is interrupt-produced and transfer-consumed transient state protected by the board spinlock.

## Dependencies

It includes `tms9914.h` and `gpibP.h`, so it is kernel-only and tied to the linux-gpib board model plus the TMS9914 controller core.

## Risks and Test Signals

The IRQ encoding covers only the 82341C supported IRQ set; mismatches are caught by `hp_82341.c`. Firmware lengths are fixed constants and are a useful regression signal if firmware blobs change. Because the header contains register contracts, test signals are indirect: successful firmware upload, correct IRQ selection, transfer counter accounting, and FIFO read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/hp_82341/hp_82341.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/amcc5920.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/amcc5920.h

## Purpose

`amcc5920.h` provides register offsets and bit-building helpers for AMCC 5920 PCI bridge chips used by some GPIB boards, notably the INES PCI path.

## Important APIs and Constants

- `AMCC_INTCS_REG` and `AMCC_PASS_THRU_REG` identify bridge interrupt/status and pass-through configuration registers.
- `AMCC_ADDON_INTR_ENABLE_BIT`, `AMCC_ADDON_INTR_ACTIVE_BIT`, and `AMCC_INTR_ACTIVE_BIT` model interrupt enable/active state.
- `amcc_wait_state_bits(region, num_wait_states)`, `amcc_prefetch_bits(region, prefetch)`, `amcc_PTADR_mode_bit(region)`, and `amcc_disable_write_fifo_bit(region)` build per-region pass-through configuration fields.
- `enum amcc_prefetch_bits` encodes disabled/small/medium/large prefetch modes.

## Control Flow and Integration

The header has only inline bit constructors. `ines_gpib.c` uses it during AMCC-backed PCI attach to disable prefetching, select PTADR mode, disable the write FIFO, set wait states, and enable add-on interrupts.

## State and Persistence Behavior

No state is stored in this header. State is represented in AMCC PCI bridge registers programmed by board drivers.

## Dependencies

The helpers use fixed-width `uint32_t` but the header itself has no include guard and does not include a type header, so including files must already provide that type.

## Risks and Test Signals

The bit helpers pre-decrement the one-based `region` argument. Passing zero underflows the shift expression and passing an out-of-range region can build invalid register values. Test signals are PCI attach on AMCC boards, valid interrupt delivery, and absence of bus timing/FIFO errors after pass-through register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/amcc5920.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/amccs5933.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/amccs5933.h

## Purpose

`amccs5933.h` defines register offsets and mailbox/interrupt bit helpers for AMCC S5933 PCI bridge chips. This subset does not show a direct user, but it is part of the GPIB PCI bridge vocabulary.

## Important APIs and Constants

- `MBEF_REG`, `INTCSR_REG`, and `BMCSR_REG` identify mailbox empty/full, interrupt control/status, and bus-master control/status registers.
- `INCOMING_MAILBOX_REG(mailbox)` maps mailbox index to incoming mailbox register offset.
- `OUTBOX_EMPTY_INTR_BIT`, `INBOX_FULL_INTR_BIT`, `INBOX_INTR_CS_BIT`, and `INTR_ASSERTED_BIT` encode INTCSR interrupt controls/status.
- `INBOX_BYTE_BITS()`, `INBOX_SELECT_BITS()`, `OUTBOX_BYTE_BITS()`, and `OUTBOX_SELECT_BITS()` select mailbox bytes and mailbox numbers.
- `MBOX_FLAGS_RESET_BIT` resets mailbox flags in BMCSR.

## Control Flow and Integration

There is no runtime control flow. Drivers include this header when programming S5933 mailbox or interrupt registers.

## State and Persistence Behavior

No kernel state is declared. State lives in hardware mailbox, interrupt, and bus-master registers.

## Dependencies

The file uses `extern inline int` helper definitions without an include guard. It relies on C compiler/kernel build semantics for inline definitions and on including code to avoid duplicate-symbol surprises.

## Risks and Test Signals

Because helpers mask mailbox/byte numbers to two bits, invalid callers can silently wrap to a different mailbox. Test signals are bridge interrupt assertion/clear behavior, mailbox status transitions, and no duplicate inline-linkage build warnings across supported compiler modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/amccs5933.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpibP.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/gpibP.h

## Purpose

`gpibP.h` is a private kernel header for linux-gpib internals. It pulls together core types, ioctl/user definitions, I/O helpers, PCI lookup helpers, event queues, pseudo IRQ support, and exported core driver registration entry points.

## Important APIs and Types

- `gpib_register_driver()` and `gpib_unregister_driver()` are the central integration points for board drivers exposing a `struct gpib_interface`.
- `gpib_pci_get_device()` and `gpib_pci_get_subsys()` provide config-filtered PCI discovery helpers.
- `num_gpib_events()`, `push_gpib_event()`, and `pop_gpib_event()` manage per-board event queues.
- `gpib_request_pseudo_irq()` and `gpib_free_pseudo_irq()` support timer-backed polling when hardware IRQs are unavailable.
- `gpib_match_device_path()` matches sysfs device paths used by USB attach flows.
- `board_array` and `registered_drivers` expose global core state to drivers.

## Control Flow and Integration

Board modules include this header to register their callback table and use common discovery/event helpers. The HP, INES, NEC7210, and LPVO files in this subset all rely on types or functions reached through this header.

## State and Persistence Behavior

The header declares global board and registered-driver lists but does not define them. Driver lifetime state is coordinated through these globals by the gpib core.

## Dependencies

It includes `gpib_types.h`, `gpib_proto.h`, `gpib_cmd.h`, public linux-gpib headers, `linux/fs.h`, `linux/interrupt.h`, and `linux/io.h`. It is not a userspace header.

## Risks and Test Signals

Because it exposes private globals, misuse can bypass core locking or registration invariants. Test signals include module registration/unregistration ordering, event queue correctness under interrupt load, and PCI/USB path matching for multi-board configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpibP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_cmd.h

## Purpose

`gpib_cmd.h` defines IEEE-488/GPIB command byte constants and small helpers for constructing and classifying command bytes and GPIB addresses.

## Important APIs and Constants

- `enum cmd_byte` names universal/addressed commands such as `GTL`, `SDC`, `GET`, `TCT`, `LLO`, `DCL`, `SPE`, `SPD`, `UNL`, `UNT`, listen/talk address bases `LAD`/`TAD`, and secondary/parallel-poll bases.
- `gpib_address_restrict()` clamps primary addresses to usable 0-30 range by mapping 31 back to 0.
- `MLA()`, `MTA()`, and `MSA()` construct listen, talk, and secondary address command bytes.
- `gpib_address_equal()` compares primary/secondary address pairs, treating two negative secondary addresses as equal/no-secondary.
- `is_PPE()`, `is_PPD()`, and `in_*_command_group()` classify command byte groups by high bits.

## Control Flow and Integration

The helpers are inline and pure. Driver and core code use them when composing command streams and validating command pass-through groups.

## State and Persistence Behavior

No state is stored. All behavior is deterministic by input byte/address.

## Dependencies

The header includes `linux/types.h` for fixed-size integer types. It is included by private gpib headers and drivers.

## Risks and Test Signals

The helpers intentionally mask command/address bits, so tests should include boundary addresses 0, 30, and 31, secondary address disabled cases, and command group classification for all high-bit groups. Misclassification affects bus command routing and pass-through handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_pci_ids.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_pci_ids.h

## Purpose

`gpib_pci_ids.h` supplies fallback vendor/device IDs for PCI GPIB boards when the running kernel headers do not define them.

## Important APIs and Constants

- `PCI_VENDOR_ID_AMCC` is defaulted to `0x10e8`.
- `PCI_VENDOR_ID_CBOARDS` is defaulted to `0x1307`.
- `PCI_VENDOR_ID_QUANCOM` is defaulted to `0x8008`.
- `PCI_DEVICE_ID_QUANCOM_GPIB` is defaulted to `0x3302`.

## Control Flow and Integration

The file is preprocessor-only. `ines_gpib.c` includes it to build its PCI ID table and custom PCI search list.

## State and Persistence Behavior

No runtime state exists.

## Dependencies

The file has an include guard and relies on standard PCI macro naming. It avoids redefining IDs that the kernel already supplies.

## Risks and Test Signals

Incorrect IDs prevent device binding or make discovery match the wrong hardware. Test signals are `MODULE_DEVICE_TABLE(pci, ...)` contents, `lspci` matching on supported boards, and successful attach for Quancom/AMCC-backed INES boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_pci_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_proto.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_proto.h

## Purpose

`gpib_proto.h` declares gpib-common core entry points used by character-device file operations, board lifecycle helpers, timer management, descriptor initialization, and user-visible GPIB operations.

## Important APIs and Functions

- File operations: `ibopen()`, `ibclose()`, and `ibioctl()`.
- Timer helpers: `os_start_timer()`, `os_remove_timer()`, and `usec_to_jiffies()`.
- Board/descriptor setup: `init_gpib_board()` and `init_gpib_descriptor()`.
- Bus operations: `ibcac()`, `ibcmd()`, `ibgts()`, `ibonline()`, `iboffline()`, `iblines()`, `ibrd()`, `ibrpp()`, `ibrsv2()`, `ibrsc()`, `ibsic()`, `ibsre()`, `ibpad()`, `ibsad()`, `ibeos()`, `ibwait()`, `ibwrt()`, `ibstatus()`, `general_ibstatus()`, `io_timed_out()`, and `ibppc()`.
- Serial polling: `serial_poll_all()` and `dvrsp()`.

## Control Flow and Integration

Board drivers do not implement these declarations; they call into or are called by the gpib core through `struct gpib_interface`. The core uses interface callbacks to satisfy these operations and update `board->status`.

## State and Persistence Behavior

The prototypes operate on `struct gpib_board`, `struct gpib_descriptor`, and status queues defined in `gpib_types.h`. Timer state is persisted in `board->timer` for active operations.

## Dependencies

The file includes `linux/fs.h` for inode/file types and relies on GPIB public constants from headers pulled in by users of `gpibP.h`.

## Risks and Test Signals

`usec_to_jiffies()` rounds up and adds one jiffy, which affects timeout behavior. Test signals include ioctl conformance, timeout paths, online/offline transitions, address changes, EOS mode, serial poll, parallel poll, and wait-mask behavior across drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_state_machines.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_state_machines.h

## Purpose

`gpib_state_machines.h` defines small enums describing the GPIB talker and listener function states tracked by controller-specific cores.

## Important APIs and Types

- `enum talker_function_state`: `talker_idle`, `talker_addressed`, `talker_active`, and `serial_poll_active`.
- `enum listener_function_state`: `listener_idle`, `listener_addressed`, and `listener_active`.

## Control Flow and Integration

The NEC7210 and TMS9914 private structures include these enums. Interrupt/status update paths set them based on hardware address-status bits and then mirror the result into `board->status` bits such as TACS and LACS.

## State and Persistence Behavior

These enums are per-board in-memory state. They are recalculated from hardware status and are not persisted beyond driver attachment.

## Dependencies

No external dependencies beyond the include guard. It is included by chip-controller headers.

## Risks and Test Signals

Incorrect transitions would break talker/listener status reporting and wait conditions. Test signals are address/unaddress command handling, serial poll active state, and correct TACS/LACS updates after ATN/address changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_state_machines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_types.h

## Purpose

`gpib_types.h` defines the core kernel data model for linux-gpib: board configuration, driver interface callbacks, board runtime state, event queues, pseudo IRQ support, status queues, descriptors, and per-file private data.

## Important APIs and Types

- `struct gpib_board_config` carries attach-time inputs: firmware blob, I/O base, MMIO base, IRQ, DMA channel, PCI bus/slot filters, sysfs path, and serial number.
- `struct gpib_interface` is the core driver contract. It contains attach/detach and callbacks for read, write, command, control ownership, IFC/REN, EOS, parallel poll, serial poll, status, addressing, T1 delay, local mode, and capability flags.
- `struct gpib_board` stores one physical board's runtime state, callbacks, buffers, locks, timers, device pointers, private driver data, address configuration, timeout, online count, autopoll state, event queue, pseudo IRQ state, copied config, and status flags.
- `struct gpib_event_queue` and `struct gpib_event` hold asynchronous bus events such as clear/trigger/IFC.
- `struct gpib_pseudo_irq` models timer-based polling.
- `struct gpib_status_queue` and `struct gpib_status_byte` track serial-poll bytes per addressed device.
- `struct gpib_descriptor` tracks per-open descriptor address, I/O busy count, kernel busy reference, and flags.
- `struct gpib_file_private` stores descriptor array and module/mutex state per open file.

## Control Flow and Integration

This header is the contract between gpib-common and board drivers. Board modules fill `struct gpib_interface`; gpib-common serializes user access with `user_mutex` and `big_gpib_mutex`, drives timers for timeout, sleeps drivers on `board->wait`, and exposes status/device operations through descriptors.

## State and Persistence Behavior

All state is in-memory for the lifetime of open files, online boards, and loaded modules. `board->config` stores a copy of attach parameters, while hardware drivers own `board->private_data`. Event/status queues persist until consumed or board teardown. Atomic fields and locks coordinate interrupt, timeout, file, and ioctl paths.

## Dependencies

When `__KERNEL__` is defined, it includes Linux GPIB, atomic, device, mutex, wait, scheduler, timer, and interrupt headers. The file is kernel-specific except for the include guard shell.

## Risks and Test Signals

The callback table has many nullable optional methods, so core callers must respect capability flags and NULL checks. Locking order is explicit: `user_mutex` must be first if held across multiple ioctls. Test signals include descriptor lifetime under concurrent I/O/close, timeout wakeups setting TIMO, interrupt wakeups on `board->wait`, event queue overflow/drop behavior, status queue overflow, pseudo IRQ start/stop, and correct module reference ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210.h

## Purpose

`nec7210.h` declares the reusable NEC uPD7210-compatible GPIB controller core. Board drivers embed `struct nec7210_priv`, supply byte-access callbacks, and delegate bus operations and interrupt handling to the exported `nec7210_*` functions.

## Important APIs and Types

- `struct nec7210_priv` stores I/O or MMIO base, register spacing, DMA metadata, register shadow bytes, auxiliary register shadows, state bits, register page lock, byte accessors, chipset type, talker/listener state, board-private extension pointer, and `srq_pending`.
- `init_nec7210_private()` zeroes the structure and initializes `register_page_lock`.
- `read_byte()` and `write_byte()` inline wrappers dispatch to the board's accessors.
- State bit numbers include PIO, DMA read/write, data/command readiness, END, bus error, RFD holdoff, device clear, and address change.
- Interface functions cover read/write/command, control ownership, IFC/REN, EOS, status update, primary/secondary address, parallel poll, serial poll, T1 delay, local mode, reset/online, register bit updates, handshake mode, holdoff release, data read, byte I/O wrappers, and interrupt handling.

## Control Flow and Integration

Board drivers initialize the private structure, set accessors and chip type, call `nec7210_board_reset()`, register IRQs that invoke `nec7210_interrupt()` or `nec7210_interrupt_have_status()`, then call `nec7210_board_online()`. Their `gpib_interface` callbacks commonly become thin wrappers around declared functions.

## State and Persistence Behavior

Register shadow arrays and auxiliary bits must remain synchronized with writes. `state` is the interrupt/transfer coordination bitmap. Talker/listener state mirrors address-status hardware. DMA metadata is present but depends on `NEC_DMA` support and board configuration.

## Dependencies

It includes `gpib_state_machines.h`, Linux types/spinlock/string/interrupt, `gpib_types.h`, and `nec7210_registers.h`.

## Risks and Test Signals

Boards must choose correct byte accessors and offset or all register operations target wrong hardware. Register page locking and AUXMR pacing matter for chips with paged registers or timing constraints. Test signals include command-ready interrupts, PIO read/write with END, RFD holdoff release, address status transitions, bus-error recovery, serial poll request handling, parallel poll completion, and MMIO/PIO wrapper correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210_registers.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210_registers.h

## Purpose

`nec7210_registers.h` defines chipset IDs, register numbers, register bit fields, auxiliary register values, and auxiliary commands for NEC7210-compatible GPIB controller chips.

## Important APIs and Constants

- `enum nec7210_chipset` identifies original NEC7210 and compatible/extended chips such as TNT4882, NAT4882, CB7210, IOT7210, IGPIB7210, and TNT5004.
- Write-register numbers include `CDOR`, `IMR1`, `IMR2`, `SPMR`, `ADMR`, `AUXMR`, `ADR`, and `EOSR`.
- Read-register numbers include `DIR`, `ISR1`, `ISR2`, `SPSR`, `ADSR`, `CPTR`, `ADR0`, and `ADR1`.
- Bit enums cover ISR/IMR data-in/out, errors, device clear, END, command pass-through, address changes, remote/local/lockout, serial request, address status, address mode, address register, serial poll, EOS/handshake modes, and parallel-poll modes.
- `enum aux_cmds` names controller commands such as chip reset, finish handshake, trigger, return to local, send EOI, go to standby, take control, listen/unlisten, execute parallel poll, IFC/REN controls, and secondary-address validation.

## Control Flow and Integration

The NEC7210 core uses these constants for every register read/write and interrupt decode. Board-specific extensions such as INES use base constants plus their own extra register bits.

## State and Persistence Behavior

No state is declared. Constants define the hardware state that `struct nec7210_priv` shadows and updates.

## Dependencies

The header is self-contained except for the include guard. It is consumed by `nec7210.h` and implementation files.

## Risks and Test Signals

Shared enum member names such as `IMR1`, `ADSR`, or `HR_END` can conflict if multiple controller register headers are included into one translation unit without care. Test signals are hardware register programming review, interrupt bit decoding, AUX command behavior, EOS/handshake mode transitions, and supported-chip compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/plx9050.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/plx9050.h

## Purpose

`plx9050.h` defines PLX9050/9052 PCI bridge register offsets and interrupt/control bit constants used by PCI GPIB board drivers.

## Important APIs and Constants

- `PLX9050_INTCSR_REG` and `PLX9050_CNTRL_REG` identify bridge interrupt control/status and control registers.
- `enum plx9050_intcsr_bits` covers local interrupt enables, polarity, status, PCI interrupt enable, software interrupt, and 9052 edge/select extensions.
- `enum plx9050_cntrl_bits` covers user pins, PCI BAR enable mode, read/write mode, retry delay, lock enable, EEPROM controls, reload, software reset, and revision mask.
- `PLX9050_PCI_RETRY_DELAY_BITS(clocks)` encodes retry delay in eight-clock units.

## Control Flow and Integration

There is no runtime logic beyond retry-delay bit encoding. `ines_gpib.c` uses `PLX9050_INTCSR_REG` and interrupt bits to enable PLX local and PCI interrupts during PCI attach.

## State and Persistence Behavior

No in-memory state exists. Values are written to PCI bridge registers by board drivers and persist until reprogrammed or reset.

## Dependencies

The header has its own include guard and no external includes.

## Risks and Test Signals

Incorrect interrupt polarity or enable bits can produce missing or stuck IRQs. Retry-delay encoding truncates by division and masks to the supported field. Test signals include successful PLX-backed PCI attach, shared IRQ behavior, and clean interrupt disable on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/plx9050.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/quancom_pci.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/quancom_pci.h

## Purpose

`quancom_pci.h` defines the small Quancom PCI interrupt control/status register contract used by Quancom GPIB boards.

## Important APIs and Constants

- `QUANCOM_IRQ_CONTROL_STATUS_REG` is the register offset, `0xfc`.
- `QUANCOM_IRQ_ASSERTED_BIT` reports an asserted IRQ.
- `QUANCOM_IRQ_ENABLE_BIT` enables IRQ generation; any write clears the interrupt according to the comment.

## Control Flow and Integration

`ines_gpib.c` uses this header for Quancom variants. Its interrupt handler checks the asserted bit and writes the enable bit back to clear/re-enable. Attach writes the enable bit, and detach writes zero when disabling.

## State and Persistence Behavior

No in-memory state is defined. IRQ enable/asserted state is in the device register.

## Dependencies

The header is self-contained with an include guard.

## Risks and Test Signals

Because any write clears the interrupt, careless writes can lose pending state. Test signals are Quancom attach, IRQ clear/re-enable behavior, no interrupt storm, and detach disabling interrupt generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/quancom_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/tms9914.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/tms9914.h

## Purpose

`tms9914.h` declares the reusable TMS9914-compatible GPIB controller core, including private controller state, register maps, command/bit definitions, and exported operation prototypes.

## Important APIs and Types

- `enum tms9914_holdoff_mode` defines no holdoff, holdoff on EOI, and holdoff on all data.
- `struct tms9914_priv` stores I/O/MMIO base, register spacing, DMA channel, interrupt-mask shadows, address-mode and auxiliary shadows, state bitmap, EOS config, serial-poll status, holdoff mode, parallel-poll config, talker/listener state, parallel-poll flags, primary address flags, holdoff flags, and byte accessors.
- Inline `read_byte()` and `write_byte()` dispatch to controller accessors.
- State bit numbers represent PIO, DMA, read/write/command readiness, END, bus error, and device clear.
- Function prototypes cover read/write/command, take control, standby, system control, IFC/REN, EOS, status, addressing, parallel poll, serial poll, line status, T1 delay, local mode, reset/online, holdoff release/mode, PIO/MMIO accessors, and interrupt handling.
- Register and bit enums map TMS9914 write/read registers, interrupt bits, address bits, bus line status bits, and auxiliary commands.

## Control Flow and Integration

Board drivers such as `hp_82341.c` embed `struct tms9914_priv`, set accessors and base/offset, and delegate most `gpib_interface` callbacks to the TMS9914 core. Interrupt handlers read ISR0/ISR1 and call `tms9914_interrupt_have_status()`.

## State and Persistence Behavior

The private structure maintains software shadows for write-only or mode registers and runtime state bits shared between interrupt handlers and blocking transfers. EOS and holdoff settings persist per attached board.

## Dependencies

It includes Linux types/interrupt plus `gpib_state_machines.h` and `gpib_types.h`.

## Risks and Test Signals

The header defines short names that overlap with NEC7210 register headers, so translation units should avoid including both conflicting maps without namespace care. Holdoff flags and state bits must match the implementation's interrupt behavior. Test signals are TMS9914-backed board reads/writes, bus line status reporting, EOS handling, parallel poll, T1 delay selection, and device-clear/timeout wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/tms9914.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/tnt4882_registers.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/include/tnt4882_registers.h

## Purpose

`tnt4882_registers.h` defines register offsets, status/control bits, FIFO/DMA control bits, and auxiliary commands for National Instruments TNT4882/Turbo-488 style controllers.

## Important APIs and Constants

- Register offsets include 9914-mode auxiliary registers, handshake/configuration registers, counters, FIFOs, command register, timer, status registers, interrupt registers, and bus control/status.
- `tnt_pagein_offset` identifies the alternate-register page-in offset.
- Bus status bits mirror REN, IFC, SRQ, EOI, NRFD, NDAC, DAV, and ATN.
- `enum cfg_bits`, `enum cmdr_bits`, `enum hssel_bits`, `enum imr0_bits`, `enum isr0_bits`, `enum isr3_bits`, `enum keyreg_bits`, `enum sts1_bits`, and `enum sts2_bits` describe FIFO, transfer, interrupt, delay, DMA, and status behavior.
- `enum tnt4882_aux_cmds` includes mode switching, request-service control, page-in, immediate holdoff, clear-END, and 7210/9914 mode commands.
- Auxiliary register bit enums provide no-talking-without-listeners, local parallel poll, holdoff, static interrupt, PP2, and ultra-short T1 settings.

## Control Flow and Integration

This header is a hardware vocabulary for TNT4882-aware code. It is not directly used by the implementation files in this subset, but it complements the NEC/TMS controller headers for other GPIB board drivers.

## State and Persistence Behavior

No in-memory state is declared. State is in hardware registers and any driver-side shadows maintained by users of these constants.

## Dependencies

The header is self-contained and guarded.

## Risks and Test Signals

Many constants share common names with other register headers (`AUXCR`, `IMR0`, `ISR0`), so inclusion ordering and translation-unit scope matter. Test signals are TNT hardware initialization, FIFO reset/start/stop, interrupt decode, mode switching between 9914/7210, T1 delay setting, and bus-status readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/include/tnt4882_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ines/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/ines/Makefile

## Purpose

This Kbuild fragment builds the INES GPIB board driver when `CONFIG_GPIB_INES` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_INES) += ines_gpib.o` compiles `ines_gpib.c` into the kernel/module object selected by the config symbol.

## Control Flow and Integration

Kbuild includes this file from the parent GPIB driver Makefile. The resulting object contains PCI, ISA, and optional PCMCIA INES support plus its gpib-interface registrations.

## State and Persistence Behavior

No runtime state exists.

## Dependencies

The Makefile depends on the kernel Kconfig symbol `CONFIG_GPIB_INES` and on `ines_gpib.c` plus headers in the same and include directories.

## Risks and Test Signals

Build coverage should verify enabled and disabled config cases. A missing parent Makefile entry or Kconfig symbol mismatch would prevent the driver from building even if this fragment is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ines/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ines/ines.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/ines/ines.h

## Purpose

`ines.h` declares board-private state and INES-specific register/bit definitions for iGPIB 7210 boards. It layers INES FIFO, extended-mode, PCI-bridge, and bus-monitor controls on top of the NEC7210 core.

## Important APIs, Types, and Constants

- `enum ines_pci_chip` identifies no PCI bridge, PLX9050, AMCC5920, Quancom, and QuickLogic5030 variants.
- `struct ines_priv` embeds `struct nec7210_priv`, stores PCI device pointer, PLX/AMCC base addresses, IRQ, PCI chip type, and shadowed `extend_mode_bits`.
- `ines_inb()` and `ines_outb()` access INES registers via the embedded NEC7210 I/O base and offset.
- Register enums define FIFO status, ISR3/ISR4, FIFO counts/watermarks, extended status/mode, transfer counters, XDMA control, and bus control monitor.
- Bit enums define FIFO/transfer/IFC/ATN events, FIFO readiness, extended mode behavior, extended status, INES FIFO enable bits in ADMR, DMA control bits, bus line monitor bits, and INES auxiliary commands/register bits.

## Control Flow and Integration

`ines_gpib.c` uses this header for accelerated read/write setup, interrupt decoding, bus line status, T1 delay programming, attach-time PCI bridge handling, and board online/reset flows.

## State and Persistence Behavior

`extend_mode_bits` is a software shadow of `EXTEND_MODE` and persists while attached. The embedded NEC7210 private state carries controller status, register shadows, and transfer state.

## Dependencies

It includes `nec7210.h`, `gpibP.h`, PLX/AMCC/Quancom PCI bridge headers, and `linux/interrupt.h`.

## Risks and Test Signals

The inline I/O helpers assume I/O-port access and correct offset; wrong PCI ID metadata corrupts register selection. FIFO counter width is limited, and `ines_gpib.c` guards transfer counter values above 0xffff. Test signals are accelerated read/write, FIFO watermark IRQs, bus line readback, T1-delay selection, and all supported PCI bridge variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ines/ines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ines/ines_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/ines/ines_gpib.c

## Purpose

`ines_gpib.c` is the board driver for INES iGPIB 7210 hardware. It supports PCI, ISA, and optionally PCMCIA devices, registers accelerated and unaccelerated linux-gpib interfaces, and delegates the base GPIB controller behavior to the NEC7210 core while using INES FIFO/extended registers for faster transfers.

## Important APIs, Types, and Functions

- `ines_line_status()` maps INES bus-control monitor bits to linux-gpib `BUS_*` line status.
- `ines_accel_read()` and `ines_accel_write()` implement FIFO/counter-backed data movement.
- `pio_read()` and `ines_write_wait()` are accelerated transfer helpers around FIFO count and wait conditions.
- `ines_interrupt()` calls `nec7210_interrupt()`, reads INES ISR3/ISR4, pushes IFC events, logs FIFO errors, and wakes sleepers for transfer-count and watermark events.
- `ines_pci_interrupt()` adds Quancom interrupt clear/re-enable behavior before delegating to `ines_interrupt()`.
- `ines_common_pci_attach()`, `ines_pci_attach()`, and `ines_pci_accel_attach()` discover PCI boards, enable devices, request regions and IRQs, program PCI bridge interrupt/timing registers, reset the NEC7210, and call `ines_online()`.
- `ines_isa_attach()`/`ines_isa_detach()` handle configured ISA I/O/IRQ resources.
- Optional PCMCIA code registers a `pcmcia_driver`, configures sockets/windows, tracks `curr_dev`, and attaches via `ines_common_pcmcia_attach()`.
- Module init/exit registers/unregisters the PCI driver and multiple `struct gpib_interface` tables.

## Control Flow

The common attach path calls `ines_generic_attach()` to allocate private data, initialize `nec7210_priv`, set I/O accessors, mark the chip type `IGPIB7210`, and initialize the PCI chip type. PCI attach then searches a custom `pci_ids[]` list with optional bus/slot filters, enables the device, requests all PCI regions, selects GPIB I/O base and offset, stores bridge-specific bases, resets the NEC7210, requests a shared IRQ, and programs bridge-specific interrupt routing. PLX enables local and PCI interrupts, AMCC disables prefetch/write FIFO and sets wait states before enabling add-on interrupts, and Quancom writes its IRQ enable register.

`ines_online()` programs INES auxiliary mode, puts the controller into immediate RFD holdoff, clears extended/DMA state, sets FIFO watermarks and ISR masks for accelerated mode, disables IN/OUT FIFOs for unaccelerated mode, calls `nec7210_board_online()`, and in accelerated mode disables normal data-in/data-out NEC interrupts because FIFO interrupts drive transfer wakeups.

Accelerated read immediately holds off RFD, clears/enables the input FIFO, configures extended-mode last-byte handling for input, sets the transfer counter if more data is expected, enables counter mode, sets holdoff on END, releases holdoff, drains the FIFO until length, END, timeout, or device clear, disables counter mode, and reports END from `RECEIVED_END_BN`.

Accelerated write clears/enables output FIFO, configures output counter mode, optionally enables last-byte handling for EOI, fills FIFO chunks while `num_out_fifo_bytes()` stays under threshold, waits for the last byte to drain, disables counter mode, and reports bytes written as `length - num_out_fifo_bytes()`.

## State and Persistence Behavior

Private state is `struct ines_priv`: embedded NEC7210 state plus PCI device/resource metadata, IRQ number, bridge type, and `extend_mode_bits`. The driver maintains shadowed extended-mode bits to avoid losing unrelated flags. Transfer state is a combination of INES FIFO counts, transfer counter registers, ISR3/ISR4 bits, NEC7210 state bits, and `board->status`. PCMCIA support additionally uses global `curr_dev`.

## Dependencies and Integration Points

The file depends on Linux PCI, optional PCMCIA, I/O port, IRQ, DMA headers, `gpib_pci_ids.h`, INES register definitions, PCI bridge headers, and the NEC7210 core. It integrates with gpib-common by registering interface names `ines_pci`, `ines_pci_unaccel`, `ines_pci_accel`, `ines_isa`, and optional PCMCIA variants.

## Risks and Test Signals

Many attach error paths return `-1` or other errors after partial allocation/resource acquisition; cleanup relies on detach or leaves risk of leaked private data, PCI refs, regions, or IRQs. In `ines_pci_detach()`, the AMCC case checks `plx_iobase` before writing PLX INTCSR, which looks inconsistent with AMCC naming and may fail to disable AMCC interrupts. `ines_set_xfer_counter()` rejects counts above 0xffff but accelerated paths can receive larger lengths; tests should cover large transfers. Optional PCMCIA uses a single global `curr_dev`, limiting multi-card behavior. Test signals are module init unwind paths, PCI bridge variants, ISA attach/detach, accelerated/unaccelerated transfers, END/EOI handling, IFC event queueing, FIFO error logging, timeout/device-clear behavior, and PCMCIA insert/remove/resume if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ines/ines_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/Makefile

## Purpose

This Kbuild fragment builds the LPVO USB GPIB driver when `CONFIG_GPIB_LPVO` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_LPVO) += lpvo_usb_gpib.o` compiles the USB/GPIB adapter driver object.

## Control Flow and Integration

The parent GPIB Makefile includes this fragment. The resulting object registers a USB driver and conditionally registers a gpib interface when USB devices are present.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies

The build depends on `CONFIG_GPIB_LPVO`, USB support, linux-gpib core headers, and `lpvo_usb_gpib.c`.

## Risks and Test Signals

Build tests should cover enabled/disabled config. Since the source has an empty USB ID table by default, build success is separate from automatic device binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/lpvo_usb_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/lpvo_usb_gpib.c

## Purpose

`lpvo_usb_gpib.c` supports the LPVO/Open USB-GPIB adapter by combining a linux-gpib `struct gpib_interface` implementation with a modified USB skeleton bulk I/O driver. The adapter is driven through a text/binary command protocol over an FTDI-style USB bulk device. The USB ID table is intentionally empty because the known FTDI ID is normally handled by `ftdi_sio`; users must bind devices manually or add an ID/rule.

## Important APIs, Types, and Functions

- Adapter protocol constants such as `USB_GPIB_ON`, `USB_GPIB_OFF`, `USB_GPIB_STATUS`, `USB_GPIB_READ`, `USB_GPIB_READ_1`, `USB_GPIB_DEBUG_ON`, `USB_GPIB_SET_LINES`, `USB_GPIB_UNTALK`, and `USB_GPIB_UNLISTEN` define the wire protocol.
- `struct usb_gpib_priv` stores per-board EOS byte/flags, cached timeout, and pointer to the USB skeleton `struct lpvo`.
- Global arrays `lpvo_usb_interfaces[]`, `usb_minors[]`, and `assigned_usb_minors` map USB minors to gpib attach choices under `minors_lock`.
- `send_command()`, `write_loop()`, `set_control_line()`, `one_char()`, and `set_timeout()` implement adapter command exchange and timeout programming.
- `usb_gpib_attach()` selects a USB device by sysfs path, bus/devnum, or `ibbase` minor; opens the USB object; turns the adapter on; enables debug/extended protocol; configures REN/IFC behavior; and disables first-byte timeout.
- `usb_gpib_read()` parses LPVO framed reads with `DLE STX` start, `DLE ETX ACK` end, DLE escaping, single-byte special handling, software EOS detection, and overflow flushing.
- `usb_gpib_write()` frames writes as newline, `IB`, DLE/STX, payload, DLE/ETX/newline, sends the command, and then unlistens.
- `usb_gpib_command()`, control-line callbacks, line status, parallel poll, EOS, status update, and placeholders implement the gpib callback table.
- `struct lpvo` stores USB device/interface, bulk URB/buffers, endpoint addresses, error state, read progress, kref, I/O mutex, wait queue, and write anchor/semaphore.
- `lpvo_probe()`, `lpvo_disconnect()`, suspend/resume/reset hooks, `lpvo_do_open()`, `lpvo_do_release()`, `lpvo_do_read()`, and `lpvo_do_write()` own USB lifecycle and bulk I/O.

## Control Flow

USB probe allocates `struct lpvo`, initializes kref, semaphore, mutex, spinlock, URB anchor, and read wait queue, takes a USB-device reference, discovers bulk endpoints, allocates the read buffer and URB, stores intfdata, optionally registers a raw userspace USB class device, lowers FTDI latency to 1 ms, and calls `usb_gpib_init_module()` to register the gpib interface on the first detected adapter and record the interface/minor in the global table.

GPIB attach locks the minor table, finds the requested adapter by `device_path`, bus/devnum, or USB minor, allocates `usb_gpib_priv`, opens the `struct lpvo` by USB minor, and sends a sequence of adapter setup commands. Detach sends adapter-off, waits briefly, releases the USB object, and frees private data.

Reads first set adapter timeouts if needed. Length-one reads use `USB_GPIB_READ_1` and expect one data byte plus ACK. Multi-byte reads send `USB_GPIB_READ`, require `DLE STX`, then loop through data and control escapes. Data bytes are appended until caller length, software EOS, or `DLE ETX ACK`. If the caller buffer fills before frame end, it discards up to `MAX_READ_EXCESS` bytes looking for the closing frame. Successful framed reads send UNTALK.

Writes allocate a frame buffer, copy the payload without DLE escaping, send it through `send_command()`, set `*bytes_written`, and send UNLISTEN. `send_eoi` is accepted by the signature but not explicitly encoded in the frame.

The skeleton read path serializes with `io_mutex`, waits for ongoing URBs, reports and clears stored errors, strips the two FTDI status bytes at the start of valid bulk reads, and restarts if only the two status bytes were returned. Writes use a semaphore to allow only one URB in flight, allocate coherent DMA memory, anchor the URB, and release resources in the write callback.

## State and Persistence Behavior

Per-board gpib state is in `usb_gpib_priv`, especially cached timeout and EOS software settings. Per-USB-interface state is in `struct lpvo` and persists from probe to disconnect with kref ownership shared by gpib attach and optional raw userspace opens. Global minor tables persist while devices are present and drive gpib interface registration/unregistration. Error state is latched in `dev->errors` and reported once. USB reset sets `errors = -EPIPE` in post-reset.

## Dependencies and Integration Points

The driver depends on the USB core, autosuspend APIs, URBs, USB class device registration when `USER_DEVICE` is enabled, linux-gpib private APIs, FTDI latency control request values, and the LPVO adapter protocol. It integrates with gpib-common through one `gpib_interface` named by `KBUILD_MODNAME`, with `skip_check_for_command_acceptors = 1`.

## Risks and Test Signals

The USB device ID table is empty by design, so automatic binding will not occur without external configuration. `usb_gpib_write()` explicitly notes DLE bytes are not escaped and can only safely send ASCII-like data; binary payloads containing DLE can corrupt framing. Several gpib callbacks are stubs returning success or zero (`primary_address`, `secondary_address`, serial poll response/status, T1 delay, parallel-poll configuration/response, return-to-local), which limits compliance. `send_eoi` is not meaningfully handled in write. `usb_gpib_attach()` returns errors after `lpvo_do_open()` and allocation without always releasing the opened device/private data unless detach follows. `lpvo_do_write()` copies `count` bytes into a buffer sized for `writesize`, which is `min(count, MAX_TRANSFER)`; large writes risk overflow unless callers never exceed `MAX_TRANSFER`. Test signals are manual USB binding, attach by path/bus/minor, setup command ACKs, timeout programming, framed reads including DLE escaping and overflow flush, writes with and without DLE bytes, disconnect during I/O, suspend/reset recovery, raw user-device open/read/write if enabled, and gpib-core behavior around stubbed callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/lpvo_usb_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/nec7210/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/nec7210/Makefile

## Purpose

This Kbuild fragment builds the NEC7210 reusable GPIB controller support object when `CONFIG_GPIB_NEC7210` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_NEC7210) += nec7210.o` compiles `nec7210.c`, which exports symbols used by NEC7210-compatible board drivers.

## Control Flow and Integration

The parent GPIB Makefile includes this fragment. Board drivers that embed `struct nec7210_priv` depend on this object being available either built-in or as a module dependency.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies

The target depends on `CONFIG_GPIB_NEC7210`, `nec7210.c`, `board.h`, and headers under `drivers/gpib/include`.

## Risks and Test Signals

If board drivers select NEC7210 helpers without this object, symbol resolution fails. Build tests should cover modular and built-in combinations of NEC7210 core and dependent boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/nec7210/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/nec7210/board.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/nec7210/board.h

## Purpose

`board.h` is a local umbrella header for `nec7210.c`. It imports gpib private APIs, Linux I/O/module/scheduler/delay helpers, and the public NEC7210 controller declaration.

## Important APIs and Types

The file defines no new APIs. It includes `gpibP.h`, `linux/io.h`, `linux/module.h`, `linux/sched.h`, `linux/delay.h`, and `nec7210.h`.

## Control Flow and Integration

There is no control flow. It simplifies includes for the NEC7210 implementation.

## State and Persistence Behavior

No state is declared.

## Dependencies

It is kernel-only and depends on linux-gpib private headers plus standard kernel headers needed by `nec7210.c`.

## Risks and Test Signals

As an umbrella header, risks are mostly include-order and dependency creep. Test signals are successful compilation of `nec7210.c` across configurations with and without I/O-port support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/nec7210/board.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/nec7210/nec7210.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/nec7210/nec7210.c

## Purpose

`nec7210.c` implements and exports reusable support for NEC uPD7210-compatible GPIB controller chips. It provides generic bus operations, interrupt decoding, status maintenance, PIO transfer loops, optional ISA DMA scaffolding, register reset/online setup, and I/O accessor wrappers used by board-specific drivers such as INES.

## Important APIs and Functions

- EOS and poll functions: `nec7210_enable_eos()`, `nec7210_disable_eos()`, `nec7210_parallel_poll()`, `nec7210_parallel_poll_configure()`, `nec7210_parallel_poll_response()`, `nec7210_serial_poll_response()`, and `nec7210_serial_poll_status()`.
- Address/status functions: `nec7210_primary_address()`, `nec7210_secondary_address()`, `nec7210_update_status_nolock()`, and `nec7210_update_status()`.
- Register/handshake helpers: `nec7210_set_reg_bits()`, `nec7210_set_handshake_mode()`, `nec7210_read_data_in()`, and `nec7210_release_rfd_holdoff()`.
- Bus-control functions: `nec7210_take_control()`, `nec7210_go_to_standby()`, `nec7210_request_system_control()`, `nec7210_interface_clear()`, `nec7210_remote_enable()`, `nec7210_t1_delay()`, and `nec7210_return_to_local()`.
- Transfer functions: `nec7210_command()`, `nec7210_read()`, and `nec7210_write()`, backed by internal `pio_read()`, `pio_write_wait()`, and `pio_write()`.
- Interrupt and lifecycle: `nec7210_interrupt()`, `nec7210_interrupt_have_status()`, `nec7210_board_reset()`, and `nec7210_board_online()`.
- I/O wrappers: `nec7210_ioport_read_byte()`, `nec7210_ioport_write_byte()`, locking I/O-port variants, MMIO variants, and locking MMIO variants.

## Control Flow

Status update reads `ADSR`, updates CIC/ATN, derives talker/listener states, sets or clears TACS/LACS, checks serial-poll pending completion, and relies on the interrupt handler for remaining status bits. The locked wrapper clears caller-requested status bits and calls the no-lock update under `board->spinlock`.

Command writes wait for `COMMAND_READY_BN`, bus error, or timeout, write command bytes to `CDOR`, and after the last byte wait again for completion or error. PIO reads wait for `READ_READY_BN`, device clear, or timeout, switch to holdoff-on-all after the first byte to make holdoff state reliable, read data via `nec7210_read_data_in()`, stop on END, and release RFD holdoff between bytes. PIO writes wait for talker-active plus `WRITE_READY_BN`, handle device clear/timeout/bus error, resend the last byte on recoverable NEC7210 bus errors up to a computed cap, and write bytes to `CDOR`.

`nec7210_write()` reserves the final byte when `send_eoi` is requested, sends the prefix by PIO, waits for write readiness, issues `AUX_SEOI`, then writes the final byte. DMA read/write code exists behind `NEC_DMA`, but normal compiled flow uses PIO because the write path has DMA disabled with `if (0 /*priv->dma_channel*/)` and comments note unreliable DMA write recovery.

Interrupt handling reads ISR1/ISR2, records SRQ, REM/LOK changes, END, data-in, data-out, command-out ready, command pass-through, bus errors, device clear, triggers, and address changes. It pushes GPIB events for device clear and trigger, updates board status on enabled interrupt bits or ATN changes, wakes `board->wait`, and returns `IRQ_HANDLED` only when relevant status occurred.

Reset writes chip reset, disables interrupts, clears status registers, unconfigures parallel poll, sets address mode and handshake defaults, clears AUXRE, and enables command pass-through. Online writes addresses, enables relevant IMR1/IMR2 bits, and sends power-on.

## State and Persistence Behavior

The core stores per-controller state in `struct nec7210_priv`: register shadows, auxiliary shadows, bitmap state, talker/listener states, and serial-request pending state. `board->status` is the shared gpib status word. Transfer readiness and error conditions are communicated through bitmap bits and `board->wait`. Register page lock serializes access for paged/timing-sensitive registers and enforces a 1 microsecond delay before AUXMR writes in locking wrappers.

## Dependencies and Integration Points

The implementation depends on `board.h`, Linux I/O, module, scheduler, delay, bitops, optional DMA APIs, and the gpib core event/status definitions. It exports symbols for board drivers to link against and expects callers to provide initialized byte accessors and board private state.

## Risks and Test Signals

`nec7210_parallel_poll()` has a FIXME for timeout support and can wait indefinitely except for signal interruption. `nec7210_read()` and `nec7210_write()` clear `DEV_CLEAR_BN` with comments marking this as wrong/XXX, which can mask device-clear state. DMA write support is documented as unreliable and effectively disabled. There is a potential race comment around DMA write completion and `CDOR`. The helper `nec7210_atn_has_changed()` returns `-1` defensively but practical callers treat nonzero as changed. Test signals are PIO read/write/command under normal, timeout, signal, bus-error, and device-clear cases; EOI final-byte behavior; END/EOS handling; serial-poll request and completion; REM/LOK/SRQ status transitions; event queueing; reset/online register programming; and I/O-port versus MMIO accessor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/nec7210/nec7210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/Makefile

## Purpose

This Kbuild fragment builds the National Instruments USB GPIB driver when `CONFIG_GPIB_NI_USB` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_NI_USB) += ni_usb_gpib.o` compiles the NI USB GPIB driver object.

## Control Flow and Integration

The fragment is included by the parent GPIB driver build. Although only the Makefile is in this work item, the object name shows the corresponding implementation is `ni_usb_gpib.c`.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies

The target depends on `CONFIG_GPIB_NI_USB` and the presence of `ni_usb_gpib.c` plus kernel USB/GPIB dependencies.

## Risks and Test Signals

Build tests should verify enabled/disabled config paths and module dependency resolution. Runtime risks belong to `ni_usb_gpib.c`, not this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/Makefile -->

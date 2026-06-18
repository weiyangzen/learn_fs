# subset-b-001299 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.c

## Purpose
`ni_usb_gpib.c` is the Linux-GPIB adapter driver for National Instruments and compatible USB-to-GPIB devices. It binds USB interfaces, exposes one `gpib_interface` named `ni_usb_b`, translates Linux-GPIB read/write/command/control operations into the NI USB bulk/control protocol, manages status monitoring through interrupt URBs and vendor requests, and handles USB suspend/resume and unplug races.

## Important APIs, types, and functions
- Module and bus entry points are `ni_usb_init_module()`, `ni_usb_exit_module()`, `ni_usb_driver_probe()`, `ni_usb_driver_disconnect()`, `ni_usb_driver_suspend()`, and `ni_usb_driver_resume()`.
- Linux-GPIB attach/lifecycle hooks are `ni_usb_attach()` and `ni_usb_detach()`, with board operations collected in `ni_usb_gpib_interface`.
- Core GPIB operations are `ni_usb_read()`, `ni_usb_write()`, `ni_usb_command()`, `ni_usb_take_control()`, `ni_usb_go_to_standby()`, `ni_usb_request_system_control()`, `ni_usb_interface_clear()`, `ni_usb_remote_enable()`, `ni_usb_update_status()`, `ni_usb_line_status()`, `ni_usb_primary_address()`, `ni_usb_secondary_address()`, `ni_usb_parallel_poll()`, and `ni_usb_t1_delay()`.
- USB transport helpers include `ni_usb_send_bulk_msg()`, `ni_usb_receive_bulk_msg()`, the nonblocking variants, `ni_usb_receive_control_msg()`, `ni_usb_bulk_complete()`, `ni_usb_timeout_handler()`, and `ni_usb_stop()`.
- Protocol parsing and framing helpers include `ni_usb_timeout_code()`, `ni_usb_parse_status_block()`, `parse_board_ibrd_readback()`, `ni_usb_parse_register_read_block()`, `ni_usb_parse_termination_block()`, `ni_usb_parse_reg_write_status_block()`, and `ni_usb_write_registers()`.

## Control flow
USB probe stores matching interfaces in the global `ni_usb_driver_interfaces[]` array under `ni_usb_hotplug_lock`; actual Linux-GPIB binding happens later in `ni_usb_attach()`, which chooses an unused probed interface, assigns endpoints by product ID, runs model-specific readiness/serial-number setup, starts the interrupt URB, disables then enables monitor bits, programs TNT4882/NEC7210-compatible registers through `ni_usb_init()`, and records board identity.

Bulk GPIB I/O follows a send-command/receive-status pattern. Reads build an IBRD command block with EOS, timeout code, length complement, and holdoff/end-clear register writes; they then receive packed 15- or 30-byte data blocks plus status and parse them with `parse_board_ibrd_readback()`. Writes and command transfers build padded bulk payloads, append a termination block, receive a status block, translate NI error codes to Linux errors, and update `board->status`. Command transfers are chunked to 16 bytes because USB-B adapters reject longer command batches. Register-oriented operations use `ni_usb_write_registers()` to bulk-write `(device,address,value)` triplets and check the returned count/status.

Status monitoring is split between synchronous polling and interrupt URBs. `ni_usb_set_interrupt_monitor()` arms a vendor wait request for selected IBSTA bits, `ni_usb_interrupt_complete()` parses an interrupt status block, clears monitored bits, wakes waiters, and resubmits the URB, while `ni_usb_soft_update_status()` updates Linux-GPIB status flags and pushes device-clear/trigger events. Suspend disables monitor bits, shuts hardware down, and kills URBs; resume resubmits the interrupt URB, reruns model-specific ready/init flows, restores monitor bits, and reapplies IFC/REN state when needed.

## State and persistence behavior
All persistent driver state is runtime memory. `struct ni_usb_priv` stores the bound USB interface, endpoint numbers, EOS settings, monitored status bits, bulk and interrupt URBs, the interrupt buffer, four mutexes, a bulk timeout timer/context, product ID, and remembered REN state. The file also maintains a global probed-interface array protected by `ni_usb_hotplug_lock`. Hardware state is programmed into adapter subdevices over USB; there is no disk persistence. On detach/disconnect, the code clears interface data, kills URBs, nulls `bus_interface`, and frees the private object.

## Dependencies and integration points
The driver depends on Linux USB core APIs, timers/completions/mutexes, Linux-GPIB core types in `gpibP.h`, NEC7210 register semantics, and TNT4882 register definitions. It integrates with user-visible GPIB operations through `gpib_register_driver()` and with USB hotplug through `usb_register()`. Supported devices include NI USB-B, USB-HS, USB-HS+, Keithley/Measurement Computing compatible IDs, and MC USB-488 devices listed in the USB ID table.

## Risks and edge cases
Concurrency is the main risk: disconnect, suspend, interrupt URB completion, bulk transfers, and GPIB operations all coordinate through multiple mutexes plus `ni_usb_hotplug_lock`. Error paths in `ni_usb_attach()` often return after allocating private state or URBs without central cleanup. Bulk timeout handling shares one `bulk_urb` and timer context, so stale completion/timer ordering must be correct. `ni_usb_line_status()` intentionally uses trylock/nonblocking bulk helpers because it can be called from wait paths, which means callers must tolerate `-EBUSY`. Protocol parsing assumes exact response lengths and magic bytes for several model variants; unexpected but harmless firmware differences may become hard errors. Several void GPIB hooks cannot report USB/register failures.

## Test signals
Useful validation includes attach/detach for each supported product ID, unplug during read/write/command, suspend/resume with REN and controller state restored, long reads across extended data blocks, command chunking above 16 bytes, EOS/EOI handling, no-listener/no-bus/timeout NI error-code translation, interrupt monitor wakeups for SRQ/ATN/CIC/LACS/TACS/DCAS/DTAS, `line_status()` under concurrent transfer load, and fault injection for URB submission, allocation, short reads, malformed status blocks, and USB reset/configuration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.h

## Purpose
`ni_usb_gpib.h` is the private protocol and state header for the NI USB GPIB driver. It declares USB IDs, endpoint assignments, adapter subdevice IDs, per-board private state, status/register wire-format structures, NI USB bulk command IDs, error codes, vendor control requests, and small helpers for encoding bulk register messages.

## Important APIs, types, and functions
Important types are `struct ni_usb_priv`, `struct ni_usb_urb_ctx`, `struct ni_usb_status_block`, and `struct ni_usb_register`. Enums define supported USB product IDs, USB-B/HS/HS+ endpoint addresses, NI USB subdevice selectors, bulk block IDs such as `NIUSB_REG_WRITE_ID` and `NIUSB_IBRD_DATA_ID`, adapter error codes such as `NIUSB_TIMEOUT_ERROR`, and vendor requests such as `NI_USB_STOP_REQUEST` and `NI_USB_WAIT_REQUEST`. Inline helpers include `nec7210_to_tnt4882_offset()`, `ni_usb_bulk_termination()`, `ni_usb_bulk_register_write_header()`, `ni_usb_bulk_register_write()`, `ni_usb_bulk_register_read_header()`, and `ni_usb_bulk_register_read()`.

## Control flow
The header has no standalone execution, but its helper functions construct the byte streams used by `ni_usb_gpib.c`: bulk operations append command IDs, register triplets, padding, and termination blocks, while control requests use the request constants to stop I/O, wait for status, poll readiness, read serial numbers, and run HS+ extra initialization.

## State and persistence behavior
`struct ni_usb_priv` is the central runtime state object. It tracks endpoint selection, EOS mode/character, monitor bits, URB ownership, transfer locks, timer state, product ID, and REN state. `struct ni_usb_status_block` and `struct ni_usb_register` describe transient wire-format data decoded from or encoded into USB transfers. No persistent storage is represented.

## Dependencies and integration points
The header depends on Linux mutex, semaphore, USB, timer, and Linux-GPIB private definitions. It integrates the USB adapter protocol with NEC7210/TNT4882 register addressing by providing `nec7210_to_tnt4882_offset()` and subdevice IDs consumed by register-write sequences in the C file.

## Risks and edge cases
The structs and enum values are protocol contracts: changing IDs, endpoint numbers, byte ordering, or helper output lengths would break adapter communication. `ni_usb_status_block.count` is parsed from a two's-complement count in the C file, so callers must not treat the raw fields as native device-neutral data. The shared `bulk_urb` and `context` fields imply only one bulk transfer at a time.

## Test signals
Compile coverage catches missing constants, but meaningful validation comes from USB protocol tests that verify register-write/read framing, termination blocks, endpoint selection per product ID, timeout-code handling, and correct status/error parsing in the C driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/pc2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/pc2/Makefile

## Purpose
This Kbuild file builds the PCII/PCIIa GPIB driver object when `CONFIG_GPIB_PC2` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_GPIB_PC2) += pc2_gpib.o`. There are no runtime APIs in the Makefile itself.

## Control flow
Kbuild includes or omits `pc2_gpib.o` based entirely on the `CONFIG_GPIB_PC2` symbol.

## State and persistence behavior
The file has build-time state only and no runtime persistence.

## Dependencies and integration points
It depends on the kernel Kbuild system and the `CONFIG_GPIB_PC2` Kconfig option. The resulting object registers the `pcII`, `pcIIa`, `pcIIa_cb7210`, and `pcII_IIa` Linux-GPIB interfaces.

## Risks and edge cases
Renaming the C file or config symbol without updating this Makefile would silently drop or break the module build.

## Test signals
Build with `CONFIG_GPIB_PC2=y` and `CONFIG_GPIB_PC2=m`; verify `pc2_gpib.o` is compiled and links against the NEC7210/GPIB core helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/pc2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/pc2/pc2_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/pc2/pc2_gpib.c

## Purpose
`pc2_gpib.c` implements Linux-GPIB support for PCII, PCIIa, PCIIa CB7210, and PCII/IIa compatible ISA GPIB boards. It is a thin board-specific wrapper around the shared NEC7210 core, responsible for ISA I/O region layout, IRQ handling, optional ISA DMA setup, interrupt-clear quirks, and registration of four board interface variants.

## Important APIs, types, and functions
The private board state is `struct pc2_priv`, embedding `struct nec7210_priv` plus IRQ and PCIIa interrupt-clear I/O address. Interrupt handlers are `pc2_interrupt()` and `pc2a_interrupt()`. Attach/detach paths include `pc2_generic_attach()`, `pc2_attach()`, `pc2_detach()`, `pc2a_common_attach()`, `pc2a_attach()`, `pc2a_cb7210_attach()`, `pc2_2a_attach()`, `pc2a_common_detach()`, `pc2a_detach()`, and `pc2_2a_detach()`. Most GPIB operation hooks are wrappers over NEC7210 helpers: `pc2_read()`, `pc2_write()`, `pc2_command()`, `pc2_take_control()`, `pc2_go_to_standby()`, `pc2_request_system_control()`, address, poll, EOS, status, and local-control helpers.

## Control flow
Module initialization registers four `gpib_interface` instances and unwinds previously registered ones if any registration fails. `pc2_attach()` allocates private state, configures NEC7210 I/O-port access with byte offset 1, requests an 8-port region at `config->ibbase`, resets the board, requests an IRQ if configured, registers a pseudo IRQ for polling ATN changes, writes the 8 MHz internal counter register, and brings the NEC7210 online. `pc2a_common_attach()` handles PCIIa-style sparse registers at offset `0x400`, validates base addresses and IRQ range, requests one port per register plus the IRQ-clear port, installs `pc2a_interrupt()`, clears pending interrupt state, resets, sets the clock, and goes online.

Interrupt handling is direct. PCII calls `nec7210_interrupt()` under `board->spinlock`. PCIIa reads ISR1/ISR2, clears the external interrupt circuit at `0x2f0 + irq`, and calls `nec7210_interrupt_have_status()`. Detach paths stop pseudo IRQs, free IRQs/DMA, reset hardware, release all requested regions, free coherent DMA buffers when compiled in, and free private state.

## State and persistence behavior
The driver keeps only in-memory runtime state in `struct pc2_priv` and the embedded NEC7210 state. Hardware state lives in ISA I/O registers. Optional DMA state is conditional on `PC2_DMA`, but the default path logs that DMA is disabled because the driver is not adapted to `isa_register_driver()` and lacks a `struct device`. There is no cross-boot persistence.

## Dependencies and integration points
The file depends on Linux I/O port, IRQ, DMA, spinlock, module, and Linux-GPIB infrastructure plus `nec7210.h`. It integrates with the GPIB core through `gpib_register_driver()` and delegates bus protocol behavior to NEC7210 library functions. Configuration comes from `struct gpib_board_config` fields such as `ibbase`, `ibirq`, and `ibdma`.

## Risks and edge cases
Several attach error paths return after region/IRQ/private allocation without a centralized cleanup call, so partial failures can leak resources until module removal or retry. PCIIa accepts only four hard-coded base addresses and IRQ 2 through 7. The PCIIa sparse region uses multiple one-byte `request_region()` calls, increasing cleanup complexity. The pseudo IRQ always uses `pc2_interrupt()` even in `pc2a_common_attach()`, which is worth regression testing because the real IRQ handler differs. DMA support is effectively disabled in normal builds.

## Test signals
Build coverage for all four interfaces, attach/detach with valid and invalid PCIIa base/IRQ values, IRQ delivery for both PCII and PCIIa clear-register behavior, pseudo IRQ polling for ATN, NEC7210 read/write/command/status operations, resource-failure injection in attach, and repeated attach/detach cycles are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/pc2/pc2_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tms9914/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/tms9914/Makefile

## Purpose
This Kbuild file builds the shared TMS9914 GPIB support object when `CONFIG_GPIB_TMS9914` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_GPIB_TMS9914) += tms9914.o`. There are no runtime APIs in the Makefile itself.

## Control flow
Kbuild includes `tms9914.o` only when the TMS9914 config symbol is selected. The object exports helper symbols used by board-specific TMS9914-based drivers.

## State and persistence behavior
The file affects build composition only and stores no runtime state.

## Dependencies and integration points
It depends on Kbuild and `CONFIG_GPIB_TMS9914`. The compiled object integrates with board drivers through exported GPL/non-GPL symbols in `tms9914.c`.

## Risks and edge cases
If TMS9914 board drivers are enabled without this object, exported helper references would fail at link or module load time.

## Test signals
Build with `CONFIG_GPIB_TMS9914=y` and `=m`, and build a dependent board driver to confirm the exported symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tms9914/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tms9914/tms9914.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/tms9914/tms9914.c

## Purpose
`tms9914.c` is the shared Linux-GPIB protocol library for boards built around TI TMS9914-compatible GPIB controller logic. It implements controller/listener/talker state transitions, programmed I/O read/write/command transfer loops, EOS and holdoff behavior, parallel and serial poll support, status/line-state decoding, interrupt handling, reset/online sequences, and I/O-port/MMIO byte access wrappers.

## Important APIs, types, and functions
Exported GPIB operation helpers include `tms9914_take_control()`, `tms9914_take_control_workaround()`, `tms9914_go_to_standby()`, `tms9914_interface_clear()`, `tms9914_remote_enable()`, `tms9914_request_system_control()`, `tms9914_t1_delay()`, `tms9914_return_to_local()`, `tms9914_enable_eos()`, `tms9914_disable_eos()`, `tms9914_parallel_poll()`, `tms9914_parallel_poll_configure()`, `tms9914_parallel_poll_response()`, `tms9914_serial_poll_response()`, `tms9914_serial_poll_status()`, `tms9914_primary_address()`, `tms9914_secondary_address()`, `tms9914_update_status()`, `tms9914_line_status()`, `tms9914_read()`, `tms9914_write()`, and `tms9914_command()`.

Interrupt and lifecycle helpers are `tms9914_interrupt()`, `tms9914_interrupt_have_status()`, `tms9914_board_reset()`, and `tms9914_online()`. I/O access wrappers are `tms9914_ioport_read_byte()`, `tms9914_ioport_write_byte()`, `tms9914_iomem_read_byte()`, and `tms9914_iomem_write_byte()`. Internal helpers manage talker/listener state, EOS checks, holdoff release, PIO waits, and address-state emulation.

## Control flow
Controller operations write TMS9914 auxiliary commands and then busy-wait briefly for ATN assertion/release. Reads set a holdoff mode depending on remaining length and EOS, release holdoff before each byte, wait on `board->wait` for `READ_READY_BN`, read `DIR`, check END/EOS, and reenter holdoff when required. Writes wait for `WRITE_READY_BN`, write bytes to `CDOR`, optionally assert EOI before the final byte, and propagate timeout, bus error, or device-clear conditions. Command transfers wait for `COMMAND_READY_BN`, write command bytes to `CDOR`, and call `check_my_address_state()` to emulate active talker/listener state for the board's primary and secondary address.

Interrupt flow starts by reading ISR0/ISR1, which clears chip interrupt status, then `tms9914_interrupt_have_status()` sets state bits for END/read/write/command readiness, handles serial poll active state, records SRQ, validates or invalidates command holdoff for secondary addressing and parallel-poll configuration commands, reports bus errors, pushes IFC/device-trigger/device-clear events, services APT secondary-address interrupts, updates board status, and wakes waiters when enabled interrupt bits fired. Reset disables interrupts, clears status registers, clears serial/parallel poll state, and enables holdoff-all mode; online programs addresses and interrupt masks and releases reset.

## State and persistence behavior
State is runtime-only and split between `struct gpib_board` status/wait/event fields and `struct tms9914_priv` fields such as interrupt masks, state bits, EOS byte/flags, holdoff mode, talker/listener state, primary address tracking, serial poll status, and parallel poll configuration. Hardware state lives in TMS9914 registers. No persistent storage exists.

## Dependencies and integration points
The file depends on Linux delay, spinlock, wait queues through the GPIB board, I/O port or MMIO accessors, and TMS9914 register/bit definitions in `tms9914.h`. Board-specific drivers provide `struct tms9914_priv` with `read_byte`/`write_byte` methods and call these helpers from their `gpib_interface` hooks.

## Risks and edge cases
Holdoff handling is subtle: reads must release and reassert holdoff at the right byte boundaries to avoid losing END/EOS or deadlocking the bus. The Agilent 82350B workaround deliberately refuses synchronous take-control because TCS can wedge that implementation. Interrupt command parsing accepts or invalidates parallel-poll configuration based on prior state; malformed command sequences can affect DAC holdoff. Wait paths rely on board timeout bits being set elsewhere. Secondary addressing is handled partly by software state and APT interrupts, so address-state transitions need coverage.

## Test signals
Tests should cover PIO read/write with and without EOI/EOS, holdoff-all and holdoff-on-EOI modes, command transfers that address/unaddress the local board, synchronous/asynchronous take-control, standby timeout, serial poll request/clear behavior, parallel poll configuration/unconfiguration, line-status decoding, IFC/GET/DCL event delivery, APT secondary-address validation, bus-error propagation, and reset/online cycles for both I/O-port and MMIO accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tms9914/tms9914.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/Makefile

## Purpose
This Kbuild file builds the National Instruments TNT4882/NAT4882/NEC7210 GPIB driver module when `CONFIG_GPIB_NI_PCI_ISA` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_GPIB_NI_PCI_ISA) += tnt4882.o` and composes `tnt4882.o` from `tnt4882_gpib.o` and `mite.o`.

## Control flow
Kbuild links the board driver and MITE PCI helper into one module/built-in object under the NI PCI/ISA config symbol.

## State and persistence behavior
The Makefile has build-time state only. Runtime state is in the compiled C files.

## Dependencies and integration points
It depends on Kbuild and `CONFIG_GPIB_NI_PCI_ISA`. It integrates TNT4882 GPIB code with MITE PCI discovery/window setup required for NI PCI boards.

## Risks and edge cases
Dropping `mite.o` from `tnt4882-objs` would break PCI attach because `tnt4882_gpib.c` calls `mite_init()`, `mite_setup()`, `mite_unsetup()`, and `mite_cleanup()`.

## Test signals
Build with `CONFIG_GPIB_NI_PCI_ISA=y` and `=m`; verify the resulting `tnt4882` object includes both `tnt4882_gpib.o` and `mite.o` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.c

## Purpose
`mite.c` is a small helper for NI MITE PCI interface chips used by NI PCI GPIB boards. It discovers National Instruments PCI devices, stores them in a global list, enables selected devices, maps the MITE and DAQ BARs, programs the I/O device window, and tears mappings/devices down.

## Important APIs, types, and functions
The global list head is `struct mite_struct *mite_devices`. Public functions are `mite_init()`, `mite_setup()`, `mite_unsetup()`, and `mite_cleanup()`. `mite_setup()` enables the PCI device, sets bus mastering, requests regions, maps BAR0 as MITE registers and BAR1 as DAQ/GPIB registers, writes `MITE_IODWBSR`, and marks the entry used.

## Control flow
At TNT4882 module init, `mite_init()` walks all PCI devices with vendor `PCI_VENDOR_ID_NATINST`, allocates a `mite_struct` for each, takes a device reference, and pushes it onto `mite_devices`. `ni_pci_attach()` later selects an unused matching entry and calls `mite_setup()`. Detach calls `mite_unsetup()` to unmap BARs, release PCI regions, disable the device, and clear `used`. Module exit calls `mite_cleanup()` to drop PCI references and free list nodes.

## State and persistence behavior
Runtime state is the global linked list of `struct mite_struct`, each holding PCI identity, mapped register bases, physical BAR addresses, a used flag, and a preallocated DMA-chain array. No persistent state exists, and the DMA-chain array is not actively configured by this file.

## Dependencies and integration points
The file depends on PCI core, I/O remapping, region management, and MITE register constants from `mite.h`. It integrates only with `tnt4882_gpib.c`, which consumes the global list and mapped `daq_io_addr` for TNT4882 register access.

## Risks and edge cases
`mite_setup()` has partial-failure cleanup gaps: if requesting regions or the second `ioremap()` fails after earlier resources were acquired, the caller must be careful because this function does not unwind all prior steps before returning. `mite_init()` lists all NI vendor devices and leaves board-type filtering to `ni_pci_attach()`. The global list is not locked, so it assumes module-level attach/remove serialization through the GPIB path.

## Test signals
PCI enumeration with multiple NI devices, attach selection by bus/slot, setup/unsetup resource accounting, BAR mapping failure injection, repeated attach/detach, and module unload reference cleanup are the most relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.h

## Purpose
`mite.h` declares the NI MITE helper state, public helper prototypes, and register/bit definitions needed to map and program the MITE PCI bridge for NI GPIB boards.

## Important APIs, types, and functions
Primary types are `struct mite_dma_chain` and `struct mite_struct`. The header exposes `mite_devices`, inline helpers `mite_irq()` and `mite_device_id()`, and functions `mite_init()`, `mite_cleanup()`, `mite_setup()`, `mite_unsetup()`, and `mite_list_devices()`. It defines MITE DMA channel register offsets and bitfields such as `MITE_CHOR`, `MITE_CHCR`, `MITE_TCR`, `MITE_IODWBSR`, `WENAB`, and many DMA mode/control bits.

## Control flow
The header has no independent control flow. `tnt4882_gpib.c` calls the declared helpers to discover and activate PCI devices, then uses `mite_irq()` and `mite_device_id()` during board matching/IRQ setup.

## State and persistence behavior
`struct mite_struct` represents runtime PCI bridge state: linked-list membership, used flag, PCI device reference, BAR physical addresses, mapped MITE/DAQ I/O addresses, a near-end flag, and an in-memory DMA ring. There is no durable persistence.

## Dependencies and integration points
The header depends on Linux PCI types and bit macros. It is part of the TNT4882 driver module and bridges `mite.c` with `tnt4882_gpib.c`. The register constants mirror MITE hardware documentation and are suitable for later DMA support even though current GPIB code primarily uses window setup and IRQ/device ID helpers.

## Risks and edge cases
The header declares `mite_list_devices()` but `mite.c` in this subset does not define it, so any future caller would fail to link unless another translation unit supplies it. Many register bitfields are hardware ABI constants; incorrect values would misprogram DMA or address windows. `extern inline` helper style can be sensitive to compiler/kernel inline semantics.

## Test signals
Compile/link coverage for the declared helpers, PCI attach paths using `mite_irq()` and `mite_device_id()`, and any future DMA-channel programming tests using the register constants are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/mite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/tnt4882_gpib.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/tnt4882_gpib.c

## Purpose
`tnt4882_gpib.c` implements Linux-GPIB support for National Instruments PCI, ISA, ISA-PnP, and optional PCMCIA boards using TNT4882, TNT5004, NAT4882, or NEC7210-compatible chips. It wraps shared NEC7210 protocol operations, adds TNT4882 FIFO-accelerated transfers and register paging, handles MITE-backed PCI mapping, ISA/PNP/PCMCIA resource setup, interrupt processing, serial/parallel poll variants, and registers many `gpib_interface` names for accelerated and unaccelerated modes.

## Important APIs, types, and functions
The private state is `struct tnt4882_priv`, embedding `struct nec7210_priv` plus MITE/PNP pointers, IRQ, TNT interrupt masks, and auxiliary-G bits. Register access helpers are `tnt_readb()`, `tnt_writeb()`, `tnt_paged_readb()`, and `tnt_paged_writeb()`. Accelerated data paths are `tnt4882_accel_read()`, `generic_write()`, `tnt4882_accel_write()`, and `tnt4882_command()`, with FIFO helpers such as `fifo_word_available()`, `fifo_byte_available()`, `fifo_space_available()`, `fifo_xfer_done()`, `drain_fifo_words()`, and `tnt_transfer_count()`.

Interrupt and protocol wrappers include `tnt4882_internal_interrupt()`, `tnt4882_interrupt()`, `tnt4882_read()`, `tnt4882_write()`, `tnt4882_command_unaccel()`, `tnt4882_take_control()`, `tnt4882_go_to_standby()`, `tnt4882_request_system_control()`, status/address/EOS/poll helpers, and `tnt4882_serial_poll_response2()`. Lifecycle paths include `tnt4882_init()`, `tnt4882_board_reset()`, `ni_pci_attach()`, `ni_pci_detach()`, `ni_isa_attach_common()`, ISA variant attach wrappers, `ni_isa_detach()`, module init/exit, and optional PCMCIA probe/config/attach/detach functions.

## Control flow
Module init registers a minimal PCI driver, registers ISA/NAT4882/NEC7210 and PCI accelerated/unaccelerated GPIB interfaces, optionally registers PCMCIA interfaces and driver, then calls `mite_init()`. PCI attach selects an unused MITE entry by optional bus/slot and device ID, maps it with `mite_setup()`, uses the DAQ BAR as the TNT register base, requests a shared IRQ, detects TNT4882 versus TNT5004 via `CSR`, and runs `tnt4882_init()`. ISA attach either discovers an ISA-PnP board or uses configured base/IRQ, requests the I/O range, maps it with `ioport_map()`, requests IRQ, and initializes. PCMCIA attach follows the same NEC7210/TNT init pattern using the current PCMCIA device resources.

Accelerated reads program FIFO direction/count/configuration, release holdoff, enable DONE/NEF interrupts, drain 16-bit FIFO words while waiting on `board->wait`, handle the final odd byte, stop the transfer if short, synchronize pending interrupts, and report END/timeouts/device clear/address changes. Accelerated writes and command transfers program FIFO output mode, load the two's-complement byte count, fill FIFO words while space is available, wait for DONE, stop the engine, process pending interrupts, and compute bytes written from the residual counter. Nonaccelerated variants delegate to NEC7210 helpers and force immediate holdoff after failed reads.

Interrupt processing first delegates NEC7210 interrupt handling, then reads TNT ISR0/ISR3, pushes IFC events, masks one-shot FIFO/DONE interrupt bits, writes updated IMR3, and wakes waiters on TNT interrupt/link-controller events. Reset disables TNT interrupt masks, read-clears status, and calls NEC7210 reset. Initialization soft-resets Turbo488 logic, configures one-chip mode for TNT chips, enables interrupt pass-through, forces RFD holdoff, programs auxiliary-G, brings NEC7210 online, and enables IFC/ATN-related TNT interrupts.

## State and persistence behavior
State is runtime-only. `struct tnt4882_priv` tracks chip type through the embedded NEC7210 state, mapped I/O base, IRQ, MITE or PNP ownership, interrupt mask bits, and auxiliary register G. FIFO counters and interrupt masks live in hardware registers. Global PCI MITE state is owned by `mite.c`; optional PCMCIA state uses `curr_dev` and per-card `local_info_t`. No disk persistence exists.

## Dependencies and integration points
The driver depends on Linux PCI, ISA-PnP, optional PCMCIA, I/O port/MMIO APIs, IRQs, Linux-GPIB core, NEC7210 helpers, TNT4882 register definitions, and the local MITE helper. It integrates with Linux-GPIB through many `gpib_interface` registrations: `ni_pci`, `ni_pci_accel`, ISA TNT/NAT/NEC variants, and optional PCMCIA variants. PCI ID tables include NI GPIB/Plus/PXI/PMC/PCIe devices and Measurement Computing/CEC compatible devices.

## Risks and edge cases
Attach error paths often return immediately after partial resource acquisition, so region, IRQ, private-data, or MITE mappings can leak on mid-attach failure. `tnt4882_pci_probe()` is a no-op; PCI enumeration is used mainly to populate driver binding while actual board selection comes from the MITE scan. Accelerated transfers depend on correct interrupt mask toggling and manual pending-interrupt processing; missed DONE/NEF/NFF events can hang waiters. NAT4882 paged register access is protected by a register-page spinlock and must not be bypassed. Some detach paths check `nec_priv->iobase` even though attach primarily sets `mmiobase`, which can affect reset/release behavior. PCMCIA code is conditional and has legacy global `curr_dev` behavior.

## Test signals
Test PCI attach by device ID and bus/slot filters, ISA configured and ISA-PnP attach, optional PCMCIA attach, chip detection for TNT4882/TNT5004/NAT4882/NEC7210, accelerated read/write including odd byte counts, END and timeout handling, bus-error translation for command versus data writes, serial-poll request transitions with `serial_poll_response2`, parallel-poll TNT5004 local configuration, IFC event delivery, resource-failure injection in attach, and repeated module load/unload for MITE cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/tnt4882_gpib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpio/Kconfig

## Purpose
`drivers/gpio/Kconfig` is the top-level Linux GPIO configuration menu for the source tree. It enables the generic GPIO library, legacy and character-device userspace ABIs, GPIO IRQ-chip support, shared GPIO support, generic helper libraries, and a large set of concrete GPIO controller/expander/test drivers grouped by bus or device class.

## Important APIs, types, and functions
This is Kconfig rather than C code, so the important units are symbols and menu blocks. Core symbols include `GPIOLIB`, `GPIOLIB_FASTPATH_LIMIT`, `OF_GPIO`, `GPIO_ACPI`, `GPIOLIB_IRQCHIP`, `GPIO_SHARED`, `DEBUG_GPIO`, `GPIO_SYSFS`, `GPIO_SYSFS_LEGACY`, `GPIO_CDEV`, `GPIO_CDEV_V1`, `GPIO_GENERIC`, `GPIO_REGMAP`, `GPIO_SWNODE_UNDEFINED`, `GPIO_MAX730X`, `GPIO_IDIO_16`, and `GPIO_I8255`. Driver menus group memory-mapped GPIO controllers, port-mapped I/O controllers, I2C/SPI/USB expanders, MFD GPIO providers, PCI expanders, virtual GPIO drivers, and debugging utilities.

## Control flow
The top-level `menuconfig GPIOLIB` gates almost the entire file through `if GPIOLIB`. Selecting `GPIOLIB` exposes core ABI/debug options and driver menus. Each driver symbol declares `bool`/`tristate` type, dependencies such as architecture, bus, firmware, ACPI/OF, `HAS_IOMEM`, `HAS_IOPORT`, or `COMPILE_TEST`, and helper selections such as `GPIO_GENERIC`, `GPIO_REGMAP`, `GPIOLIB_IRQCHIP`, `REGMAP_*`, `IRQ_DOMAIN`, `GENERIC_IRQ_CHIP`, `CONFIGFS_FS`, and `AUXILIARY_BUS`. Defaults are mostly platform-driven, for example SoC GPIO drivers defaulting to `y` on their native architecture or USB/MFD proxy drivers defaulting with their parent.

## State and persistence behavior
The file produces build-time `.config` state. It does not execute at runtime, but the selected symbols determine which GPIO core features and drivers are built in, built as modules, or omitted. ABI choices such as `GPIO_SYSFS`, `GPIO_CDEV`, and `GPIO_CDEV_V1` determine runtime userspace interfaces. `GPIOLIB_FASTPATH_LIMIT` stores a numeric configuration that affects stack versus dynamic allocation thresholds in GPIO core code.

## Dependencies and integration points
The file integrates GPIO drivers with architecture symbols, bus subsystems (`I2C`, `SPI_MASTER`, `USB`, `PCI`, `MCB`, `SIOX`, `VIRTIO`), firmware interfaces (`OF`, `ACPI`, Raspberry Pi firmware, ZynqMP firmware), MFD parent devices, regmap, irqdomain/generic IRQ chip support, configfs/debugfs test infrastructure, and auxiliary bus support. It also nudges userspace toward the modern character device ABI by making `GPIO_SYSFS` select `GPIO_CDEV`.

## Risks and edge cases
Kconfig mistakes can create invalid build combinations: missing `depends on HAS_IOMEM/HAS_IOPORT` can expose drivers on unsupported architectures, missing `select GPIOLIB_IRQCHIP` or IRQ domain dependencies can break interrupt-capable drivers, and careless `select` use can force dependencies without their prerequisites. `GPIOLIB_FASTPATH_LIMIT` warns that incorrect values can cause stack corruption. Deprecated ABIs (`GPIO_SYSFS`, `GPIO_CDEV_V1`, and `GPIO_MOCKUP`) remain selectable for compatibility and need regression coverage. Large menu organization also risks duplicate or misplaced symbols when adding new drivers.

## Test signals
Relevant validation includes `olddefconfig`/`allmodconfig`/`allyesconfig`/`randconfig` builds across representative architectures, `COMPILE_TEST` coverage, dependency checks for each bus menu, ABI checks for `GPIO_CDEV` and deprecated sysfs/v1 paths, GPIO IRQ-chip build combinations, configfs/debugfs virtual driver tests, and scripts/kconfig checks for unmet direct dependencies or recursive selects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/Kconfig -->

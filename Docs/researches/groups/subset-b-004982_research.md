# Research group subset-b-004982

This grouped worker report covers NFC ST95HF, TRF7970A, virtual NCI, and NTB framework/hardware source files. Each section is delimited with the required `BEGIN_FILE_RESEARCH` and `END_FILE_RESEARCH` markers so reconciliation can split the report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/core.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/core.c

## Purpose

This file is the core Linux NFC digital-layer driver for the STMicroelectronics ST95HF NFC transceiver. It binds as an SPI driver, powers and resets the chip, registers an `nfc_digital_dev`, and implements initiator-side NFC operations for ISO14443A, ISO14443B, and ISO15693. It delegates raw SPI transfer details to `st95hf/spi.c` while keeping all NFC protocol selection, frame handling, WTX handling, IRQ completion, and lifecycle coordination in this file.

## Important APIs, types, and functions

The central state object is `struct st95hf_context`, which contains the SPI transport context, NFC digital device pointers, enable GPIO, optional regulator, the current transmission flag, current RF protocol/technology, RATS/WTX `fwi` timing state, and synchronization primitives. `struct cmd`, `struct param_list`, and `cmd_array[]` encode ST95HF commands such as echo, protocol select, register writes, WTX response, field-off, and ISO15693 select.

The internal command helper `st95hf_send_recv_cmd()` constructs ST95HF command packets from `cmd_array[]`, applies optional parameter substitutions, sends them over SPI, and optionally receives synchronous status responses. `st95hf_echo_command()`, `st95hf_send_spi_reset_sequence()`, and `st95hf_por_sequence()` implement bring-up and recovery. `st95hf_select_protocol()`, `secondary_configuration_type4a()`, `secondary_configuration_type4b()`, and `iso14443_config_fdt()` configure RF protocol and frame delay timing.

Digital-layer entry points are collected in `st95hf_nfc_digital_ops`: `st95hf_in_configure_hw()`, `st95hf_in_send_cmd()`, `st95hf_switch_rf()`, and a placeholder `st95hf_abort_cmd()`. Target-mode methods are stubs that return success without implementing peer-to-peer behavior. Driver binding is handled through `st95hf_probe()`, `st95hf_remove()`, `st95hf_id`, `st95hf_spi_of_match`, and `module_spi_driver()`.

## Control flow and state behavior

Probe allocates `st95hf_context`, stores the nested SPI context in device driver data, enables the optional `st95hfvin` regulator, initializes completions and locks, obtains the `enable` GPIO, installs a falling-edge threaded IRQ, performs a SPI reset sequence, runs POR via repeated echo checks, allocates an NFC digital device with ST95HF protocol masks, registers it, and initializes the semaphore/mutex used for asynchronous exchanges.

The normal initiator flow is `in_configure_hw()` selecting RF technology and framing, followed by `in_send_cmd()` wrapping the caller SKB with ST95HF command headers. For Type A frames it appends `sendrcv_trflag` and records whether the command is a RATS request. It allocates a receive SKB, stores the completion callback context, takes `exchange_lock`, and sends the SPI command as `ASYNC`; the IRQ thread later receives and completes the request.

The hard IRQ distinguishes synchronous internal command completion from asynchronous NFC exchange completion. If `spicontext.req_issync` is true it completes the SPI wait and returns. Otherwise the threaded handler reads the response, checks remove state under `rm_lock`, handles WTX requests in-line by changing frame delay timing and transmitting a WTX response, validates ST95HF and CRC error status, trims protocol-specific status/CRC bytes, restores default timing after WTX, then calls the digital-layer callback and releases `exchange_lock`.

Remove unregisters and frees the digital device under `rm_lock`, marks `nfcdev_free`, waits for the outstanding asynchronous exchange semaphore, sends a reset command, delays for reset completion, and disables the regulator. Persistent state is only in memory and in hardware registers; there is no filesystem persistence.

## Dependencies and integration points

This file depends on the Linux NFC digital framework (`net/nfc/digital.h`), SPI helper functions from `spi.h`, GPIO descriptors, regulators, IRQ threading, sk_buffs, and device tree compatible `st,st95hf`. The NFC subsystem calls the digital ops, while the SPI subsystem owns probe/remove. The chip-specific command constants and response interpretation tightly couple the file to ST95HF firmware behavior.

## Risks and edge cases

The asynchronous request lifecycle relies on `exchange_lock` being taken before a command and released exactly once from the IRQ thread; missed IRQs or SPI-send failures must release it correctly. The IRQ thread uses a static `wtx` flag, which is acceptable only if instances are effectively single-device or serialized; multiple devices could share that static state. `st95hf_abort_cmd()` is empty, so abort semantics depend on higher layers tolerating no immediate cancellation. Response trimming assumes minimum response sizes and protocol-specific layout, so malformed short responses risk invalid access unless lower transport/hardware prevents them. Probe initializes `rm_lock` after device registration, which means any immediate callback/IRQ path before initialization would be hazardous, although typical registration flow likely avoids it.

## Test signals

Useful validation includes module probe/remove with regulator and GPIO present, POR echo retry paths, synchronous protocol-select commands, each supported RF technology and framing, RATS response parsing with and without TA1/TB1, WTX request handling, CRC error propagation, timeout/error responses from ST95HF, and remove while an async exchange is pending. Hardware tests should watch SPI traffic, IRQ ordering, semaphore release, NFC polling behavior, and clean regulator/GPIO state after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.c

## Purpose

This file implements the low-level SPI transport functions used by the ST95HF NFC driver. It is intentionally small: it serializes SPI access, sends ST95HF command buffers, waits for synchronous interrupt completion when requested, and reads normal or echo responses from the chip.

## Important APIs, types, and functions

The public functions are `st95hf_spi_send()`, `st95hf_spi_recv_response()`, and `st95hf_spi_recv_echo_res()`, all exported with `EXPORT_SYMBOL_GPL` and declared in `spi.h`. They operate on `struct st95hf_spi_context`, especially its `spidev`, `done`, `spi_lock`, and `req_issync` fields.

`st95hf_spi_send()` builds a single transmit `spi_message`, marks whether the request is synchronous, sends it with `spi_sync()`, and for `SYNC` requests waits up to 1000 ms for the IRQ handler to complete `done`. `st95hf_spi_recv_response()` first transmits the ST95HF receive command and reads the two-byte response header, computes the full response length including long-frame support using header bits `0x60`, then issues a second SPI transfer for the remaining payload. `st95hf_spi_recv_echo_res()` performs the one-byte echo response read sequence.

## Control flow and state behavior

All three functions hold `spicontext->spi_lock` around SPI bus operations, so the higher-level driver can interleave synchronous configuration commands and asynchronous data exchange without concurrent bus transactions. `st95hf_spi_send()` sets `req_issync` before sending; the top-half IRQ handler in `core.c` checks that flag and completes `done` for synchronous commands. Asynchronous sends return as soon as `spi_sync()` completes, leaving response handling to the threaded IRQ path.

The response reader writes into a caller-provided buffer and returns the total response length. It does not allocate memory or persist state outside `req_issync`.

## Dependencies and integration points

The implementation depends on the Linux SPI API and on the IRQ/completion convention in `core.c`; without the ST95HF IRQ handler completing `done`, synchronous sends time out. It also relies on ST95HF command codes from `spi.h`.

## Risks and edge cases

The response length computed from the chip header is trusted and there is no local maximum-buffer check in `st95hf_spi_recv_response()`. Callers must pass a buffer large enough for the device-reported length. `req_issync` is protected by the SPI lock during send but read from IRQ context without that lock, so ordering depends on command/IRQ sequencing and normal completion semantics. A missing IRQ for synchronous commands causes a fixed one-second timeout.

## Test signals

Tests should cover SPI send failures, synchronous timeout, successful IRQ completion, echo reads, normal short responses, long-frame response length calculation, and concurrent callers contending on `spi_lock`. Hardware traces should show the receive command followed by a two-byte header read and then a payload read of exactly the computed length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.h

## Purpose

This header defines the ST95HF SPI transport interface shared between the core ST95HF NFC driver and the transport implementation. It centralizes command opcodes, reset length, synchronous/asynchronous request typing, the SPI context structure, and function prototypes.

## Important APIs, types, and functions

The basic ST95HF SPI commands are `ST95HF_COMMAND_SEND`, `ST95HF_COMMAND_RESET`, and `ST95HF_COMMAND_RECEIVE`; `ST95HF_RESET_CMD_LEN` documents the one-byte reset command length. `enum req_type` distinguishes `SYNC` commands, which require IRQ completion before returning, from `ASYNC` commands, whose responses are handled later. `struct st95hf_spi_context` stores `req_issync`, `struct spi_device *spidev`, `struct completion done`, and `struct mutex spi_lock`.

The prototypes are `st95hf_spi_send()`, `st95hf_spi_recv_response()`, and `st95hf_spi_recv_echo_res()`.

## Control flow and state behavior

The header has no executable control flow but defines the state contract used by `core.c` and `spi.c`: the core driver initializes the completion and mutex, the send helper updates `req_issync`, and the IRQ handler completes `done` for synchronous transactions.

## Dependencies and integration points

It depends only on `<linux/spi/spi.h>` for SPI device definitions and indirectly on completion/mutex declarations from kernel headers included by that path. It is private to the ST95HF driver directory and should remain aligned with the transport behavior in `spi.c`.

## Risks and edge cases

Any change to `enum req_type` or `struct st95hf_spi_context` must be kept consistent with both IRQ-side and SPI-side code. Because the context embeds synchronization objects, callers must initialize it before any send/receive call and must not copy it after initialization.

## Test signals

Compile coverage of the ST95HF module is the main signal for this header. Runtime tests should indirectly verify that the `SYNC`/`ASYNC` split and completion state defined here match actual command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/trf7970a.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/trf7970a.c

## Purpose

This file is the Linux SPI driver for the TI TRF7970A RFID/NFC transceiver. It supports initiator and target modes through the NFC digital framework, covering MIFARE, ISO14443A/B, FeliCa, ISO15693, and NFC-DEP protocol masks. The driver owns chip power sequencing, runtime PM, register programming, FIFO transmit/receive, IRQ handling, command timeout handling, device tree quirks, and NFC digital ops.

## Important APIs, types, and functions

The central state object is `struct trf7970a`. It records the state-machine state, SPI/regulator/GPIO handles, digital device pointer, quirk flags, initiator/abort flags, active TX/RX SKBs, completion callback, cached register values, current technology/framing, guard time, mode-detect RF technology, timeout-work state, and optional RX gain reduction.

Low-level helpers include `trf7970a_cmd()`, `trf7970a_read()`, `trf7970a_read_cont()`, `trf7970a_write()`, `trf7970a_read_irqstatus()`, `trf7970a_update_iso_ctrl_register()`, and `trf7970a_update_rx_gain_reduction()`. Data movement is handled by `trf7970a_transmit()`, `trf7970a_fill_fifo()`, and `trf7970a_drain_fifo()`. Completion helpers are `trf7970a_send_upstream()` and `trf7970a_send_err_upstream()`.

The state machine uses `enum trf7970a_state` with states for powered off, RF off, idle, RX blocked, waiting for TX FIFO, waiting for RX data, waiting for RX continuation, waiting to issue ISO15693 EOF, listening, and listening with mode detection. NFC digital callbacks are collected in `trf7970a_nfc_ops`, including initiator configure/send, target configure/send/listen/listen_md/get_rf_tech, RF switch, and abort.

Probe/remove and PM entry points are `trf7970a_probe()`, `trf7970a_remove()`, `trf7970a_suspend()`, `trf7970a_resume()`, `trf7970a_pm_runtime_suspend()`, and `trf7970a_pm_runtime_resume()`.

## Control flow and state behavior

Probe requires a device tree node, configures SPI mode 1 and 8-bit words, reads quirks (`irq-status-read-quirk`, `en2-rf-quirk`), obtains EN/EN2 GPIOs, validates the 13.56 MHz or 27.12 MHz clock, parses optional `ti,rx-gain-reduction-db`, installs a rising-edge threaded IRQ, enables VIN and VDD_IO regulators, configures voltage-dependent register bits, allocates and registers the NFC digital device, enables runtime PM autosuspend, and performs startup power sequencing.

Power transitions are explicit. `trf7970a_power_up()` enables VIN, respects EN2 errata, asserts EN, waits for oscillator/device readiness, and moves to RF_OFF. `trf7970a_init()` soft-initializes the chip, applies RX gain reduction, writes IO/modulator/FIFO/special-function defaults, and invalidates the ISO control cache. `trf7970a_switch_rf_on()` runtime-resumes and initializes from RF_OFF to IDLE; `trf7970a_switch_rf_off()` clears RF_ON, moves to RF_OFF, and releases runtime PM with autosuspend.

Initiator configuration first selects technology in `trf7970a_in_config_rf_tech()` and then framing in `trf7970a_in_config_framing()`. The framing path may test for an existing RF field before turning the field on, updates ISO control and modulation registers, and waits protocol-specific guard time. Per-command configuration inspects Type 2 commands to toggle 4-bit ACK/NACK receive mode and inspects ISO15693 flags to adjust data rate/subcarrier and decide whether an EOF must be issued for write/lock responses.

`trf7970a_send_cmd()` validates idle state, handles pending abort, allocates an RX SKB if the command expects a response, re-enables RX if noise previously blocked it, performs per-command config, stores callback state, builds the five-byte transmit prefix, clears stale IRQ status, and sends up to one FIFO worth of payload. `trf7970a_transmit()` schedules timeout work depending on whether more FIFO data remains, an EOF is pending, or normal RX data is expected.

The IRQ handler is mutex-protected and is paired with delayed timeout work. It reads interrupt status, ignores RF-off/no-status cases, handles idle noise by blocking RX, refills TX FIFO on TX low-watermark, drains RX FIFO on receive interrupts, copes with TX-only completion for no-response commands, applies delayed target-mode framing changes, detects active target RF mode when listening with mode detection, and reports errors upstream. Timeout work either ignores a timeout that lost a race with IRQ cancellation, treats WAIT_FOR_RX_DATA_CONT as receive complete, issues ISO15693 EOF, or completes with `-ETIMEDOUT`.

Abort behavior is intentionally delayed for active transmits: `trf7970a_abort_cmd()` marks `aborting`, and `trf7970a_send_upstream()` converts a non-error response to `-ECANCELED` just before callback. Listening aborts can complete immediately by canceling timeout work and sending `-ECANCELED`.

## Dependencies and integration points

The driver integrates with SPI, device tree, GPIO descriptors, regulators, runtime/system PM, delayed workqueues, IRQ threading, sk_buffs, and the NFC digital subsystem. It uses device tree compatible `ti,trf7970a` and SPI device ID `trf7970a`. Runtime users are NFC digital core initiator/target paths; hardware behavior depends on TRF7970A FIFO, IRQ status, direct commands, and ISO control register semantics.

## Risks and edge cases

The biggest risks are races between IRQ and timeout work, which the driver mitigates with `trf->lock` and `ignore_timeout` but still depends on careful cancellation ordering. State-machine transitions are sensitive: invalid RF-off/on or send/listen requests can force RF off or return errors. FIFO accounting and SKB expansion must handle long frames without losing partial data. Type 2 and ISO15693 command sniffing assumes command buffers are long enough for accessed bytes. Runtime PM paths must not power down outside RF_OFF, and shutdown during active operations must complete callbacks with cancellation. The IRQ status read quirk changes read width and must match silicon.

## Test signals

High-value tests include probe with and without optional EN2 and gain properties, both supported clock frequencies, regulator voltage variants, runtime suspend/resume, system suspend/resume, initiator polling for each technology/framing, Type 2 read versus write ACK behavior, ISO15693 speed and EOF-option commands, FIFO payloads larger than 127 bytes, target listen and listen-with-mode-detect, abort before and during command execution, RF-noise induced RX block/unblock, no-response commands, timeout-only receive completion, and error IRQ propagation. Hardware traces should confirm power sequencing delays, SPI prefix format, FIFO refill timing, and IRQ/timeout ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/trf7970a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/virtual_ncidev.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/virtual_ncidev.c

## Purpose

This file implements a virtual NCI device exposed as a misc character device named `virtual_nci`. It is a simulation/testing bridge between user space and the kernel NFC NCI core: kernel NCI outbound frames become readable bytes on the misc device, and user-space writes are injected back into the NCI receive path.

## Important APIs, types, and functions

`struct virtual_nci_dev` stores the allocated `struct nci_dev`, a mutex, a single pending outbound `send_buff`, a wait queue, and a running flag. The NCI controller ops are `virtual_nci_open()`, `virtual_nci_close()`, and `virtual_nci_send()`. Character-device operations are `virtual_ncidev_open()`, `virtual_ncidev_close()`, `virtual_ncidev_read()`, `virtual_ncidev_write()`, and `virtual_ncidev_ioctl()`.

The only ioctl is `IOCTL_GET_NCIDEV_IDX`, which copies the associated `nfc_dev->idx` to user space. Registration is through `module_misc_device(miscdev)`.

## Control flow and state behavior

Opening `/dev/virtual_nci` allocates a private virtual device, allocates an NCI device with broad virtual protocol masks, initializes synchronization, stores the private data in the file, and registers the NCI device. NCI core open sets `running = true`; close frees any pending send buffer and clears running.

When the NCI core sends a frame, `virtual_nci_send()` takes the mutex, rejects the send if a previous frame is still pending or the device is not running, copies the SKB into `send_buff`, wakes readers, and consumes the original SKB. User-space reads block until `send_buff` is available, copy out up to `count` bytes, pull consumed bytes from the SKB, and free it when empty. User-space writes allocate an SKB, copy input bytes into it, and call `nci_recv_frame()` to inject it into the NFC core.

## Dependencies and integration points

The file depends on the NFC NCI core (`nci_allocate_device`, `nci_register_device`, `nci_recv_frame`), miscdevice infrastructure, user-copy helpers, mutexes, wait queues, and SKBs. It has no hardware dependencies and uses mode `0600`, limiting the device node to privileged or owner access.

## Risks and edge cases

The send path allows only one pending outbound SKB; if user space does not read promptly, subsequent NCI sends fail and drop their SKBs. `virtual_nci_send()` returns `-1` instead of a conventional negative errno. The read wait condition checks `send_buff` without explicitly considering device close, so blocked reads depend on file lifecycle and wakeups from send. `virtual_ncidev_close()` unregisters/free NCI state but does not explicitly free `send_buff` unless NCI close already ran. The code uses `kzalloc_obj(*vdev)`, which is a local macro/helper expectation in this source tree and should be verified against the kernel baseline.

## Test signals

Tests should open the device, obtain the NCI index via ioctl, bring the NCI device up, verify outbound NCI frames become readable in partial and full reads, verify writes are delivered to `nci_recv_frame()`, exercise close while buffers are pending, attempt concurrent readers/writers, and confirm send rejection when `running` is false or `send_buff` is occupied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/virtual_ncidev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/Kconfig

## Purpose

This Kconfig file defines the top-level Non-Transparent Bridge configuration menu. It gates the NTB framework on PCI support, exposes optional MSI interrupt forwarding support, includes hardware and test submenus, and defines the NTB transport client option.

## Important APIs, types, and functions

The key symbols are `NTB`, `NTB_MSI`, and `NTB_TRANSPORT`. `NTB` is a tristate menuconfig depending on `PCI`. `NTB_MSI` is a bool depending on `PCI_MSI` and documents MSI forwarding support. `NTB_TRANSPORT` is a tristate client that exposes queue-pair APIs to other drivers.

## Control flow and state behavior

There is no runtime flow. Build-time inclusion is controlled by the symbols and by `source` lines for `drivers/ntb/hw/Kconfig` and `drivers/ntb/test/Kconfig`, both active only inside `if NTB`.

## Dependencies and integration points

The file integrates the NTB subsystem with kernel configuration and the recursive Kconfig tree for hardware drivers, tests, and transport. It is paired with `drivers/ntb/Makefile`.

## Risks and edge cases

Misconfigured dependencies can expose hardware drivers without PCI support or hide client drivers. Enabling `NTB_MSI` requires hardware driver support for MSI interrupt creation and may consume an extra memory window.

## Test signals

Configuration tests should verify `menuconfig NTB` visibility only with PCI, `NTB_MSI` visibility only with PCI_MSI, hardware submenu availability under NTB, and build coverage for `NTB=m/y` plus `NTB_TRANSPORT=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/Makefile

## Purpose

This Makefile builds the NTB framework, hardware/test subdirectories, and optional transport client according to Kconfig symbols.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB) += ntb.o hw/ test/` builds the core object and descends into hardware/test directories when NTB is enabled. `obj-$(CONFIG_NTB_TRANSPORT) += ntb_transport.o` builds the transport client. `ntb-y := core.o` sets the core object contents, and `ntb-$(CONFIG_NTB_MSI) += msi.o` conditionally adds MSI support.

## Control flow and state behavior

There is no runtime behavior; the file controls link composition and subdirectory traversal.

## Dependencies and integration points

It pairs with the top-level NTB Kconfig and depends on `core.c`, optional `msi.c`, `ntb_transport.c`, and child Makefiles under `hw/` and `test/`.

## Risks and edge cases

If `CONFIG_NTB` is disabled but a transport or hardware object is selected incorrectly elsewhere, build rules may not descend as expected. Optional MSI code must be guarded by `CONFIG_NTB_MSI` in both Makefile and code.

## Test signals

Build matrix checks for `CONFIG_NTB=y/m`, `CONFIG_NTB_MSI=y`, and `CONFIG_NTB_TRANSPORT=y/m` are sufficient signals for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/core.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/core.c

## Purpose

This file implements the generic Linux NTB bus/framework. Hardware drivers register `struct ntb_dev` instances on the `ntb` bus, and client drivers register `struct ntb_client` drivers that bind to those devices. The core also manages client context callbacks for link, doorbell, and message events and provides default two-port topology helpers.

## Important APIs, types, and functions

Exported framework APIs include `__ntb_register_client()`, `ntb_unregister_client()`, `ntb_register_device()`, `ntb_unregister_device()`, `ntb_set_ctx()`, `ntb_clear_ctx()`, `ntb_link_event()`, `ntb_db_event()`, `ntb_msg_event()`, `ntb_default_port_number()`, `ntb_default_peer_port_count()`, `ntb_default_peer_port_number()`, and `ntb_default_peer_port_idx()`.

The internal bus callbacks are `ntb_probe()`, `ntb_remove()`, and `ntb_dev_release()`. `ntb_bus` is registered at module init and unregistered at exit.

## Control flow and state behavior

Client registration validates `ntb_client_ops`, initializes the embedded `driver`, assigns the NTB bus, module owner, and driver name, then calls `driver_register()`. Device registration validates the NTB device, PCI device, and hardware ops, initializes the release completion, sets the bus, parent, release method, device name from `pci_name()`, clears client context, initializes `ctx_lock`, and calls `device_register()`.

When a client binds, `ntb_probe()` takes a device reference, converts the generic device/driver to NTB types, and calls the client's probe. If probe fails, it drops the reference. Remove invokes the client's remove callback and drops the reference. `ntb_unregister_device()` calls `device_unregister()` and waits for `ntb_dev_release()` to complete, giving hardware drivers a clear lifetime boundary before freeing the enclosing object.

Client callback context is protected by `ctx_lock`. `ntb_set_ctx()` rejects invalid ops and existing context, then stores `ctx` and `ctx_ops` under the spinlock. Clear and event-dispatch functions also use the spinlock, making event callbacks callable from interrupt paths but requiring callbacks to obey atomic-context constraints if invoked there.

## Dependencies and integration points

The file depends on `linux/ntb.h` for NTB structures/validation helpers, PCI for parent naming, and the Linux driver core bus API. Hardware drivers such as AMD and EPF call `ntb_register_device()` and event helpers; client drivers call `ntb_register_client()` wrappers and `ntb_set_ctx()`.

## Risks and edge cases

Event callbacks run while `ctx_lock` is held, so callback implementations must not call back into APIs that attempt to take the same lock or sleep if the event comes from IRQ context. `ntb_set_ctx()` checks `ntb->ctx_ops` before acquiring the spinlock, so concurrent double-set attempts rely on external client serialization. Lifetime is tied to reference balancing in probe/remove and release completion; missing `put_device()` paths would leak NTB devices.

## Test signals

Validation should include registering/unregistering dummy hardware devices and clients, failed client probe paths, context set/clear rejection paths, event dispatch with and without callbacks, unregister waiting for release, and default topology helper outputs for primary, secondary, B2B upstream/downstream, and invalid topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/Kconfig

## Purpose

This Kconfig file is the NTB hardware-driver submenu aggregator. It does not define symbols itself; it includes Kconfig files for supported hardware families.

## Important APIs, types, and functions

It sources `drivers/ntb/hw/amd/Kconfig`, `idt/Kconfig`, `intel/Kconfig`, `epf/Kconfig`, and `mscc/Kconfig`.

## Control flow and state behavior

There is no runtime behavior. Build-time visibility comes from the sourced hardware Kconfig files and the parent `if NTB` in the top-level NTB Kconfig.

## Dependencies and integration points

This file connects the NTB core configuration menu to AMD, IDT, Intel, generic EPF, and Switchtec/MSCC hardware drivers. It is paired with `drivers/ntb/hw/Makefile`.

## Risks and edge cases

Adding a new hardware driver requires updating both this aggregator and the hardware Makefile; otherwise a symbol may be visible but not built, or built without a visible option.

## Test signals

Kconfig tests should confirm all sourced hardware symbols appear under the NTB menu and remain hidden when `CONFIG_NTB` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/Makefile

## Purpose

This Makefile descends into hardware-specific NTB driver directories based on Kconfig symbols.

## Important APIs, types, and functions

It maps `CONFIG_NTB_AMD` to `amd/`, `CONFIG_NTB_IDT` to `idt/`, `CONFIG_NTB_INTEL` to `intel/`, `CONFIG_NTB_EPF` to `epf/`, and `CONFIG_NTB_SWITCHTEC` to `mscc/`.

## Control flow and state behavior

There is no runtime behavior. It controls build traversal for selected hardware providers.

## Dependencies and integration points

The file must stay consistent with `drivers/ntb/hw/Kconfig` and each child directory Makefile.

## Risks and edge cases

Symbol/directory mismatches cause selected drivers not to compile or unselected directories to be traversed. This file also assumes child directories contain valid Makefiles.

## Test signals

Build matrix coverage that enables each NTB hardware symbol individually is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Kconfig

## Purpose

This Kconfig file defines the AMD NTB hardware driver option.

## Important APIs, types, and functions

The single symbol is `NTB_AMD`, a tristate option named "AMD Non-Transparent Bridge support". It depends on `X86_64` and documents support for AMD NTB on capable Zeppelin hardware.

## Control flow and state behavior

There is no runtime behavior; selecting this symbol controls whether the AMD hardware driver directory builds.

## Dependencies and integration points

It is sourced by `drivers/ntb/hw/Kconfig` and matched by `drivers/ntb/hw/Makefile` plus `drivers/ntb/hw/amd/Makefile`.

## Risks and edge cases

The dependency is architecture-only; actual device support still depends on matching PCI IDs in `ntb_hw_amd.c`. If new AMD platforms are supported, help text and PCI IDs may need updates.

## Test signals

Config tests should verify visibility on x86_64 when NTB is enabled and hidden on non-x86_64 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Makefile

## Purpose

This Makefile builds the AMD NTB hardware driver object when selected.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB_AMD) += ntb_hw_amd.o` maps the Kconfig symbol to the driver source.

## Control flow and state behavior

There is no runtime behavior.

## Dependencies and integration points

It pairs with `amd/Kconfig` and the source/header files `ntb_hw_amd.c` and `ntb_hw_amd.h`.

## Risks and edge cases

If the object name changes or multi-object composition is introduced, this Makefile must be updated. Otherwise the AMD option will not link the expected driver.

## Test signals

Build with `CONFIG_NTB_AMD=m` or `y` and confirm `ntb_hw_amd` is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.c

## Purpose

This file implements the AMD PCIe Non-Transparent Bridge hardware driver. It binds to supported AMD/Hygon PCI devices, maps NTB MMIO registers, exposes NTB hardware operations to the generic NTB core, manages memory windows, scratchpads, doorbells, link events, MSI/MSI-X/INTx interrupts, heartbeat polling, side-info readiness state, debugfs diagnostics, and PCI lifecycle.

## Important APIs, types, and functions

The driver state is `struct amd_ntb_dev` from `ntb_hw_amd.h`. Hardware ops are provided through `amd_ntb_ops`, including memory-window count/alignment/translation, peer memory-window address, link status/enable/disable, doorbell masks/read/clear/peer-set, scratchpad read/write, and peer scratchpad read/write.

Memory-window functions include `ndev_mw_to_bar()`, `amd_ntb_mw_count()`, `amd_ntb_mw_get_align()`, `amd_ntb_mw_set_trans()`, `amd_ntb_peer_mw_count()`, and `amd_ntb_peer_mw_get_addr()`. Link functions include `amd_ntb_get_link_status()`, `amd_poll_link()`, `amd_link_is_up()`, `amd_ntb_link_is_up()`, `amd_ntb_link_enable()`, and `amd_ntb_link_disable()`.

Interrupt and event handling is split across `ndev_init_isr()`, `ndev_deinit_isr()`, `ndev_interrupt()`, `ndev_vec_isr()`, `ndev_irq_isr()`, `amd_handle_event()`, and `amd_handle_db_event()`. Side-info and heartbeat helpers are `amd_set_side_info_reg()`, `amd_clear_side_info_reg()`, `amd_init_side_info()`, `amd_deinit_side_info()`, and `amd_link_hb()`.

PCI lifecycle is handled by `amd_ntb_pci_probe()`, `amd_ntb_pci_remove()`, `amd_ntb_pci_shutdown()`, `amd_ntb_init_pci()`, `amd_ntb_deinit_pci()`, `amd_init_dev()`, and `amd_deinit_dev()`. Module init creates a top debugfs directory and registers the PCI driver.

## Control flow and state behavior

Probe allocates `amd_ntb_dev`, attaches PCI driver data, initializes the embedded `ntb_dev` with topology `NTB_TOPO_NONE` and AMD ops, enables the PCI device, requests regions, enables bus mastering, configures a 64-bit or fallback 32-bit DMA mask, maps BAR0 as `self_mmio`, derives `peer_mmio` by adding `AMD_PEER_OFFSET`, determines primary/secondary topology from the side-info register, initializes NTB capabilities, initializes interrupts, reserves the highest doorbell bit as a peer-unload notification bit, enables link-up/down event interrupts, sets local side ready, polls link, creates debugfs, and registers the NTB device with the core.

The driver supports only primary/secondary topology, not B2B. In those modes it splits the 16 scratchpads into local and peer halves by offset and starts delayed heartbeat polling. Link-up is considered true only when peer side-info readiness is observed, with extra primary-side interpretation of link-up/link-down events and peer status bits. Link-down handling can clear peer ready state and reschedule heartbeat polling until the peer returns.

Memory-window translation writes peer-side XLAT and limit registers, verifies that hardware accepted both values, and rolls back on failure. BAR1 uses 32-bit limit writes, while BAR23/BAR45 paths use 64-bit helpers. Peer memory-window address simply exposes local PCI BAR resources to clients.

Doorbell state is represented by a valid mask and a mask register guarded by `db_mask_lock`. Interrupt setup prefers MSI-X with 24 vectors and a minimum of 16, falls back to MSI, then INTx. Doorbell vectors below `AMD_DB_CNT` dispatch `ntb_db_event()`, and event vectors or single-vector mode dispatch link/power events. The highest reserved doorbell bit signals peer driver unload and triggers link-event notification plus heartbeat rescheduling.

Remove and shutdown clear local ready state, notify the peer via the reserved doorbell, unregister the NTB device, remove debugfs, cancel heartbeat work, tear down interrupts, unmap PCI resources, and free memory.

## Dependencies and integration points

This driver depends on the NTB core, PCI/MSI/MSI-X APIs, MMIO accessors, debugfs, delayed work, DMA mask setup, and AMD-specific register layout from `ntb_hw_amd.h`. It registers PCI IDs for multiple AMD and Hygon devices and exposes itself to NTB clients through `ntb_register_device()`.

## Risks and edge cases

Several index checks use `idx > count` rather than `idx >= count`, which should be reviewed against expected callers because `idx == count` can map past the last valid memory window or vector. `amd_ntb_link_disable()` logs "Enabling Link" despite disabling interrupts, which is confusing for diagnostics. Event handling switches on exact status values, so combined event bits may fall to the default path instead of handling each bit. Link status reads sometimes return success-like zero when PCI capability reads fail, potentially hiding errors. Register writes are verified for memory-window setup, but rollback paths write a mix of self/peer registers and should be tested carefully on hardware. Callbacks into NTB core may occur from IRQ context.

## Test signals

Useful tests include PCI probe/remove/shutdown on each supported device data variant, MSI-X full vector setup and fallback to MSI/INTx, memory-window translation for BAR1/BAR23/BAR45 including rollback on verification failure, scratchpad partitioning for primary and secondary topologies, doorbell mask set/clear and peer doorbell signaling, reserved unload doorbell behavior, link up/down events, peer D-state events, heartbeat recovery after peer reload, debugfs `info` reads, and NTB client bind/unbind through the core. Hardware tests should confirm side-info readiness behavior across surprise link removal and driver reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.h -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.h

## Purpose

This header defines AMD NTB register offsets, bit masks, constants, data structures, and helpers used by `ntb_hw_amd.c`. It captures the hardware contract for AMD NTB capability registers, side-info state, memory-window translation/limit registers, doorbells, events, SMU status, scratchpads, and link status fields.

## Important APIs, types, and functions

Important constants include `AMD_DB_CNT`, `AMD_MSIX_VECTOR_CNT`, `AMD_SPADS_CNT`, `AMD_CNTL_OFFSET`, `AMD_SIDEINFO_OFFSET`, memory-window limit and XLAT offsets, doorbell offsets, event masks, SMU offsets, and `AMD_PEER_OFFSET`. Link extraction macros are `NTB_LNK_STA_SPEED()` and `NTB_LNK_STA_WIDTH()`.

The header defines fallback `read64`/`write64` implementations using paired 32-bit MMIO operations when architecture `readq`/`writeq` are unavailable. `struct ntb_dev_data` describes per-device memory-window count, base BAR index, and endpoint flag. `struct amd_ntb_vec` links interrupt vectors to the driver state. `struct amd_ntb_dev` embeds `struct ntb_dev` and stores topology/status, capability counts, masks, MSI-X state, MMIO bases, scratchpad offsets, heartbeat work, and debugfs dentries.

The macros `ntb_ndev()` and `hb_ndev()` convert NTB/work pointers back to `amd_ntb_dev`. Forward declarations expose side-info and link-poll helpers across the C file.

## Control flow and state behavior

The header has no runtime flow but defines how runtime state is laid out and how register state is interpreted. The split of self and peer MMIO, local and peer scratchpads, and reserved event/doorbell masks is foundational for the C file's lifecycle and interrupt behavior.

## Dependencies and integration points

It depends on `linux/ntb.h` and `linux/pci.h`. The file is private to the AMD NTB hardware driver and should remain synchronized with AMD silicon register definitions and any new PCI ID capability data.

## Risks and edge cases

Fallback 64-bit MMIO writes are not atomic because they are implemented as two 32-bit writes; callers should only use them where hardware tolerates that sequence. Register offsets and bit definitions are hard-coded, so platform variants with different layout require new capability data or code changes. `struct ntb_dev_data` uses small integer types, so counts and BAR shifts must remain within expected bounds.

## Test signals

Compile tests on architectures with and without native `readq/writeq` validate fallback paths. Runtime tests through `ntb_hw_amd.c` should verify register offsets, event masks, scratchpad counts, BAR mapping, and link speed/width extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/amd/ntb_hw_amd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Kconfig

## Purpose

This Kconfig file defines the generic EPF-backed NTB host driver option.

## Important APIs, types, and functions

The single symbol is `NTB_EPF`, a tristate option named "Generic EPF Non-Transparent Bridge support". Its help text describes support for configurable endpoint-based NTB.

## Control flow and state behavior

There is no runtime behavior; the symbol controls whether the EPF NTB hardware driver builds.

## Dependencies and integration points

It is sourced by `drivers/ntb/hw/Kconfig` and matched by `drivers/ntb/hw/epf/Makefile`.

## Risks and edge cases

The Kconfig option has no explicit PCI dependency in this file, although the driver itself is PCI-based and parent NTB normally depends on PCI. If reused outside the parent menu, dependencies would need tightening.

## Test signals

Build configuration should verify `CONFIG_NTB_EPF=m/y` compiles the EPF driver when NTB is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Makefile

## Purpose

This Makefile builds the EPF NTB host driver object when selected.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB_EPF) += ntb_hw_epf.o` maps the EPF Kconfig symbol to the driver object.

## Control flow and state behavior

There is no runtime behavior.

## Dependencies and integration points

It pairs with `epf/Kconfig` and `ntb_hw_epf.c`.

## Risks and edge cases

Any source rename or multi-object split must update this file to keep the selected Kconfig symbol linked correctly.

## Test signals

Build with `CONFIG_NTB_EPF=m` or `y` and verify `ntb_hw_epf` is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/ntb_hw_epf.c -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/ntb_hw_epf.c

## Purpose

This file implements a host-side PCI driver that exposes a configurable endpoint-function NTB device through the generic NTB core. It maps endpoint-defined control, doorbell, peer scratchpad, and memory-window BARs; sends control commands to endpoint firmware/function logic; configures interrupts; and implements NTB ops for link control, memory windows, scratchpads, and doorbells.

## Important APIs, types, and functions

`struct ntb_epf_dev` embeds `struct ntb_dev` and stores a device pointer, command mutex, BAR mapping table, memory-window/scratchpad/doorbell counts, mapped control/doorbell/peer-spad regions, scratchpad offsets, a last doorbell value, and the valid doorbell mask.

Command protocol constants define control-register offsets (`NTB_EPF_COMMAND`, `NTB_EPF_ARGUMENT`, `NTB_EPF_CMD_STATUS`, address/size registers, count registers, doorbell data/offset registers) and commands (`CMD_CONFIGURE_DOORBELL`, `CMD_TEARDOWN_DOORBELL`, `CMD_CONFIGURE_MW`, `CMD_TEARDOWN_MW`, `CMD_LINK_UP`, `CMD_LINK_DOWN`). `ntb_epf_send_command()` serializes command submission and polls status up to one second.

The NTB ops table `ntb_epf_ops` includes memory-window count/alignment/set/clear, peer memory-window count/address, link enable/disable/is-up, scratchpad and peer scratchpad read/write, doorbell valid mask, peer doorbell set, doorbell read/clear, and no-op mask operations. PCI lifecycle functions are `ntb_epf_pci_probe()` and `ntb_epf_pci_remove()`.

## Control flow and state behavior

Probe rejects PCI bridges, allocates the device state with devm, obtains the per-device BAR map from PCI ID driver data, initializes the embedded NTB device, initializes the command mutex, enables the PCI device, requests regions, enables bus mastering, sets a 64-bit or fallback 32-bit DMA mask, maps the control BAR, maps or derives peer scratchpad space, maps the doorbell BAR, allocates MSI-X or MSI vectors, requests IRQs, sends a configure-doorbell command to the endpoint, reads memory-window and scratchpad counts from the control region, validates memory-window count, and registers the NTB device.

The endpoint command path writes an argument, writes a command, polls `NTB_EPF_CMD_STATUS` for OK or ERROR, times out after one second, clears status, and releases the mutex. Link enable and disable are command wrappers. Memory-window setup writes lower/upper address and size registers and sends `CMD_CONFIGURE_MW`; clear sends `CMD_TEARDOWN_MW`.

IRQ vector 0 is treated as link event, while other vectors are doorbells. The ISR computes the vector index from `irq - pci_irq_vector(pdev, 0)`, stores `db_val = irq_no + 1`, and dispatches `ntb_link_event()` or `ntb_db_event()`. Doorbell peer signaling reads endpoint-provided doorbell entry size/data/offset from control registers and writes the data into the mapped doorbell region.

Three BAR maps are provided for TI J721E, NXP/Freescale i.MX8, and Renesas R-Car PCI IDs. These maps determine where config, peer scratchpad, doorbell, and memory windows live.

## Dependencies and integration points

The driver depends on PCI, MSI/MSI-X allocation, MMIO accessors, DMA mask setup, the NTB core, and endpoint-side firmware/function behavior that implements the command/status register protocol. It registers PCI IDs for TI J721E, Freescale `0x0809`, and Renesas `0x0030` RAM-class endpoint devices.

## Risks and edge cases

`ntb_epf_mw_to_bar()` uses `idx > ndev->mw_count`, so `idx == mw_count` can access beyond valid memory-window entries. Some BAR maps contain `NO_BAR`; callers must not request absent memory windows, and validation should ensure endpoint-reported `mw_count` matches the map. `ntb_epf_mw_set_trans()` ignores the return value from `ntb_epf_send_command()` and always returns 0 after issuing the command. `ntb_epf_mw_clear_trans()` initializes `ret = 0` and also ignores the command return, so teardown failures are hidden. `ntb_epf_peer_db_set()` computes `interrupt_num = ffs(db_bits) + 1`; `db_bits == 0` or multi-bit values are not explicitly rejected, and `ffs()` is one-based, so off-by-one behavior should be checked. `ntb_epf_deinit_pci()` unconditionally iounmaps `peer_spad_reg`, even when it aliases inside `ctrl_reg`, which may be unsafe depending on `pci_iounmap()` expectations for derived addresses.

## Test signals

Validation should include probe/remove on each BAR map, MSI-X and MSI fallback, endpoint command OK/ERROR/timeout behavior, link vector and doorbell vector interrupts, memory-window setup/teardown including endpoint errors, peer doorbell writes, scratchpad and peer scratchpad access, invalid peer/index handling, absent BAR handling, and NTB client bind/unbind. Endpoint integration tests should assert command status clearing and correct BAR layout for each platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/epf/ntb_hw_epf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Kconfig

## Purpose

This Kconfig file defines the IDT PCIe-switch NTB hardware driver option and documents required platform pre-initialization.

## Important APIs, types, and functions

The main symbol is `NTB_IDT`, a tristate option named "IDT PCIe-switch Non-Transparent Bridge support". It depends on `PCI` and selects `HWMON`.

## Control flow and state behavior

There is no runtime behavior. The help text describes that partitions, NT-function ports, and NT-function BAR apertures must be configured before Linux PCI enumeration, typically via EEPROM or BIOS/SMBus, because some driver behavior depends on peer BAR settings.

## Dependencies and integration points

It is sourced by `drivers/ntb/hw/Kconfig` and matched by `drivers/ntb/hw/idt/Makefile`. Selecting it implies hardware monitoring support through `HWMON`.

## Risks and edge cases

The driver depends on platform pre-initialization that cannot be done reliably through kernel PCI fixups. Systems without correct EEPROM/BIOS setup may expose incomplete or incorrect NT functions, leading to probe failures or unsafe BAR assumptions.

## Test signals

Configuration tests should verify the PCI dependency, `HWMON` selection, and build of the IDT driver. Platform tests should include correctly and incorrectly pre-initialized switches to validate failure diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Makefile

## Purpose

This Makefile builds the IDT NTB hardware driver object when selected.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB_IDT) += ntb_hw_idt.o` maps the IDT Kconfig symbol to its driver object.

## Control flow and state behavior

There is no runtime behavior.

## Dependencies and integration points

It pairs with `idt/Kconfig` and the IDT hardware driver source, which is outside this specific work-item list.

## Risks and edge cases

The Makefile assumes the selected object exists in the same directory and that `CONFIG_NTB_IDT` dependencies are complete in Kconfig.

## Test signals

Build with `CONFIG_NTB_IDT=m` or `y` and verify `ntb_hw_idt` is produced and linked with any required HWMON dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Makefile -->

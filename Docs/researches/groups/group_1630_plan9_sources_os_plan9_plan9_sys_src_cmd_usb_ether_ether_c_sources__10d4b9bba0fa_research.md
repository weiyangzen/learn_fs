# Group Research: group_1630_plan9_sources_os_plan9_plan9_sys_src_cmd_usb_ether_ether_c_sources__10d4b9bba0fa

Scope: `Docs/research_subset_a.md` / source tree `sources/os/plan9/plan9`.  
Read status: every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.c

Implements the generic USB Ethernet adapter runtime and per-device file tree. It registers `etherU%d` subtrees with the USB 9P directory framework and exposes Plan 9 ether-style files including `clone`, `addr`, `stats`, `ifstats`, per-connection `data`, `ctl`, `type`, and stats files.

Key structures and behavior:
- Maintains a static VID/DID `cinfo[]` table for ASIX and SMSC controllers, with CDC Ethernet used as fallback through the `ethers[]` reset chain.
- Uses `Ether`, `Conn`, and `Buf` abstractions from `ether.h` to multiplex packets to multiple user connections.
- `newconn`, `fsopen`, `fsread`, `fswrite`, and `fsclunk` implement connection lifecycle and file operations.
- `etherctl` supports `connect`, `nonblocking`, `promiscuous`, `headersonly`, `addmulti`, and `remmulti`, then delegates unknown controls to controller-specific `ctl`.
- Read/write worker processes move buffers between USB bulk endpoints and connection queues.
- `etherinit` discovers CDC-style endpoints, including CDC union descriptor handling; `openeps` opens bulk endpoints.
- `kernelproxy` tries to bind the USB Ethernet device through `#l0/ether0/clone`; if that succeeds, no user-space `etherU%d` tree is needed.

Important interactions:
- Depends on `usb/lib` for `Dev`, endpoint opening, control requests, and `Usbfs`.
- Controller-specific reset functions may install custom `bread`, `bwrite`, `promiscuous`, `multicast`, and stats hooks.
- On fatal read errors it detaches the kernel USB endpoint, tears down the file tree with `usbfsdel`, and closes references.

Notable risks/quirks:
- Comments call out that this should ideally use `/dev/etherfile`.
- Multicast/loopback behavior is incomplete; loopback currently keys mainly off promiscuous state.
- Always defaults to configuration/interface choices found by scanning descriptors, with limited policy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.h

Shared declarations for the USB Ethernet driver family.

Defines:
- Controller IDs: CDC, ASIX variants, and SMSC LAN95xx.
- Ethernet constants such as address length, packet length, header size, max packet size, connection count, and buffer count.
- USB CDC Ethernet descriptor constants.
- `Buf`, the receive/transmit buffer with header slack and payload pointer.
- `Conn`, the per-open ether connection, including packet type filtering, header-only mode, promiscuous flag, and receive channel.
- `Etherops`, the controller-specific operations table.
- `Ether`, the main device state containing USB endpoints, MAC address, counters, queues, operation hooks, and embedded `Usbfs`.
- `Cinfo`, the VID/DID/controller mapping record.
- `Etherpkt`, a minimal Ethernet frame header layout.

Exports:
- `ethermain`, controller reset hooks, `parseaddr`, and `dumpframe`.
- Global `cinfo[]` and `etherdebug`.
- `deprint` debug macro.

This header is the contract between the generic Ethernet file server and hardware-specific backends such as SMSC and ASIX.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/main.c

Command entry point for `usb/ether`.

Behavior:
- Parses top-level options: `-a` MAC override, `-D` USB filesystem debug, `-d` USB debug, `-N` device number override, `-m` mountpoint, and `-s` service name.
- Builds an argument string passed into each device worker.
- Matches candidate devices via `matchether`, accepting communication-class devices or devices listed in `cinfo[]`.
- Initializes the USB file directory service at `/net` by default using `usbfsinit`.
- Calls `startdevs` to open/configure matching USB devices and run `ethermain`.

This file is thin orchestration; actual packet/file handling is in `ether.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/smsc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/smsc.c

SMSC LAN95xx backend for the generic USB Ethernet layer.

Main responsibilities:
- Defines LAN95xx USB vendor requests, device registers, MII registers, EEPROM bits, and transmit/receive header flags.
- `wr` and `rr` issue USB vendor register writes/reads.
- `miird`/`miiwr` access PHY registers through MAC MII registers.
- `eepromr` reads EEPROM bytes, and `getmac` obtains the MAC address.
- `smscinit` performs hardware reset, EEPROM MAC load, burst configuration, LED setup, VLAN/default AFC setup, checksum offload disable, PHY initialization, interrupt setup, and TX/RX enable.
- `smscbread` unpacks LAN95xx receive aggregation headers and extracts Ethernet frames.
- `smscbwrite` prepends the two LAN95xx transmit command words before writing to the bulk-out endpoint.
- `smscreset` matches `cinfo[]` entries, initializes hardware, allocates burst buffer state, installs `Etherops`, and sets a nominal 100 Mbps speed.

Notable gaps:
- Promiscuous and multicast methods are stubs returning `-1` under disabled TODO blocks.
- Link speed is hardcoded to 100 Mbps.
- Receive burst constants are conservative (`Hsburst = 8`) with a comment noting the Linux value differs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/smsc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.c

Minimal HID report descriptor/parser support used by USB pointer handling.

Core logic:
- `get8bits` and `getbits` extract unaligned bitfields from a `Chain`.
- `parsereportdesc` walks a HID report descriptor and builds a compact `HidRepTempl` focused on pointer reports: buttons, X, Y, Z/padding, and wheel fields.
- Tracks report ID, report size/count, usage page, usages, input blocks, and collections.
- Requires a pointer application with X/Y and buttons; otherwise reports descriptor rejection.
- `parsereport` decodes one input report into per-interface values and sign-extends X/Y/wheel fields.
- `hidifcval` returns the nth decoded value of a requested kind.
- `dumpreport` prints decoded template/value state for debugging.

Scope is intentionally narrow: it is not a full HID parser, but enough for common mouse report descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.h

Shared USB HID keyboard/mouse definitions.

Defines:
- HID boot keyboard and pointer CSP constants.
- HID class requests: get protocol, set idle, set protocol.
- Boot/report protocol constants.
- Keyboard modifier bit indexes and masks.
- Plan 9 scan-code constants used by `kb.c`.
- Pointer acceleration and button mask constants.
- `Chain`, a bitstream buffer for HID report parsing.
- `HidInterface` and `HidRepTempl`, the simplified report template used by `hid.c`.
- HID item constants used by the minimal parser.

Exports:
- `kbmain`.
- HID report dump/parse helpers.

This header connects `main.c`, `kb.c`, and `hid.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/kb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/kb.c

USB HID keyboard and mouse driver.

Major responsibilities:
- Opens interrupt-in endpoints for boot keyboards and boot/report-protocol pointers.
- Writes keyboard scan codes to `#I/kbin` and mouse events to `#m/mousein`, with shared `Kin` reference management.
- Maps HID keyboard keycodes through `sctab[]` into Plan 9 scan codes.
- Handles keyboard modifier diffs, key down/up synthesis, and key repeat via a separate repeat process.
- Handles pointer reports in either boot protocol (`ptrbootpvals`) or parsed HID report form (`ptrrepvals`).
- Applies optional pointer acceleration and formats mouse events as `m%11d %11d %11d`.
- Configures HID devices using first configuration/report descriptor when possible, falling back to boot protocol.
- Includes recovery logic for babble/read errors by asking the USB endpoint/device to reset and reopening data.

Important paths:
- `kbmain` decides whether keyboard and/or pointer endpoints are enabled, allocates `KDev`, and starts `kbdwork` or `ptrwork`.
- `kbstart` opens the endpoint, sets idle/report/boot protocol, opens data, and creates the worker.
- `kbfatal` detaches and closes the USB device on terminal errors.

Quirks:
- Report descriptor parsing is only pointer-oriented.
- Some debug scan codes mutate driver debug level.
- Comments note incomplete recovery semantics for bundled devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/kb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/main.c

Command entry point for USB keyboard/mouse support.

Behavior:
- Parses `-a` acceleration, `-d` USB debug, `-k` keyboard-only, `-m` mouse-only, `-N` ignored device number, and `-b` force boot protocol.
- Builds a worker argument string and chooses CSP matches for boot keyboard and pointer devices.
- If keyboard-only is requested, removes pointer CSP from the search list.
- Installs USB device formatter and calls `startdevs` with `matchdevcsp` and `kbmain`.

The file contains no event handling; it discovers devices and dispatches them to `kb.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/kb/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dev.c

Core USB device and endpoint helper implementation.

Main functions:
- `opendev` opens an endpoint directory’s `ctl` file and builds a `Dev`.
- `opendevdata` opens the endpoint `data` file.
- `openep` creates or opens an endpoint under `/dev/usb/ep<dev>.<id>`, sets max packet, transaction count, and polling interval.
- `loaddevdesc`, `loaddevconf`, and `configdev` retrieve and parse descriptors into `Usbdev`.
- `loaddevstr` decodes USB UTF-16LE string descriptors.
- `closedev` reference-counts and frees `Dev`, descriptor tree, strings, endpoints, configs, and driver aux state.
- `usbcmd` builds control transfer packets, retries failed commands, and handles request/response phases.
- `unstall` clears endpoint halt both at USB standard request level and kernel endpoint `ctl`.
- `devctl` writes a single formatted control command.

Important design:
- `Dev` has one existence reference plus per-I/O or per-driver references.
- Descriptor parsing is delegated to `parse.c`.
- Control transfer debugging uses `hexstr` and request formatting.

Risks/quirks:
- Some endpoint naming behavior is retained for backward compatibility.
- `usbcmd` only treats positive counts as success, so zero-length replies are special-cased by callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/devs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/devs.c

Device discovery and per-device worker launcher for standalone USB drivers.

Key functions:
- `matchdevcsp` matches text from `/dev/usb/*/ctl` against requested CSP values.
- `finddevs` scans `/dev/usb`, reads endpoint zero control files, and returns enabled idle devices matching a predicate.
- `startdevs` binds `#u` if needed, opens/configures explicit or discovered devices, then starts a `workproc` for each successful device.
- `workproc` tokenizes driver arguments and invokes the supplied device main function.

Behavior:
- Supports both explicit device path arguments and automatic discovery.
- Uses a channel to wait for worker startup success/failure.
- Closes devices on failed driver initialization.

This is the common launcher used by `usb/ether`, `usb/kb`, `usb/serial`, and `usb/print`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/devs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dump.c

Debug formatting and allocation helpers for the USB library.

Provides:
- `classname` mapping USB class IDs to readable names.
- `hexstr` heap-allocating byte dump string.
- `seprintiface` and `seprintconf` helpers for structured descriptor output.
- `Ufmt`, the `%U` formatter for `Dev*`, printing device path, class/subclass/proto, VID/DID, refs, strings, configurations, interfaces, endpoints, and device-specific descriptors.
- `estrdup` and `emallocz`, fatal-on-failure allocation wrappers with malloc tags.

Also defines global `usbdebug`.

This file is used heavily by discovery, driver startup, and diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fs.c

Generic 9P server framework for USB driver file trees.

Core elements:
- Defines `Rpc` state containing incoming/outgoing `Fcall`, fid pointer, flush state, and data buffer.
- Manages fid and RPC freelists under `rpclck`.
- Implements 9P operations: version, attach, walk, open, read, write, clunk, stat, flush, and permission-denied stubs.
- Dispatches blocking open/read/write work to a small cached process pool managed by `schedproc`.
- `usbdirread` serializes generated directory entries.
- `usbreadbuf` serves static buffers with offset/count semantics.
- `usbfsinit` creates a pipe-backed 9P server, optionally posts it in `#s`, and optionally mounts it.

Important behavior:
- Only one user is allowed after first attach unless username matches.
- Flush marks an RPC as flushed but does not abort underlying I/O.
- On 9P read failure it calls `fsops->end` or closes the underlying device.

This is the foundation used by `usbdirfs`, Ethernet, serial, and `usbdctl` file trees.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fsdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fsdir.c

Multiplexing root directory for multiple USB driver file systems.

Main behavior:
- Maintains a dynamically resized array of registered `Usbfs*`.
- `usbfsadd` assigns a high-32-bit qid namespace and registers a subtree.
- `usbfsdel` and `usbfsgone` unregister subtrees, call end hooks, close devices, and optionally exit when all are gone.
- `usbfsdirdump` prints registered filesystem state.
- Root `fswalk`, `fsopen`, `fsread`, `fswrite`, `fsclunk`, and `fsstat` dispatch operations to the correct registered filesystem based on qid high bits.
- `usbdirfs` is the exported root `Usbfs` used by USB drivers and `usbd`.

Design:
- qid high 32 bits identify the registered device/subtree; low bits are private to that subtree.
- Operations take temporary references on underlying `Dev` objects while dispatching.
- Entry 0 is reserved for the top-level root.

This file lets independent USB drivers appear under one mounted `/dev` or `/net` directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fsdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/parse.c

USB descriptor parser.

Main functions:
- `parsedev` validates and unpacks the standard device descriptor into `Usbdev`.
- `parseiface` creates/fills `Iface` and alternate setting state.
- `parseendpt` creates/fills `Ep`, handles direction, type, isochronous attributes, max packet, high-speed transactions, and interface endpoint lists.
- `parsedesc` walks mixed descriptors following a configuration descriptor, dispatching standard interface/endpoint descriptors and storing unknown/device-specific descriptors with context.
- `parseconf` validates and unpacks the standard configuration descriptor, then parses the remaining descriptor stream.

Important details:
- If a device-level CSP is zero, the first interface CSP becomes the device CSP.
- Device-specific descriptors preserve links to current config/interface/endpoint/alt setting for drivers such as CDC Ethernet and hubs.
- Handles endpoint ID sharing for IN/OUT by marking direction `Eboth`.

This parser populates the descriptor model consumed by all drivers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usb.h

Primary USB userspace library header.

Defines:
- USB constants: endpoint/config/interface limits, request type bits, standard requests, class IDs, descriptor types/sizes, feature selectors, device states, endpoint directions/types, config attributes, and HID report item constants.
- Core structs: `Dev`, `Usbdev`, `Ep`, `Altc`, `Iface`, `Conf`, raw descriptor wrappers, and standard descriptor layouts.
- CSP helper macros, little-endian GET/PUT macros, debug macros, and `%U` formatter declaration.
- USB library API for device opening, descriptor loading/parsing, control requests, endpoint opening, device discovery, driver startup, and utility allocation.

This is the shared ABI for all Plan 9 USB command drivers in this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usbfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usbfs.h

Header for the USB 9P file server framework.

Defines:
- Message/buffer sizing constants.
- `Fid` state with fid number, qid, open mode, next pointer, and aux field.
- `Usbfs` operation table for walk, clone, clunk, open, read, write, stat, and end.
- `Dirgen` callback type.
- Utility functions for reading static buffers, adding/removing file systems, directory reads, and starting the USB file server.
- Shared error strings and exported `usbdirfs`.

This is the contract implemented by `fs.c` and `fsdir.c` and consumed by USB drivers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usbfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/print/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/print/main.c

Command entry point for USB printer support.

Behavior:
- Matches printer-class devices with CSP `0x020107`.
- Parses `-d` USB debug and `-N` device number override.
- Builds worker arguments and invokes `startdevs` with `printmain`.
- Installs `%U` formatting and starts each matching device.

Actual endpoint setup is in `print.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/print/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/print/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/print/print.c

USB printer endpoint binder.

Main behavior:
- `findendpoints` scans parsed USB endpoints for a printer interface CSP and bulk OUT endpoint.
- Opens the bulk OUT endpoint, opens its data file for writing, optionally enables debug, and names it `lp%d`.
- `printmain` parses `-N`, then calls `findendpoints`.

Despite enum qid constants, this file does not implement its own file server; it configures the kernel USB endpoint as a printer-like output device.

Known limitation:
- Header comment notes it assumes the printer remains connected and is not hot-plugged.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/print/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/probe -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/probe

Small rc script to list USB devices from `/dev/usb/ctl`.

Behavior:
- Binds `#u` to `/dev` if `/dev/usb` does not exist.
- Optional `-h` filters out root hubs and hubs.
- Uses `awk` to pair enabled endpoint-zero lines with the following descriptive line from `/dev/usb/ctl`.
- Prints device endpoint plus information and exits successfully.

This is a diagnostic helper, not a C driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/probe -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.c

FTDI backend for the generic USB serial driver.

Major components:
- Large `ftinfo[]` VID/DID table for FTDI and FTDI-based products.
- `ftdiread`/`ftdiwrite` wrap FTDI vendor/class control requests.
- Baud divisor calculation supports SIO, AM, BM, 2232/4232-style devices, plus special divisor quirks.
- `ftgettype` infers chip family, interface count, packet size, baud base, input/output header sizes, and optional JTAG interface.
- `ftsetparam`, `ftmodemctl`, `ftsendlines`, and `ftsetbreak` implement serial line configuration.
- `ftuseinhdr` consumes FTDI input status headers and updates modem/error counters.
- `wait4data` and `wait4write` integrate FTDI packet headers with the common serial read/write layer.
- Background `epreader` reads endpoint data, strips FTDI status headers with `cpdata`, and sends buffered packets to `statusreader`.
- `statusreader` coordinates common-layer blocking reads through `w4data`/`gotdata`.
- `ftinit` starts status reading and, for JTAG, configures latency, timeouts, and MPSSE bit mode.
- `ftreset` and `ftclearpipes` issue FTDI reset/purge commands.

Notable quirks:
- FTDI input packets carry two status bytes per USB packet and optional output headers for old SIO devices.
- Multi-interface devices can expose a JTAG interface named separately by the common layer.
- The `ftdiwrite` request test uses `||`, making the index adjustment effectively always applied.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.h

FTDI constants and declarations.

Contents:
- Extensive VID/DID constants for FTDI and FTDI-based devices.
- FTDI command request constants for reset, modem control, flow control, baud rate, data parameters, status, latency timer, bit mode, EEPROM access, and pins.
- Port/interface constants and request type bit.
- Chip type constants: SIO, FT8U232AM, FT232BM, FT2232C, FTKINDR, FT2232H, FT4232H.
- Legacy SIO baud selector constants.
- Data/parity/stop/break bit encodings.
- Flow-control encodings.
- Bitbang/MPSSE mode constants.
- FTDI input status header bit definitions and output header fields.
- Exports `ftops` and `ftmatch`.

This header is mostly device database and protocol definitions consumed by `ftdi.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/main.c

Command entry point for USB serial devices.

Behavior:
- Matches devices through `uconsmatch`, `plmatch`, `ftmatch`, or `slmatch`.
- Parses `-D` USB filesystem debug, `-d` USB debug, `-N` device number, `-m` mountpoint, and `-s` service name.
- Initializes USB directory file server mounted at `/dev` by default.
- Calls `startdevs` to run `serialmain` for matching devices.

It only handles discovery and setup; common serial file implementation is in `serial.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.c

Prolific PL2303-compatible backend for the generic USB serial driver.

Main behavior:
- Provides `plinfo[]` device table and `plmatch`.
- Implements vendor read/write helpers.
- `plinit` determines chip type from release ID or heuristics, performs the Prolific vendor initialization sequence, sets DCR registers, reads line parameters, and starts interrupt status reader.
- `plgetparam` and `plsetparam` map Plan 9 serial parameters to PL2303 line coding bytes.
- `plmodemctl`, `plsendlines`, and `setctlline` manage modem/flow control lines.
- `plsetbreak` sends break control request.
- `plclearpipes` uses vendor pipe reset for HX devices or standard endpoint unstall for others.
- `plreadstatus` reads interrupt endpoint status and updates DCD/DSR/CTS/ring/error counters.
- `statusreader` loops on interrupt status until failure.
- `plseteps` sets bulk endpoint max packet sizes to 256.

Notes:
- The code includes comments comparing behavior to Linux PL2303 handling.
- Some status field assignment looks rough, for example break-error and CTS bits share nearby handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.h

Prolific PL2303 protocol and device constants.

Defines:
- Device flavor/revision constants.
- PL2303 class/vendor request IDs and line coding sizes.
- Interrupt status bit definitions.
- Device control register indices/values and pipe reset commands.
- VID/DID constants for Prolific and many rebadged USB serial cables.
- Exports `plops` and `plmatch`.

This header supplies the lookup table constants and request encodings used by `prolific.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.c

Generic USB serial file server and common serial control layer.

Main responsibilities:
- Exposes each serial interface as a `Usbfs` subtree with data and control files, usually `eiaU*` and `eiaU*ctl`, plus JTAG naming for JTAG interfaces.
- Parses control commands in `serialctl`: baud, line bits, parity, stop bits, RTS/DTR/modem, break, flush, software flow characters, and other Plan 9 serial controls.
- Provides `serdumpst` status formatting for control reads.
- Opens bulk IN/OUT and optional interrupt endpoints with timeouts and chip-specific endpoint setup.
- `dread` serves directory reads, data reads, and control status reads.
- `dwrite` writes serial data or applies control commands.
- `altwrite` handles data writes with timeout retry and recovery.
- `serialrecover` un-stalls endpoints, resets devices, or detaches after repeated failures.
- `serialreset` drains ports and invokes chip reset hooks.
- `serialmain` detects chip backend, initializes interfaces, starts per-interface file systems, and registers them under `usbdirfs`.

Backend integration:
- Uses `Serialops` installed from Prolific, ucons, FTDI, or Silabs.
- Supports chip-specific `wait4data`, `wait4write`, `setparam`, `sendlines`, `setbreak`, and recovery hooks.

Risks/quirks:
- Some error-run counters are static in `dread`, not per port.
- Long continuous read errors can terminate all serial service.
- Comments note software flow control is not fully implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.h

Shared declarations for USB serial drivers.

Defines:
- `Serialops`, the chip-specific operation table.
- `Serialport`, per-interface state including endpoints, embedded `Usbfs`, line settings, modem/error counters, channels, and data buffering.
- `Serial`, whole-device state including `Dev`, chip type, recovery state, operation table, interface count, packet sizes, FTDI header sizes, and baud base.
- Common control constants such as software flow characters and RTS/DTR bits.
- `Cinfo` VID/DID/controller record.
- Exports common entry points and helpers: `serialmain`, `serialrecover`, `serialreset`, `serdumpst`, and global debug/device tables.

This header is the contract between the common serial layer and chip backends.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.c

Silicon Labs CP210x-style backend for the generic USB serial driver.

Main behavior:
- Matches CP210x VID/DID pairs in `slinfo[]`.
- Provides vendor request helpers `slread`, `slwrite`, and `slput`.
- `slinit` enables UART operation and reads initial parameters.
- `slgetparam` reads baud and line control register, decoding bits/parity/stop.
- `slsetparam` writes line control and baud.
- `seteps` disables read timeout on input endpoint.
- `wait4data` repeatedly reads until nonzero data.

Exports `slops` with init/getparam/setparam/seteps/wait4data hooks.

Style note:
- `slmatch` uses legacy K&R implicit-int style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.h

Tiny Silabs serial backend header.

Exports:
- `Serialops slops`
- `slmatch(char *info)`

Used by `serial/main.c` and `serial.c` for CP210x matching and operation dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.c

Backend for Ajays Net20DC USB debug cable / console-like serial device.

Behavior:
- Defines `uconsinfo[]` with Net20DC VID/DID.
- `uconsmatch` matches device info text against that table.
- `ucseteps` marks the port as non-real baud (`~0`), limits max transfers to 8 bytes, and sets endpoint max packet size to 8.
- `uconsops` only supplies `seteps`; all other serial operations are no-ops/defaults.

This is a minimal adapter for a special USB debug cable rather than a full UART chip.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.h

Header for the ucons serial backend.

Defines:
- Net20DC VID/DID constants.
- `uconsmatch`.
- Exported `Serialops uconsops`.

Used by the common serial matching and operation dispatch path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/dev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/dev.c

USB daemon device-driver dispatch support.

Main responsibilities:
- Manages per-driver device-number bitmasks with `getdevnb` and `putdevnb`.
- Matches `Devtab` entries by VID/DID and device/interface CSP, respecting no-auto flags.
- Starts drivers either embedded (`dt->init`) or external executable.
- `startdevproc` builds arguments including `-N`, appends configured args, and executes `/bin/usb/<driver>`, `/boot/<driver>`, or CPU-specific binaries for external drivers.
- Embedded drivers receive an already configured `Dev`; a separate control-only `Dev` is kept by usbd for port tracking.
- `writeinfo` writes human-readable class/CSP/VID/DID/vendor/product info into the kernel endpoint control file.
- `startdev` handles hub special-case creation directly and otherwise finds a matching driver table entry.

Important design:
- Hubs are enumerated inside `usbd` to avoid concurrent default-address enumeration.
- Non-hub drivers may be external processes or embedded functions generated by `mkdev`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/mkdev -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/mkdev

rc/awk generator for `Devtab` entries from `usbdb`.

Behavior:
- Reads class constants from `../lib/usb.h` and builds sed substitutions from class names to numeric constants.
- Emits C includes and extern declarations for embedded driver `*main` functions.
- Parses `embed` and `auto` sections in `usbdb`.
- Emits `Devtab devtab[]` entries with driver name, embedded init or `nil`, CSP/class/subclass/proto match fields, VID/DID, and args.
- Pads CSP arrays to four entries.
- Terminates table with a nil entry.

This script generates machine-maintained USB daemon driver matching code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/mkdev -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.c

USB daemon hub enumeration and control service.

Major responsibilities:
- Creates root/non-root `Hub` objects, configures hub descriptors, powers ports, and maintains global hub list.
- Polls all hub ports periodically; detects attach, detach, suspend/resume, reset requests, and status changes.
- `portattach` performs USB enumeration: enable/reset port, create kernel USB device, set address, get max packet, load descriptors, set configuration, and store `Dev`.
- `startdev` is called after successful port attach to launch the appropriate driver.
- `portdetach` tears down child hubs/devices, releases driver numbering, detaches kernel endpoints, unregisters USB file systems, and closes devices.
- `portresetwanted`/`portreset` implement reset requests signaled through endpoint control files.
- `work` serializes enumeration across hubs to avoid default-address conflicts.
- Exposes `usbdctl` as a small `Usbfs` file with commands for dump, exit, debug level, fsdebug, driver args, auto/noauto.
- Reads environment variables for debug and driver args.
- `threadmain` binds `#u`, starts root hub discovery, starts `usbdirfs`, registers `usbdctl`, and mounts/posts the USB service.

Design notes:
- Root hubs are configured by reading kernel control data rather than a standard descriptor.
- Non-root hub interrupt endpoints are not used; polling is intentional.
- Comments describe reset/event limitations and the lack of a kernel event file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.h

Shared header for `usbd`.

Defines:
- Hub descriptor constants, hub/port feature selectors, port status bits, port states, enumeration delays, polling interval, and driver table CSP match flags.
- `Hub`, containing descriptor-derived hub state, ports, root flag, USB device, and global list link.
- `Port`, containing state, previous status, removable/power flags, attached `Dev`, child hub, assigned device number, and number-mask pointer.
- `DHub`, the USB hub descriptor layout.
- `Devtab`, the driver dispatch table entry with name, optional embedded init function, CSPs, VID/DID, args, device-number mask, and noauto flag.
- Exports `newhub`, `startdev`, device-number helpers, `threadmain`, and `usbdfsops`.

This header ties `usbd.c`, `dev.c`, and generated device tables together.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/va/a.h

Shared header for the Plan 9 MIPS assembler (`va`).

Defines:
- Core assembler data structures: `Sym`, `Io`, `Gen`, and `Hist`.
- Buffer, hash table, include, macro, hunk, and parser constants.
- Global assembler state via `EXTERN`: input buffer, symbol hash, include paths, history, line number, output file, pass number, pc, current token, debug flags, and output `Biobuf`.
- Parser/lexer/codegen function declarations.
- Compatibility function declarations from the compiler compatibility layer.
- OS type constants matching the C compiler.

This is the central state and API header for `a.y` and `lex.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/a.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/va/a.y

Yacc grammar for the MIPS assembler frontend.

Main contents:
- Token and semantic value declarations for instruction classes, registers, constants, labels, names, and addressing modes.
- Grammar for labels, variable assignments, scheduling directives, and instruction statements.
- Instruction forms cover arithmetic/immediate ops, NOR, load/store, MOVW/MOVV/MOVD/MOVF, multiply/divide, jumps, branches, TEXT/GLOBL/DATA, floating-point ops, coprocessor branches, WORD, NOP, BREAK/CACHE overload, and special ops.
- Addressing grammar builds `Gen` operands for registers, immediates, memory references, branch targets, static/external names, HI/LO, FP regs, coprocessor regs, and string/float constants.
- Constant expression grammar supports unary and binary arithmetic/bitwise operators.

Output:
- Semantic actions call `outcode` with assembled opcode and operands.
- Undefined labels become branch operands and are diagnosed on pass 2.
- Some register/operand validation is minimal and defers work to later stages.

This file defines accepted assembly syntax and operand lowering into the assembler’s `Gen` representation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/va/l.s

MIPS kernel low-level assembly support file.

Contents:
- Memory, timing, CP0 register, status bit, trap, segment, PTE, and address-space constants.
- `start` bootstrap for the first processor: sets status/FPU, clears BSS, records argc/argv/env, and calls `main`.
- `touser` transitions to user mode with a supplied stack pointer.
- `newstart` brings secondary processors online.
- Firmware jump helper.
- Interrupt priority functions: `splhi`, `spllo`, `splx`.
- Write-buffer flush, label save/restore, and `gotopc`.
- TLB helpers: put/probe/read entries and indexed TLB writes.
- Exception vector and `exception` handler path for user/kernel traps and syscalls.
- Register save/restore helpers for general registers and floating-point registers.
- `rfnote` restore path.
- Instruction and data cache flush routines.

This is machine/runtime support, not assembler implementation. It is included in this group because it lives under `cmd/va`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/va/lex.c

Assembler driver, lexer initialization, opcode table, and object emission support for `va`.

Main behavior:
- `main` parses assembler options, sets target char/string (`v`/`mips` or little-endian `0`/`spim`), include paths, defines, output file, and parallel assembly for multiple inputs.
- `assemble` derives output filename, configures include paths, creates output, runs two assembler passes, emits history, and finalizes object output.
- `itab[]` maps register names, special names, and instruction mnemonics to parser token types and opcode values.
- `cinit` initializes null operand state, error/input globals, hash table, predefined symbols, and current pathname.
- `syminit`, `isreg`, and `cclean` provide assembler support hooks.
- `zname` emits symbol-name records.
- `zaddr` serializes `Gen` operands into object format.
- `outcode` emits instructions on pass 2, assigns symbol table slots, records line number and scheduling flag, and advances pc on pass 1/2.
- `outhist` emits source path history records.
- Includes shared compiler lexer, macro, and compatibility bodies.

This file bridges parsing to Plan 9 object output for the MIPS assembler.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/va/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/dat.h

Internal data definitions for the Vac filesystem/archive implementation.

Defines:
- `MetaBlock` and `MetaEntry` forward declarations.
- `MaxBlock` limit.
- Tuning constants for estimated directory-entry size, fullness threshold, flush size, and dirty percentage.
- `MetaEntry`, a pointer plus size wrapper for one metadata entry.
- `MetaBlock`, tracking metadata block size, used/free space, index allocation/use, unbotch flag, and buffer pointer.
- `VacDirEnum`, directory enumeration state containing `VacFile`, block offset, entry indexes, and buffered `VacDir` entries.

This header supports metadata packing and directory enumeration in the broader `vac` codebase.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/error.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/error.c

Defines global Vac error string variables.

Errors include:
- Missing/unallocated directory entry.
- No such file/path and bad path.
- Corrupted directory or metadata.
- Not directory/file.
- I/O error.
- Bad offset, too big, read-only, removed.
- Illegal block address.
- Directory not empty, file exists, cannot remove root.

These strings are declared in `error.h` and used across the Vac implementation for `werrstr`-style reporting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/error.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/error.h

Vac error string declaration header.

Behavior:
- Undefines `EIO` first, because host headers such as macOS `<errno.h>` may define it as a macro.
- Declares all error strings defined in `error.c`, including directory, metadata, block, path, read-only, removed, existence, and root-removal errors.

This keeps Vac’s symbolic error names portable across host build environments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vac/error.h -->
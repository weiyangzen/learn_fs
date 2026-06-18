# Group Research: group_22_9front_sources_os_plan9_9front_sys_src_9_port_devtls_c_sources_os_pla_42f5c6359d30

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devtls.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devtls.c

Implements the Plan 9 TLS record-layer device, exposed as `#a/tls`. It supports SSL 3.0 through TLS 1.2 record framing, close/error alerts, application records, handshake record forwarding, and cipher-state changes controlled from user space.

The device presents `clone`, `encalgs`, `hashalgs`, and per-conversation files `ctl`, `data`, `hand`, `status`, and `stats`. A user-space handshaker opens `hand`, binds an underlying fd with `ctl fd`, sets protocol version and secrets, writes `changecipher`, and finally sends `opened` to permit application data on `data`.

Core state is held in `TlsRec`, with independent `OneWay` input/output cipher state, sequence counters, pending secrets, processed/unprocessed record blocks, and a handshake queue. `tlsrecread` parses and decrypts records, handles SSL2-format initial ClientHello compatibility, routes handshake/alert/application data, validates MACs or AEAD tags, and updates cipher state on ChangeCipherSpec. `tlsrecwrite` fragments output into records, computes AAD/MAC/tag, pads CBC records, encrypts, and writes to the underlying channel.

Supported algorithms include clear, RC4-128, 3DES-CBC, AES-CBC, ChaCha20-Poly1305 variants, AES-GCM variants, MD5, SHA1, and SHA256 HMAC. The code depends on Plan 9 block queues, device dispatch, `libsec`, and fd-to-channel kernel plumbing.

Security-sensitive points are the record error paths, CBC padding/MAC behavior, nonce handling for AEAD, and state transitions around `opened`, close notify, and fatal alerts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devtls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devuart.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devuart.c

Implements the `#t` UART device. It enumerates physical UART providers from `physuart[]`, builds `eiaN`, `eiaNctl`, and `eiaNstatus` entries, and exposes serial input/output through Plan 9 queues.

`uartenable` opens input/output queues, applies default line settings, enables the physical UART, and links it into the enabled UART list. `uartdisable` removes it and calls the hardware disable hook. `uartopen` increments open counts for control/data files; `uartclose` closes queues, drains output, disables hardware, and clears modem hangup state.

Control commands in `uartctl` configure baud, DTR/RTS, FIFO, break, bits, parity, stop bits, queue limits, nonblocking mode, timer cadence, modem control, hangup behavior, and software flow control. RX interrupt input enters an interrupt staging ring via `uartrecv`, then `uartclock` periodically flushes it to the input queue and handles hangups/backoff.

The file also owns console UART helpers `uartgetc`, `uartputc`, and `uartputs`, plus mouse-special UART entry points. Main dependencies are `PhysUart`, `Uart`, queues, timers, and `netif` qid encoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devuart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devusb.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devusb.c

Implements the Plan 9 USB device framework at `#u`. It does not enumerate devices itself; user-space `usbd` drives enumeration using this kernel endpoint abstraction. Host-controller implementations register via `addhcitype`.

The namespace contains `usb/ctl` and endpoint directories `epN.M` with `data` and `ctl`. Endpoint zero represents a USB device; additional endpoints are created with control commands. `newdev` creates device endpoint zero, tracks hub/root-port/topology state, handles transaction translator metadata, and assigns device ids. `newdevep` creates nonzero endpoints with default transfer parameters.

Control commands cover new endpoint/device creation, detach, reset, debug, clear halt, address assignment, hub configuration, max packet size, transfer descriptors, poll interval, timeout, isochronous timing, endpoint names, and info strings. Root hubs are faked with `rhubread`/`rhubwrite`, translating hub class requests into HCI port operations.

`usbopen` validates endpoint type/mode, enforces exclusive data opens, computes bandwidth/load, and calls HCI endpoint open. `usbread`/`usbwrite` dispatch endpoint I/O through HCI hooks, with special root-hub handling. Locking and refcounts around `eps[]`, `Ep`, and `Udev` are central to safe endpoint lifetime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devusb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devwd.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/devwd.c

Implements a small watchdog device `#w` with `wdctl`. Platform watchdog backends register through `addwatchdog`, which installs a single global `Watchdog` and disables it initially.

Reads from `wdctl` call the backend `stat` hook if present. Writes accept `enable`, `disable`, and `restart`, dispatching to the backend hooks. The device otherwise uses standard device helpers for attach, walk, stat, open, remove, wstat, and power.

Important behavior: writes reject nonzero offsets or messages larger than `READSTR`; unknown commands return `Ebadarg`. The file assumes the write buffer is mutable when it truncates at newline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/devwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dtracydev.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/dtracydev.c

Provides the DTrace-like `dtracy` provider for Plan 9 `Dev` operations. It registers entry and return probes for walk, stat, open, create, close, read, bread, write, bwrite, remove, and wstat for each device in `devtab`.

`devprovide` snapshots each original `Dev` into `ledger[i].clean`, then creates probes named like `dev:<device>:<op>:entry` and `dev:<device>:<op>:return`. Enabling a probe swaps the selected operation pointer in `devtab[i]` to a wrapper; disabling restores the clean function pointer.

Wrappers package arguments into `DTTrigInfo.arg[]`, trigger the entry probe, call the original implementation, place the return value in `arg[9]` where applicable, and trigger the return probe. This is invasive instrumentation: correctness depends on preserving original function signatures and restoring function pointers exactly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dtracydev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dtracysys.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/dtracysys.c

Provides the `dtracy` syscall provider. It wraps entries in `systab[]` with generated `WRAP0` through `WRAP5` functions that copy syscall arguments from a `va_list`, trigger `sys:<name>:entry`, invoke the original syscall, place the return value in `arg[9]`, and trigger `sys:<name>:return`.

`wraptab[]` maps syscall numbers to wrappers for common Plan 9 syscalls including bind, open, read, write, mount, stat, wstat, pread, pwrite, semacquire, seek, and nsec. `sysprovide` creates entry/return probes for every valid syscall name in `sysctab`, normalizing uppercase names and special-casing `SYSR1`.

`sysenable` and `sysdisable` swap `systab[i]` with `wraptab[i]` when total enabled probes transitions to or from zero. This pointer-swap scheme is compact but assumes wrapper coverage for enabled syscall indices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dtracysys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dtracytimer.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/dtracytimer.c

Implements the `dtracy` timer provider. It creates one probe, `timer::1tk`, and triggers it from `dtracytick`.

When enabled, `running` is set and each tick records the interrupted program counter in `arg[0]` and whether the register frame is user mode in `arg[1]`. Disabling clears `running`. This is a minimal sampling hook intended to be called from architecture timer interrupt code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/dtracytimer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ecc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/ecc.c

Implements NAND flash ECC generation and correction for 256-byte data chunks. `nandecc` uses a precomputed table to compute line and column parity into a 24-bit ECC value.

`nandecccorrect` compares calculated and stored ECC values. It returns good on exact match, corrects a single data-bit error when the syndrome matches `CORRECTABLEMASK`, updates stored ECC, detects a single-bit error in the ECC itself, or reports an uncorrectable two-bit error. Optional reporting prints calculated/stored ECC and correction details.

The file depends on `nandecc.h` for `NandEccError` result values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ecc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/edf.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/edf.c

Implements kernel earliest-deadline-first scheduling support. It manages EDF admission, release/deadline timers, runtime accounting, yield-to-next-period behavior, and a schedulability test over admitted processes.

`edfinit` allocates `Edf` state. `edfadmit` validates period/cost/deadline settings, runs `testschedulability`, marks the process admitted, synchronizes releases with same-period tasks where possible, and schedules immediate or future release. `edfready` decides whether a process is runnable now, should wait for release, or can continue best-effort with extra time.

`edfrun` arms deadline timers based on remaining slice and deadline. `edfrecord` charges runtime to EDF or extra time and forces deadline expiry when budget is exhausted. `edfyield` sleeps until the next release. `edfstop` expels a process and cancels timers.

The schedulability test simulates release/deadline events ordered by `testenq`, bounded by `Maxsteps`. Integration points include run queues, timer callbacks, process tracing, and process priority demotion to `PriExtra`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/edf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/edf.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/edf.h

Defines EDF scheduler constants and the `Edf` structure. Flags cover admitted/sporadic tasks, yield behavior, notes, deadline state, and extra-time mode. Time fields are in microseconds and include deadline, inherited deadline, period, cost, remaining slice, release time, absolute deadline, next period start, and last scheduled time.

The struct embeds a `Timer`, schedulability-test fields, and accounting counters for EDF runtime, extra runtime, aging, periods, and missed deadlines. It declares `edflock` and `edfunlock`, plus format-check pragmas for EDF time formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/edf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/error.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/error.h

Declares the kernel’s shared external error string symbols. These include namespace, mount, permission, argument, I/O, networking, process, memory, exec, stat, directory, media, and message-size errors.

The header is widely included by device and kernel subsystems so they can call `error(E...)` using canonical Plan 9 error strings. Definitions live elsewhere; this file is declaration-only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/etherif.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/etherif.h

Defines the shared Ethernet controller interface. `Ether` embeds `ISAConf` and `Netif`, stores bus/device metadata, MTU bounds, device hooks for attach/transmit/control/power/shutdown, an output queue, MAC address, bridge MAC table, and optional destination MAC address table.

It declares helpers for speed/link updates, packet input, driver registration, Ethernet CRC, and MAC parsing. Small ring arithmetic macros are also provided.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/etheriwl.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/etheriwl.c

Implements the Intel Wi-Fi Link driver for many Intel PCI wireless chip families, from 4965/5000/6000-era devices through 7000/8000/9000 family devices. It relies on firmware from `/boot` or `/lib/firmware`.

The file defines large hardware register maps, flow-handler registers, scheduler registers, firmware TLV parsing, EEPROM/NVM access, DMA ring setup, RX/TX queues, firmware paging memory, calibration state, station/context state, and controller state. `iwlpci` discovers supported Intel PCI IDs and maps BAR0; `iwlpnp` binds a controller to an `Ether` device and installs hooks.

Firmware handling includes `readfirmware`, `crackfw`, `loadsections`, `loadfirmware1`, `ucodestart`, and `boot`. It supports both older boot-code paths and newer section-loading paths, including init firmware calibration followed by main firmware runtime.

Runtime configuration sends firmware commands for PHY, MAC, binding contexts, stations, multicast filter, power mode, MCC/LAR, Bluetooth coexistence, calibration, paging, and TX antenna setup. `rxon` reconciles current channel/BSSID/AID/promiscuous settings and programs older or newer firmware families through `rxon6000` or 7000+ context commands.

Transmit builds firmware TX commands from Wi-Fi nodes, rates, antenna masks, ACK/RTS/protection requirements, station ids, and packet blocks, then queues them through `qcmd`. Receive drains the RX ring, handles command completions, firmware alive/errors, calibration records, NVM responses, time events, TX status, RX PHY timestamps, and received frames forwarded to `wifiiq`.

Interrupt handling disables/re-enables masks, acknowledges ISR/FH ISR, calls receive processing, records wait bits, and marks the controller broken on firmware/hardware fatal errors. A recovery kernel process periodically powers off, resets, boots firmware, and restores RX state when `broken` is set.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/etheriwl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethermii.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/ethermii.c

Implements generic MII/PHY support for Ethernet drivers. It probes PHYs, creates `MiiPhy` records, reads/writes PHY registers with optional paged register handling, resets PHYs, configures autonegotiation, and computes link status.

`mii` probes a mask of possible PHY addresses and records valid OUIs. `miimir`/`miimiw` serialize register access and apply `pagereg` mapping. `miiane` advertises 10/100/1000 capabilities and pause support, then restarts autonegotiation. `miianec45`, `miimmdr`, and `miimmdw` support MMD/Clause-45 style multi-gigabit autonegotiation registers.

`miistatus` reads status twice for sticky link state, determines negotiated speed/duplex/flow-control, and sets `phy->link`. `miistatusc45` handles 2.5G/5G/10G MMD status bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethermii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethermii.h -->
# File Research: sources/os/plan9/9front/sys/src/9/port/ethermii.h

Defines MII register numbers, status/control bit masks, autonegotiation advertisements, 1000BASE-T master/slave bits, extended status bits, and MMD multi-gigabit control/status bits.

It defines `Mii`, containing PHY array, current PHY, controller name/context, and read/write hooks, plus `MiiPhy`, containing identity, advertised capabilities, link result fields, and optional page-register mapper. It declares all generic MII helper functions and `addmiibus`/`delmiibus` hooks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethermii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethersink.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/ethersink.c

Implements a sink Ethernet driver: an Ethernet `/dev/null` useful as a bridge target for Ethernet-based VPNs. `reset` registers a non-linking 1000 Mbps pseudo-interface with attach, multicast, promiscuous, and control hooks.

`attach` makes the output queue nonblocking and sets its limit to zero, silently discarding output. The custom `ctl` accepts `ea <mac>` to set the interface MAC address. Multicast and promiscuous operations are no-ops.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethersink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethervirtio10.c -->
# File Research: sources/os/plan9/9front/sys/src/9/port/ethervirtio10.c

Implements a non-legacy Virtio 1.0 Ethernet driver for PCI devices that require modern virtio capability-based MMIO access. It targets the case where QEMU disables legacy virtio-net.

The driver discovers virtio PCI capabilities, maps common/device/ISR/notify regions, negotiates features, initializes RX/TX/control virtqueues, and registers an `Ether` device. `attach` enables queues, marks the driver ready, and starts RX/TX kernel processes.

`txproc` consumes blocks from the Ethernet output queue and posts two-descriptor TX chains: virtio net header plus packet. `rxproc` maintains RX buffers, posts them to the receive queue, and forwards completed packets to `etheriq`. `vctlcmd` sends control-queue commands for promiscuous and all-multicast modes.

Interrupt handling wakes queues when used rings advance. `shutdown` clears device status and bus mastering. `ifstat` reports negotiated features, device status, and queue indices/counters. The implementation depends on `virtio10.h`, PCI helpers, DMA-safe ring allocation, and Plan 9 block pools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/port/ethervirtio10.c -->
# Group Research: group_165_9front_sources_os_plan9_9front_sys_src_cmd_nusb_cam_ctl_c_sources_os_985a12ca801d

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/ctl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/ctl.c

This file implements the control-plane surface for the 9front USB Video Class camera driver. It defines a `Param` table mapping user-visible control names to UVC control selectors, value lengths, advertised-control bitmap bits, and per-type read/write handlers. The file is responsible for turning textual 9P `ctl` messages into UVC `GET_*` and `SET_CUR` control transfers, and for formatting available camera state back into readable lines.

The low-level helpers cover booleans, signed integers, unsigned integers, and enumerated values. Reads first use `GET_INFO` through `infocheck()` to verify that a control supports `GET`, then issue `GET_CUR`, and for numeric values also `GET_MIN`, `GET_RES`, and `GET_MAX`. Failed control requests call `errorcode()`, which fetches `VC_REQUEST_ERROR_CODE_CONTROL` from the relevant terminal/unit and maps UVC error codes to Plan 9 error strings.

Special parameters handle stream format and frame rate. `pformatread()` reports the current probe-control format/frame as `<width>x<height>x<bits>-<fourcc>`, falling back to numeric format/frame indices if descriptors are missing. `pformatwrite()` parses `WIDTHxHEIGHT` or `WIDTHxHEIGHTxBPP-FOURCC`, searches the parsed format/frame descriptor arrays, refuses changes while the camera is active, and snaps the frame interval to a valid interval for the selected frame. `pfpsread()` and `pfpswrite()` expose `dwFrameInterval` as frames per second, again rejecting changes while active.

`ctlread()` enumerates all special controls plus camera-terminal and processing-unit controls actually advertised by descriptor bitmaps. `ctlwrite()` accepts either an explicit unit id followed by parameter name, or an automatic form where the parameter name selects the first matching unit type. It validates unit type, advertised support, and write availability before dispatching to the parameter writer.

Key dependencies are the global UVC descriptor arrays `unit`, `unitif`, and `nunit` declared in `dat.h`, `ProbeControl` and selector constants from `uvc.h`, and `getframedesc()` from `video.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/dat.h

This header defines the shared in-memory state used by the USB camera driver. `Format` pairs a UVC uncompressed-format descriptor with an array of frame descriptors. `VFrame` is the buffered video-frame object used by the streaming path, with byte count, allocation size, read cursor, data pointer, and linked-list pointer.

`Cam` is the main per-camera object. It stores the USB device and selected streaming endpoint, the streaming interface and input header, parsed format table, current UVC probe control, 9P file handles for camera files, and streaming state. The streaming fields include active/abort flags, active and free frame lists, a deferred-read request queue, a `QLock`, converter process id, and frame read mode.

The header also declares the global VideoControl unit arrays `nunit`, `unit`, and `unitif`, used by `ctl.c` and descriptor parsing code to associate UVC units with interfaces and advertised control bitmaps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/descprint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/descprint.c

This file provides diagnostic pretty-printers for USB Video Class descriptors and probe-control state. Each `print*` function accepts a Plan 9 `Fmt` and a raw descriptor pointer, casts it to the relevant UVC structure from `uvc.h`, and emits a labeled multi-line textual view.

The VideoControl side covers headers, input terminals, output terminals, camera terminals, selector units, processing units, encoding units, and extension units. Camera-terminal and processing-unit printers expose important control metadata such as terminal/unit ids, terminal type, source id, focal lengths, control sizes, and `bmControls` bitmaps. Extension and selector unit printers handle variable-length source-id/control arrays by walking through trailing bytes.

The VideoStreaming side covers input/output headers, still-frame descriptors, uncompressed format descriptors, uncompressed frame descriptors, and color-format descriptors. Frame printing includes dimensions, bit-rate bounds, frame-buffer size, default interval, and either continuous min/max/step interval data or discrete frame intervals.

`printProbeControl()` dumps every field of a UVC probe/commit control block, including format/frame indices, frame interval, max frame and payload sizes, version fields, H.264-related fields, and layout-per-stream entries. `printDescriptor()` is the dispatcher: it uses the interface subclass and descriptor subtype to select the correct printer, with unknown subtype messages for unsupported VideoControl or VideoStreaming descriptors.

This file has no device I/O side effects; it is purely formatting support for camera introspection files and debug output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/descprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/fns.h

This header declares cross-file functions for the UVC camera driver. It exposes control read/write entry points, descriptor and probe-control printers, streaming lifecycle functions (`videoopen`, `videoclose`, `videoread`, `videoflush`), and `getframedesc()` for resolving the active format/frame indices.

The declarations define the narrow coupling between the 9P camera frontend, the UVC control implementation, descriptor diagnostics, and the video conversion/streaming implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/uvc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/uvc.h

This header defines the UVC descriptor layouts, request codes, class/subclass constants, descriptor subtype constants, terminal/unit control selector constants, and little-endian helper macros used by the USB camera driver.

The descriptor structs model the variable-length UVC descriptors as C layouts with trailing one-element arrays where necessary. It includes VideoControl descriptors (`VCHeader`, terminals, selector/processing/encoding/extension units), VideoStreaming descriptors (`VSInputHeader`, `VSOutputHeader`, `VSStillFrame`, uncompressed format/frame descriptors, color format), and `ProbeControl`. These definitions are used directly by parser, control, descriptor printing, and streaming code by casting raw descriptor bytes from the USB library.

The enum section captures UVC class values (`CC_VIDEO`, `SC_VIDEOCONTROL`, `SC_VIDEOSTREAMING`), class-specific descriptor types, VideoControl and VideoStreaming subtypes, request codes (`GET_CUR`, `GET_MIN`, `GET_MAX`, `GET_RES`, `GET_INFO`, `SET_CUR`, and aggregate variants), camera-terminal controls, processing-unit controls, encoding-unit controls, streaming controls, and terminal type values such as `ITT_CAMERA`.

The header uses `GET3` in addition to the USB library's `GET2` and `GET4`. All multi-byte fields in the structs are byte arrays, which keeps descriptor interpretation endian-explicit and matches the rest of the nusb code style.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/uvc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/video.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/video.c

This file implements the UVC video streaming path. It manages a pool of `VFrame` objects, reads isochronous/bulk video payloads from the selected endpoint, reconstructs complete raw frames, converts them to Plan 9 RGB image data, and services pending 9P video reads.

Frame queues are split into free and active lists protected by `Cam.qulock`. `grabframe()` obtains a free frame or recycles an inactive active-list frame, while `pushframe()` appends a completed frame and wakes deferred reads. `videoread()` either returns the next bytes of an active frame, queues the 9P request if no frame is available, or returns a zero-length delimiter in frame mode after a complete frame has been consumed. `videoflush()` removes an interrupted queued read.

The only built-in pixel converter is YUY2. `yuy2convert()` transforms packed YUY2 into a Plan 9 `b8g8r8` image buffer with a 60-byte image header. `getconverter()` matches a UVC GUID against the converter table and reports unknown format GUIDs.

`cvtproc()` is the streaming worker. It reads endpoint packets, tracks UVC frame-id toggles in the payload header, accumulates payload bytes until a full raw frame is present, converts the frame, and pushes it to readers. On abort or read failure it frees frame lists, closes the endpoint, restores the streaming interface alternate setting, and clears active state.

`videoopen()` validates the selected frame descriptor and converter, performs UVC probe/commit negotiation, selects an alternate endpoint setting with sufficient bandwidth in `selbw()`, opens endpoint data, allocates the frame pool, and starts `cvtproc()`. `videoclose()` interrupts the converter process by setting the abort flag and sending a thread interrupt.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/video.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/disk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/disk.c

This file is the USB mass-storage 9P file server. It supports SCSI transparent command devices over USB bulk-only transport and exposes each logical unit as a small disk tree with `ctl`, `raw`, `data`, and user-defined partition files.

Partition management is adapted from Plan 9 disk/partfs. `addpart`, `delpart`, `lookpart`, `freepart`, `fixlength`, and `makeparts` maintain per-LUN `Part` entries in block units. The `ctl` file reports inquiry, USB device path, LUN number, geometry, and extra partitions; writes accept `part name start end` and `delpart name`.

USB mass-storage setup starts by finding bulk endpoints for either bulk-only (`Protobulk`) or UAS protocol ids, issuing class-specific reset and Get Max LUN requests, and probing each LUN with SCSI inquiry and capacity reads. Capacity supports both READ CAPACITY(10) and READ CAPACITY(16) when the 10-byte response reports `0xffffffff`.

`umsrequest()` is the transport bridge used by `scsireq.c`: it builds a command block wrapper, writes it to the OUT endpoint, transfers optional data, reads and validates a command status wrapper, maps CSW status to SCSI status, handles residue quirks, and reports hard errors for phase failures.

The 9P implementation maps root entries to LUN directories and LUN entries to partition/control files. Normal `data` and partition I/O uses `setup()` to align arbitrary byte offsets/counts to logical blocks, using an intermediary block buffer for partial-block reads/writes. `raw` implements a three-phase command/data/status interface for direct SCSI command passthrough.

The main routine parses debug flags, opens and configures the USB device, performs mode-switch exits for known fake-storage modem/NIC devices, applies a SanDisk residue quirk, initializes LUNs, names them `sdU...`, and posts the service under `/srv/usb`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/mkscsierrs -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/mkscsierrs

This rc script generates a C source fragment containing SCSI additional sense-code messages. It emits includes, an `Err` struct, a `scsierrs[]` table, and a `scsierrmsg(int)` lookup function.

The table is generated from `/sys/lib/scsicodes`. Lines beginning with four lowercase hexadecimal characters followed by whitespace are transformed by `sed` into `{0xCODE, "message"}` entries. The generated lookup returns the matching message or the generic string `"scsi error"`.

The generated function is referenced by `scsireq.c` through the declaration in `scsireq.h`, allowing USB disk diagnostics to report textual SCSI sense errors without depending on libdisk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/mkscsierrs -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.c

This file is a local copy/adaptation of Plan 9 `scuzz` SCSI request helpers, modified for USB disk support and extra debugging. It builds SCSI command descriptor blocks, dispatches them either through `umsrequest()` for USB transparent SCSI or through an existing raw file descriptor, handles status/sense processing, and exposes higher-level helpers such as inquiry, read, write, seek, mode sense/select, start, and read capacity.

The command builders select 6-, 10-, or 16-byte read/write/seek forms based on block offset, transfer size, and flags. Direct-access devices normally use READ/WRITE(10), while small offsets may use 6-byte commands unless `Frw10` is set. Very large offsets use 16-byte commands. Sequential-device logic supports fixed-block tape-like reads/writes and includes legacy Exabyte-specific behavior.

`SRrequest()` is the central dispatcher. It emits optional debug traces, calls USB or raw transport, records returned status, retries on busy, runs REQUEST SENSE after check-condition status, converts sense data to error strings through `scsierrmsg()`, and returns byte counts on success. The debug helpers format outgoing commands, returned status, partial data bytes, and sense-derived errors.

Device-opening helpers probe inquiry data and initialize device-type-specific state. Direct devices read capacity and set logical block size; sequential devices query block limits and select variable or fixed block modes; WORM/CD-like devices use mode sense for block size. `SRopenraw()` opens a `raw` file in a served disk tree, while `SRopen()` performs readiness and device-type setup.

The implementation preserves broad SCSI support beyond USB disks, but in this group its important role is as the reusable SCSI command library called by `disk.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.h

This header defines the SCSI request API and constants shared by the USB disk server and SCSI helper implementation. `ScsiPtr` describes command or data buffers, and `ScsiReq` stores flags, unit/lun identity, block size, current block offset, raw fd, USB LUN pointer, command/data buffers, status, sense data, inquiry data, and tape-read state.

The enums cover software flags (`Fopen`, `Fseqdev`, `Frw10`, `Fusb`, and others), SCSI status codes, internal status values with sense-data/software/bad-argument/read-only meanings, command opcodes for direct, tape, CD/MMC, changer, DVD, and vendor-specific operations, sense-data bit masks, block-address limits, and device types returned by inquiry.

The header also provides big-endian SCSI helper macros (`GETBELONG`, `PUTBELONG`, `GETBE24`, `PUTBE24`) and prototypes for all `SR*` operations, `SRrequest`, raw/open/close helpers, `umsrequest`, `scsidebug`, and `scsierrmsg`.

It intentionally forward-declares `Umsc` so the generic SCSI request object can carry a USB-mass-storage LUN pointer without requiring all USB transport internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/scsireq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/ums.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/ums.h

This header defines USB mass-storage transport constants and data structures. It includes protocol/subclass ids, class-specific request codes (`Umsreset`, `Getmaxlun`), maximum LUN/partition limits, raw-command phase values, CBW/CSW sizes and status codes, and data direction flags.

`Part` represents a served partition in logical-block units. `Umsc` embeds `ScsiReq` as its first field and extends it with a served name, block count, byte capacity, transfer setup scratch state, a `QLock`, partition table, raw command buffer, raw phase, inquiry string, parent `Ums`, and an aligned I/O buffer sized to `Maxiosize`.

`Ums` stores the opened USB IN/OUT endpoints, the LUN array, maximum LUN index, bulk-only sequence tag, and a quirk flag for devices that report wrong residues.

`Cbw` and `Csw` model the USB bulk-only Command Block Wrapper and Command Status Wrapper layouts used by `disk.c`'s `umsrequest()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/disk/ums.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/asix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/asix.c

This file implements ASIX USB Ethernet chip support for the common nusb Ethernet server. It covers older AX88178/AX88772-style devices and AX88179/AX88178A-style gigabit devices, each with different vendor control requests and packet framing.

The common ASIX section defines media-mode bits, RX-control bits, MII register bits, and helpers for vendor reads/writes, GPIO, PHY id, RX control, MII reads/writes, and EEPROM reads. The AX88178/AX88772 receive path parses ASIX packet headers containing length and one's-complement length, extracts one or more Ethernet frames from a USB transfer, and passes valid frames to `etheriq()`. Transmit prepends the ASIX length/check header and emits a padding header when the transfer is max-packet aligned.

`a88178init()` performs GPIO and EEPROM-dependent reset sequencing, reads the MAC address, configures PHY advertisement including gigabit where appropriate, starts autonegotiation, programs medium mode and RX control, and installs callbacks. `a88772init()` handles embedded/external PHY selection, reset sequencing, MAC read, PHY advertisement, IPG setup, RX enable, and callback installation.

The AX88179 path defines a separate register-access API, receive aggregation parser, transmit header format, link wait, promiscuous/multicast toggles, and link-speed callback. `a88179init()` resets PHY/clock state, handles 88179A firmware compatibility, optionally sets or reads the MAC address, enables RX filtering and power behavior, waits for link, selects bulk-in queue parameters based on USB/link speed, programs medium mode, and installs the callbacks used by `ether.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/asix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/aue.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/aue.c

This file supports ADMtek Pegasus-style USB Ethernet adapters. It defines vendor register read/write requests, control/status register bits, EEPROM/MII register addresses, GPIO bits, and packet status masks.

The CSR helpers read and write 8- and 16-bit device registers through USB vendor control requests. `eeprom16r()` reads 16-bit EEPROM words by programming the EEPROM address/control registers and polling for completion. `reset()` resets the MAC and toggles GPIOs needed by the chip.

`auereceive()` reads a USB packet, removes the four-byte trailing status/length header, drops packets with error bits or invalid lengths, and queues valid frames through `etheriq()`. `auetransmit()` prepends a two-byte frame length before writing to the OUT endpoint.

Promiscuous and multicast callbacks update receive-control bits (`C2prom` and `C0allmulti`). `aueinit()` resets the chip, reads the MAC address from EEPROM, writes it into PAR registers, disables promiscuous mode, enables RX/TX and endpoint counter clearing, then installs the common Ethernet callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/aue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/cdc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/cdc.c

This file implements generic CDC Ethernet packet framing for the nusb Ethernet server. It uses no device-specific data headers: `cdcreceive()` reads a USB bulk packet directly into a `Block` and submits it to `etheriq()`, and `cdctransmit()` writes the Ethernet frame as-is.

The transmit path sends a zero-length packet when the frame length is an exact multiple of the endpoint max packet size, with a comment noting that some Linux behavior differs by sending an extra byte.

`cdcinit()` scans device-specific descriptors for an Ethernet networking functional descriptor (`Dfunction`, `Fnether`). It loads the MAC-address string referenced by the descriptor, validates that it is 12 hex characters, parses it into `macaddr`, and installs receive/transmit callbacks. It returns failure if no suitable descriptor/MAC is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/cdc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/dat.h

This header defines shared data structures and globals for USB Ethernet drivers. `Block` is the packet buffer with read/write pointers, limit, base storage, and next pointer; `BLEN`, `allocb`, `copyblock`, and `freeb` provide lightweight buffer operations.

It defines Ethernet constants (`Eaddrlen`, `ETHERHDRSIZE`, `Maxpkt`), `Etherpkt` header layout, CDC descriptor constants used during endpoint/interface discovery, and `Macent` entries for the bridge-learning table.

The globals include debug flags, user-specified MAC flag, promiscuous/multicast counters, multicast address table, active MAC address, bridge MAC table, `etheriq()` ingress hook, and driver callback slots. Chip-specific files fill `epreceive`, `eptransmit`, and optional promiscuous/multicast/link-speed callbacks during initialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/ether.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/ether.c

This file is the common 9P Ethernet server used by all nusb USB Ethernet chip drivers. It presents a Plan 9 Ethernet-like tree under `usbnet`, with an interface directory, `clone`, `stats`, `addr`, and per-connection directories containing `ctl`, `data`, and `type`.

Connections are represented by `Conn`, while each open `data` file owns a `Dq` queue pairing pending 9P reads with queued `Block`s. `matchrq()` matches frames to waiting reads. `fsopen()` allocates connection slots through `clone`, initializes per-connection flags, and attaches queues. `fswrite()` accepts control messages for bridge mode, bypass mode, header-only tracing, promiscuous mode, multicast membership, and EtherType filtering. It also handles writes to `data` by building a packet block with headroom/trailer slack and passing it to the output path.

Ingress and egress share `ethermux()`, which validates Ethernet frames, filters unicast/multicast/broadcast traffic, learns source addresses for bridge mode, applies per-connection EtherType and promiscuous filters, supports header-only trace delivery, and decides whether a packet should be consumed locally, delivered to a bypass connection, bridged, or transmitted. `etheriq()` handles USB ingress, and `etheroq()` handles user egress, including source-MAC rewriting for non-bridge connections.

Endpoint discovery prefers CDC union descriptors that tie an Ethernet control interface to a data interface, then falls back to any interface with bulk IN/OUT endpoints. `threadmain()` parses debug, MAC override, and driver type arguments, opens/configures the USB device, finds endpoints, invokes the selected chip-specific init function, opens endpoint data files, starts the USB read process, and posts the 9P service.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/ether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/lan78xx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/lan78xx.c

This file supports Microchip/SMSC LAN78XX USB Ethernet controllers, including the Ethernet core used in LAN7515 hub-plus-Ethernet devices. It defines LAN78XX register addresses, USB vendor requests, FIFO sizing, burst parameters, EEPROM access bits, RX/TX framing flags, MAC/PHY control bits, and MII advertisement/status constants.

The register helpers `wr()` and `rr()` perform 32-bit vendor control writes/reads. `miird()` and `miiwr()` access the internal PHY through the MII address/data registers. `eepromr()` reads bytes from EEPROM by polling the E2P command register. `phyinit()` resets the PHY, advertises 10/100 plus pause/asymmetric pause and gigabit full-duplex, configures LED modes, and restarts autonegotiation.

The receive path reads a burst-sized buffer, parses LAN78XX RX command headers, drops packets with `Rxerror`, aligns to four-byte packet boundaries, and submits frames to `etheriq()`. Transmit prepends two 32-bit TX command words including frame length and FCS request.

Promiscuous and multicast callbacks update `Rfectl` accept bits. `lan78xxlinkspeed()` derives 0/10/100/1000 Mbps from PHY status and partner ability. `lan78xxinit()` performs hardware and PHY reset, reads or applies the MAC address, programs address filters, USB burst mode, FIFO sizes, interrupts, LEDs, flow control, checksum-offload disable, PHY init, MAC RX/TX enable, FIFO enable, and callback installation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/lan78xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/rndis.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/rndis.c

This file implements minimal RNDIS Ethernet support. It defines static RNDIS initialize, query-permanent-address, and set-current-filter messages, plus helpers to send and receive encapsulated control messages over class/interface control requests.

`rndisin()` repeatedly fetches control responses, rejects nonzero status, ignores asynchronous status messages, and reports short responses. `rndisinit()` sends the initialize message, validates the initialize-complete response, requires a connectionless 802.3 device, queries the permanent MAC address, validates returned offset/size, copies it to `macaddr`, sets a packet filter for all multicast plus broadcast, and installs callbacks.

Data transfer uses the RNDIS packet message header. `rndisreceive()` reads a USB packet, validates message type, total length, data offset, data length, and minimum Ethernet header size, then advances the block read pointer to the embedded Ethernet frame before calling `etheriq()`. `rndistransmit()` prepends a 44-byte RNDIS packet header around each Ethernet frame before writing to the endpoint.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/rndis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/smsc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/smsc.c

This file supports SMSC LAN95XX USB Ethernet controllers. It defines register addresses, burst/flow-control defaults, EEPROM command bits, MAC/RX/TX flags, MII access bits, PHY advertisement/status bits, and receive/transmit framing flags.

Like `lan78xx.c`, it uses 32-bit vendor register helpers and internal-MII helpers. `eepromr()` reads the MAC address bytes from EEPROM. `phyinit()` resets the PHY, advertises 10/100 and pause capabilities, clears pending PHY interrupt state, enables autonegotiation-complete/linkdown interrupt masks, and restarts autonegotiation.

`smscreceive()` reads either burst-sized or max-packet buffers, parses per-packet RX headers, drops error packets, strips the four-byte trailing checksum/status from complete packets, handles multiple aggregated frames, and sends good frames to `etheriq()`. `smsctransmit()` prepends two 32-bit TX headers with first/last segment bits.

Promiscuous and multicast callbacks adjust `Maccr` bits. `smsclinkspeed()` reports link-down, 100 Mbps, or 10 Mbps from PHY status. `smscinit()` resets hardware and PHY, reads or uses the configured MAC, programs address registers, burst behavior, interrupts, LEDs, flow control, VLAN tag, disables checksum offload, clears filters, initializes PHY, enables interrupts/MAC/TX, and installs callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/smsc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/url.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/url.c

This file supports Realtek RTL8150 USB 10/100 Ethernet adapters. It defines the vendor memory request, control/read/write selectors, device register offsets, command/RX/TX/media bits, PHY/MII fields, EEPROM offsets, and receive-status bits.

The `mem()` helper performs USB vendor memory reads or writes to device register offsets; `csr8r`, `csr16r`, `csr8w`, `csr16w`, and `csr32w` layer typed CSR access on top. `reset()` sets the software-reset bit and polls until it clears.

`urlreceive()` reads a packet plus four-byte trailer, discards short transfers, uses the two-byte receive status at the end to require a valid packet bit, and queues valid frames. `urltransmit()` pads frames shorter than 60 bytes before writing them directly to the bulk endpoint.

Promiscuous and multicast callbacks update RX configuration accept bits (`Aap`, `Aam`). `urlinit()` resets the device, reads the MAC address from ID registers, resets again, writes the MAC back, configures transmit retry/interframe gap and receive filters, clears multicast hash registers, enables TX/RX, and installs callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ether/url.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/joy/hid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/joy/hid.h

This header defines HID constants used by the USB joystick driver. It includes thread stack size, joystick and Xbox 360 class/subclass/protocol identifiers, maximum supported axes, HID class request codes, protocol values, output report selector, report descriptor item tags, and main-item flag bits.

The item-tag and flag constants mirror the generic HID report parser in `joy.c`: main items (`Input`, `Output`, `Collection`, `Feature`), global items (`Usage Page`, logical/physical bounds, report size/id/count), local items (`Usage`, usage ranges, designator/string fields), delimiter handling, and data/constant, variable/array, absolute/relative flags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/joy/hid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/joy/joy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/joy/joy.c

This file implements a USB HID game-controller reader that prints joystick events to standard output. It opens an interrupt IN endpoint, obtains or supplies a HID report descriptor, parses incoming reports, tracks up to six axes and 64 buttons, and emits textual `axis`, `down`, and `up` lines for changed state.

The HID report parser is a compact recursive parser over HID short/long items. `repparse1()` maintains global and local item state, expands usage ranges, handles collections and push/pop, and calls a callback for each logical field in Input/Output/Feature items. `getbits()` extracts arbitrary bit fields from reports, and `signext()` handles signed fields.

`joyparse()` consumes Input fields only. It honors report ids, applies signed conversion and a configurable deadband, maps desktop usages X/Y/Z/Rx/Ry/Rz to axes, and maps button-page usages to a 64-bit button mask. `joywork()` reads reports, parses them, prints axis changes and button transitions, and retries transient read errors before treating the device as fatal.

The driver includes controller quirks. A PS3 controller is enabled through a feature-report request. Xbox 360 and compatible controllers often lack a HID descriptor, so `xbox360()` injects a synthetic report descriptor and sends an LED command. Some Shanwan-compatible devices receive vendor reads before the synthetic descriptor is installed.

`threadmain()` accepts debug and deadband options, selects a suitable interrupt IN endpoint matching generic joystick or Xbox 360 CSP values, and starts the reader.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/joy/joy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/kb/hid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/kb/hid.h

This header defines HID constants for the keyboard/mouse driver. It contains stack size, max simultaneous keys, class/subclass/protocol identifiers for boot mouse, generic HID, non-boot pointer, and boot keyboard endpoints, HID class request codes, boot/report protocol values, output-report selector, report descriptor item tags, and main-item flag bits.

These constants drive descriptor selection, `SET_IDLE`/`SET_PROTOCOL`/`SET_REPORT` control transfers, and the generic HID report parser in `kb.c`. The item tags and flags are parallel to the joystick header but include keyboard/mouse-specific CSP values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/kb/hid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/kb/kb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/kb/kb.c

This file implements the USB HID keyboard, mouse, touchpad, touchscreen, and tablet input bridge. It reads HID interrupt reports, parses them against HID report descriptors, translates keyboard usages to Plan 9 scan codes sent to `/dev/kbin`, translates pointer/touch data to mouse(3) messages sent to `/dev/mousein`, and serves a small control file for repeat timing, debug, and raw output reports.

Descriptor handling first tries to fetch the HID report descriptor. If missing for boot keyboard or boot pointer devices, it uses built-in boot descriptors. `setproto()` also sends `SET_IDLE` and switches boot-mode devices to either boot or report protocol as appropriate. Device quirks override or patch descriptors for a Gaomon S620 tablet and an Elecom trackball.

The HID parser recursively walks collections and fields, preserving global/local state and invoking `hidparse()` for collections and input items. `hidparse()` collects keyboard/consumer usages, button states, relative pointer deltas, absolute X/Y coordinates scaled to 31-bit mouse coordinates, scroll deltas, contact ids, touch in-range/tip state, stylus buttons, and contact dimensions into `Hidreport`/`Hidslot` structures.

`readerproc()` reads reports in a high-priority process. Keyboard state is diffed against the previous key set to emit key-up/key-down scan codes, and a repeat process generates repeated scan codes after configurable delay/period. Pointer slots are matched by usage/id, absolute z is converted to relative movement, multiple slots are combined, button bits are mapped to Plan 9 mouse buttons, and either absolute (`a`) or relative (`m`) mouse messages are written.

The 9P control file supports reading current repeat settings, writing `repeat N`, `delay N`, `debug N`, entering `rawon`, and then sending raw HID output reports until `rawoff`. `threadmain()` scans all interrupt IN endpoints with keyboard/pointer/HID CSPs, starts one reader per endpoint, and posts the control service if any setup succeeds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/kb/kb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dev.c

This file implements core USB device/endpoint lifecycle and control-transfer helpers for nusb drivers. It opens `/dev/usb/epN.M` control/data files, configures devices by reading descriptors, creates endpoint files through endpoint control messages, loads string descriptors, manages reference-counted `Dev` cleanup, and provides retrying USB control requests.

`openep()` creates or opens a kernel USB endpoint file for a parsed `Ep`, sets max packet size, transaction count, and polling interval, and returns a `Dev` for endpoint I/O. `opendev()` opens a control endpoint directory, stores path/id metadata, initializes fds, and sets a reference. `opendevdata()` opens the `data` file for an endpoint. `getdev()` accepts either a path or numeric device id, opens/configures endpoint zero, and stores the hash name used by served device names.

Descriptor loading uses `loaddevdesc()` for the device descriptor and string ids, and `loaddevconf()` for configurations. `configdev()` opens data if needed, loads the device descriptor, and loads all configurations. `closedev()` decrements references and frees endpoint/configuration/interface/descriptor trees, strings, paths, and fds.

`usbcmd()` constructs standard USB control request packets, writes them to the endpoint data file, optionally reads the reply, retries transient failures up to `Uctries`, and logs requests/replies when `usbdebug` is high. `unstall()`, `setconf()`, `setalt()`, and `devctl()` provide common endpoint recovery and configuration helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dump.c

This file provides USB debug formatting and allocation helpers. It defines the global `usbdebug`, endpoint direction/type names, USB class names, and device-state strings.

`classname()` maps USB class codes to readable names, including common standard classes and several special class values. `Ufmt()` is the `%U` formatter for `Dev *`: it prints endpoint path, device class/subclass/protocol, vendor/product ids, reference count, vendor/product/serial strings, configurations, interfaces, endpoints, and raw device-specific descriptors. Helper routines format interfaces, endpoints, and configurations.

The file also defines `estrdup()` and `emallocz()`, fatal-on-failure wrappers used throughout the nusb code. These set malloc tags for debugging and match Plan 9 style by aborting on allocation failure instead of returning null.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/parse.c

This file parses standard USB device and configuration descriptors into the in-memory structures from `usb.h`. `parsedev()` validates the device descriptor, records USB version, CSP, USB3 endpoint-zero max packet interpretation, class, configuration count, vendor/product/device ids, string descriptor ids, and endpoint zero defaults.

`parseiface()` validates interface descriptors, derives CSP from interface or device class, creates/looks up `Iface` entries by interface number, alternate setting, and CSP, links them into the configuration, and associates endpoint zero with the first interface of configuration zero.

`parseendpt()` validates endpoint descriptors, derives direction/type/address, creates endpoint ids that remain unique across type/direction/interface/alternate settings, merges same-interface IN/OUT endpoints into `Eboth` when possible, stores max packet size, high-bandwidth transaction count, attributes, polling interval, and attaches endpoints to both the device endpoint chain and the interface endpoint array.

`parsedesc()` walks the variable descriptor stream following a configuration descriptor. It dispatches standard interface and endpoint descriptors to the parsers and stores all other device-specific descriptors as raw `Desc` records tagged with the current configuration, most recent interface, and most recent endpoint. `parseconf()` validates the configuration header, records configuration value/attributes/power, checks total length, and parses the remaining descriptor stream.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/usb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/usb.h

This header is the central nusb USB library interface. It defines descriptor constants, standard request constants, USB class codes, endpoint direction/type constants, configuration attributes, HID report tag constants, and tunable limits for endpoints, configurations, interfaces, raw descriptors, and control-request retries.

The core structures are `Dev`, `Usbdev`, `Ep`, `Iface`, `Conf`, `Desc`, and unpacked standard descriptor layouts. `Dev` represents endpoint-zero devices or opened endpoints, with fds, parsed USB tree, endpoint pointer, refcount, and driver auxiliary pointer. `Usbdev` stores device-level identity, strings, configurations, endpoint chains, and raw device-specific descriptors. `Ep`, `Iface`, and `Conf` represent parsed topology and alternate settings.

The header provides little-endian `GET2`/`PUT2`/`GET4`/`PUT4` macros, CSP packing/unpacking macros, debug-print macros, vararg annotations, and declarations for descriptor parsing, device opening/configuration, endpoint opening, control transfers, unstalling, alt/config selection, allocation helpers, class-name formatting, and the `%U` formatter.

All driver subtrees in this group depend on this header for USB request construction, descriptor interpretation, endpoint selection, and common object lifetimes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/lib/usb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ptp/ptp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ptp/ptp.c

This file implements a USB PTP/MTP-like camera storage 9P server. It opens bulk IN/OUT endpoints, starts a PTP session, discovers storage ids and object handles, lazily maps them into a 9P tree, supports reading objects and thumbnails, supports deleting objects, and closes the session when the service exits.

The PTP transport uses `Ptprpc`, a fixed buffer for PTP command/data/response containers. `vptprpc()` builds operation requests, writes optional data phases, reads optional data phases, validates response type/transaction/code through `ptpcheckerr()`, decodes PTP response errors to strings, and extracts output parameters. Transfers are serialized through a single `Ioproc` sent over `iochan`; `ptprpc()` integrates that serialization with 9P request flush handling by racing I/O ownership against per-request interrupt channels.

Tree state is cached in `Node` objects indexed by qid path. `getnode()` lazily constructs root, storage, object, and thumbnail nodes by issuing `GetStorageInfo` or `GetObjectInfo`, decoding PTP UTF-16 strings, assigning directory/file modes, sizes, image-thumbnail names, object formats, parent/store/handle metadata, and timestamps from PTP date strings. `readchilds()` fills child lists by calling `GetStorageIds` or `GetObjectHandles`; image objects also get synthetic thumbnail nodes.

`fsread()` serves directories, attempts efficient partial file reads with `GetPartialObject`, and falls back to full `GetObject`/`GetThumb` caching. `fsremove()` maps object deletion to `DeleteObject` and frees cached object or thumbnail nodes. `fsdestroyfid()` releases cached object data when fids go away. `fsflush()` interrupts blocked PTP requests.

`threadmain()` opens/configures the USB device, finds bulk endpoints plus optional interrupt endpoint, opens endpoint data fds, creates the I/O process, opens a PTP session using the process id as session id, and posts the service as an `sdU...` tree with a `.ptp` service name.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/ptp/ptp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/acm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/acm.c

This file implements CDC ACM serial-device support for the shared nusb serial framework. It probes functional descriptors for call-management and abstract-control-management records, records the data-interface id from the call-management descriptor, and installs ACM serial operations when both required descriptors are present.

`acmsetparam()` sends a CDC `SET_LINE_CODING` class/interface request containing baud rate, stop bits, parity, and data bits. `acminit()` initializes defaults to 9600 baud, one stop bit, eight data bits, and applies them. `acmwait4data()` releases the serial lock while blocking on reads from the IN endpoint, then reacquires it.

`acmfindeps()` locates the data interface recorded during probe, finds bulk IN and OUT endpoints, optionally notes an interrupt endpoint if the serial framework expects one, and opens the data endpoints via `openeps()`. The installed `Serialops` supplies init, set-parameter, wait-for-data, and endpoint-finding behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/acm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ch340.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ch340.c

This file implements CH340/CH341-style USB serial adapter support for the shared serial framework. It matches known vendor/product ids, installs CH340 serial operations, and uses vendor control requests to initialize the chip, configure baud rate, line control, modem control, and endpoint discovery.

`chinit()` reads the chip version, records the driver name and chip type, sends the serial-init vendor command, sets default 115200 8N1 parameters, applies them, and increments the device reference because the serial process keeps using it. `chsetbaud()` computes the CH340 divisor/factor encoding from the requested baud rate and writes it to the baud-rate register pair.

`chsendlines()` maps RTS/DTR state to modem-control bits and sends the inverted line mask expected by the device. `chmodemctl()` sets both DTR and RTS according to the requested state, updates framework modem state, and writes an additional modem register. `chsetparam()` combines baud, character size, parity, stop-bit selection, RX/TX enable bits, modem-control update, and final line-control register write.

The operations table uses the generic serial `findendpoints` helper for endpoint setup, while this file supplies CH340-specific init, parameter, send-lines, and modem-control logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ch340.c -->
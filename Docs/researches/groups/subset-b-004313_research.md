# Research: subset-b-004313

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-core.c

Purpose: This is the main Linux SocketCAN SPI driver body for the Microchip MCP2517FD, MCP2518FD, MCP251863, and generic MCP251xFD CAN/CAN-FD controllers. It owns probe/remove, runtime PM, chip detection, mode switching, bit timing, interrupt dispatch, error recovery, GPIO exposure, regulator/clock setup, and netdev open/stop integration.

Important APIs, types, and functions: `mcp251xfd_probe()` allocates and initializes the CAN netdev and `struct mcp251xfd_priv`; `mcp251xfd_register()` powers and soft-resets the chip, detects the concrete model, initializes ethtool/GPIO support, and registers the CAN device; `mcp251xfd_open()` and `mcp251xfd_stop()` connect SocketCAN lifecycle to power, rings, interrupts, workqueues, RX offload, and the transceiver regulator. `mcp251xfd_irq()` is the threaded IRQ loop and dispatches to handlers for RX, TEF, RX overflow, invalid messages, controller errors, mode changes, system errors, ECC, and SPI CRC errors. The file also defines device type data, bit timing constants, TDC limits, OF/SPI match tables, `net_device_ops`, GPIO callbacks, and runtime PM callbacks.

Control flow: Probe validates IRQ/clock/regulators, chooses PLL and SPI speed limits, initializes regmap and RX offload, then registers the device. Registration enables power/clock, performs wake/config/reset/clock setup, may reinitialize regmap after autodetecting the chip, checks optional RX_INT, and registers the CAN netdev. Open allocates rings, enables the transceiver, initializes timestamps, starts the chip, enables RX offload, creates TX fallback workqueue, requests the threaded IRQ, enables chip interrupts, and starts the TX queue. The IRQ loop first drains optional RX_INT fast-path RX, then repeatedly reads pending interrupt/status bits, acknowledges clearable bits before handling, processes data and error sources in an order that preserves mode/ECC recovery, and stops/dumps/disables on failures.

State and persistence behavior: Runtime state is in `mcp251xfd_priv`: CAN state, `flags`, saved bus error counters for bus-off, `regs_status`, ECC state/counter, ring state, timestamp counter, power resources, detected model/quirks, optional RX_INT/XSTBYEN/GPIO state, and SPI speed limits. No persistent storage is used; all hardware state is reconstructed during probe/open/runtime resume. Bus-off intentionally powers down/stops the controller while preserving `priv->bec` for later counter reads.

Dependencies and integration points: The file integrates Linux SPI, regmap, SocketCAN (`alloc_candev`, `register_candev`, `open_candev`, `can_change_state`, `can_bus_off`), `can_rx_offload`, ethtool helpers, GPIO chip API, regulators, clocks, runtime PM, device properties, OF/SPI IDs, and the split MCP251xFD helpers (`regmap`, `ring`, `rx`, `tef`, `tx`, `timestamp`, `ethtool`, `dump`, FIFO init).

Risks: Hardware errata dominate the risk surface: mode transitions can timeout or report invalid all-zero/all-one registers, CRC reads may fail during wake, ECC in TX RAM may require retransmit recovery, RX/TX MAB underflow/overflow can masquerade as multiple interrupts, and RX_INT may be electrically active after reset and must be disabled. The IRQ path mixes register acknowledgements, offload completion, and bus-off powerdown; ordering regressions could lose interrupts, process stale registers, or leave queues stuck.

Test signals: Useful checks include probe on each supported compatible string, runtime suspend/resume, CAN 2.0 and CAN-FD bit timing, loopback/listen-only modes, bus-off and restart, BERR reporting, RX/TX stress with and without coalescing, SPI CRC/ECC fault injection if available, RX_INT and XSTBYEN device-tree variants, GPIO controller mode conflicts, and devcoredump generation on forced IRQ/register failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-crc16.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-crc16.c

Purpose: Implements the MCP251xFD-specific CRC-16 used by CRC-enabled SPI register and RAM commands. The in-kernel generic CRC16 helper is not used because the controller expects a left-shift/table variant.

Important APIs, types, and functions: `mcp251xfd_crc16_compute()` computes a CRC over one contiguous buffer with initial value `0xffff`; `mcp251xfd_crc16_compute2()` computes a command+data CRC by continuing the first calculation over a second buffer. Internal helpers are `mcp251xfd_crc16_byte()` and `mcp251xfd_crc16()`, backed by `mcp251xfd_crc16_table`.

Control flow: Callers build the SPI command and payload, pass the command or command+payload bytes to these helpers, then append the returned big-endian CRC to the SPI transfer buffer. Reads use the same algorithm in `mcp251xfd-regmap.c` to verify the CRC returned by the controller.

State and persistence behavior: The file is stateless. The only static data is the constant 256-entry lookup table. No allocation, locking, hardware access, or persistent configuration is performed.

Dependencies and integration points: It includes `mcp251xfd.h` for prototypes and is consumed primarily by CRC regmap operations, TX object loading, and prebuilt ring write commands. It is part of the driver's SPI framing contract and must match device silicon behavior exactly.

Risks: Any table or shift-direction error would corrupt every CRC-protected SPI access. Because retry logic treats `-EBADMSG` specially, CRC bugs can look like intermittent hardware or wakeup failures. `compute2()` depends on callers passing exactly the bytes included in the chip-side CRC calculation.

Test signals: Validate with known-good MCP251xFD SPI command vectors, CRC read/write smoke tests on real hardware, and negative tests that flip payload or CRC bytes and confirm `-EBADMSG` paths in regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-crc16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.c

Purpose: Builds a binary devcoredump snapshot for MCP251xFD failure diagnosis. It records selected register ranges, controller RAM, and software TEF/RX/TX ring metadata so postmortem tools can correlate hardware state with driver ring state.

Important APIs, types, and functions: `mcp251xfd_dump()` is the exported entry. Internal types include `mcp251xfd_dump_iter`, register-space descriptors, and ring key/value descriptors. Helpers write object headers (`mcp251xfd_dump_header()`), read register spaces (`mcp251xfd_dump_registers()`), serialize ring metadata (`mcp251xfd_dump_ring()`, `mcp251xfd_dump_tef_ring()`, `mcp251xfd_dump_rx_ring()`, `mcp251xfd_dump_tx_ring()`), and append an END marker.

Control flow: The function computes the dump file size from register spaces, ring count, and object headers, allocates a vmalloc buffer, places headers first and payload after the header array, appends register and ring objects, then publishes the buffer through `dev_coredumpv()`. Register read failures skip that register space rather than aborting the dump.

State and persistence behavior: The dump captures transient hardware and in-memory driver state; persistence is delegated to the kernel devcoredump facility. The driver does not keep a copy after handing the buffer to `dev_coredumpv()`.

Dependencies and integration points: Compiled only when devcoredump support is enabled through the declaration in `mcp251xfd.h`. It depends on regmap, ring structures, dump object definitions from `mcp251xfd-dump.h`, and is called from core startup/IRQ failure paths.

Risks: Dump size depends on register/RAM ranges and RX ring count; allocation may fail under memory pressure, exactly when diagnostics are most valuable. The register reader uses `map_reg` while sizing uses `map_rx` value width, so regmap assumptions must remain consistent. Consumers must understand the little-endian object format.

Test signals: Force a controlled IRQ/start failure and verify a devcoredump appears with REG, TEF, RX, TX, and END objects; decode the ring keys and compare against live debug logs; test allocation failure behavior with fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.h

Purpose: Defines the on-wire/in-file binary object format used by MCP251xFD devcoredumps.

Important APIs, types, and functions: The header provides `MCP251XFD_DUMP_MAGIC`, `enum mcp251xfd_dump_object_type` for REG/TEF/RX/TX/END sections, `enum mcp251xfd_dump_object_ring_key` for serialized ring fields, `struct mcp251xfd_dump_object_header`, and `struct mcp251xfd_dump_object_reg`.

Control flow: There is no executable flow. `mcp251xfd-dump.c` uses the definitions to create a header table followed by payloads. Each object header points to payload offset and length, and an END object terminates parsing.

State and persistence behavior: The definitions encode transient state into little-endian fields. They are effectively an ABI for any userspace or debugging tool that parses MCP251xFD devcoredumps.

Dependencies and integration points: The header depends on kernel fixed-width endian types through the including context. It is private to the MCP251xFD driver but its format leaks to devcoredump consumers.

Risks: Reordering enum values or changing struct layout would break existing dump parsers. The END value is `-1`, stored as little-endian u32 by the writer, so parsers must treat it as the sentinel type rather than a small positive enum.

Test signals: Build-test with `CONFIG_DEV_COREDUMP=y`, generate a dump, and validate that object headers have the expected magic, offsets, lengths, object order, and ring key count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ethtool.c

Purpose: Exposes MCP251xFD ring sizing, IRQ coalescing, and hardware timestamp capability through ethtool. It translates user-visible ring/coalesce parameters into valid layouts for the controller's 2 KiB RAM.

Important APIs, types, and functions: `mcp251xfd_ethtool_init()` installs `mcp251xfd_ethtool_ops` and initializes default RX/TX object counts. `mcp251xfd_ring_get_ringparam()` and `mcp251xfd_ring_set_ringparam()` report and set RX/TX pending objects. `mcp251xfd_ring_get_coalesce()` and `mcp251xfd_ring_set_coalesce()` expose IRQ delay/frame coalescing. All layout decisions are delegated to `can_ram_get_layout()`.

Control flow: Getters compute layout maxima for current CAN/CAN-FD mode and return current fields from `priv`. Setters compute a normalized layout, reject changes that would affect active hardware while `netif_running()` is true, then store the normalized object/coalesce counts for the next open/reallocation.

State and persistence behavior: The file mutates only in-memory `mcp251xfd_priv` fields: RX object count, TX object count, coalescing object thresholds, and coalescing usec delays. Settings do not persist across driver unload or reboot unless userspace reapplies them.

Dependencies and integration points: Integrates with Linux ethtool ops, SocketCAN timestamp reporting (`can_ethtool_op_get_ts_info_hwts`), and the generic CAN RAM layout helper in `mcp251xfd-ram.c`. `mcp251xfd-ring.c` later consumes these normalized settings during ring allocation and initialization.

Risks: Incorrect normalization can overcommit RAM or create FIFO depths that violate hardware/coalescing assumptions. Runtime changes are intentionally rejected because live ring reallocation would race IRQ/TX/RX state. The ethtool convention for disabling coalescing is `usecs=0,max_frames=1`, which must be preserved.

Test signals: Run `ethtool -g/-G` and `ethtool -c/-C` in CAN and CAN-FD modes, confirm invalid oversized settings are clamped through layout calculations, verify live changes return `-EBUSY`, and test coalescing interrupts under RX/TX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.c

Purpose: Computes valid RX/TX object layouts for a CAN controller RAM shared between receive FIFOs, transmit FIFOs, and optional IRQ coalescing buffers.

Important APIs, types, and functions: `can_ram_get_layout()` is the exported helper. Internal helpers `can_ram_clamp()` and `can_ram_rounddown_pow_of_two()` enforce min/max limits, FIFO depth limits, power-of-two FIFO sizing, and reserved coalescing FIFO space.

Control flow: The helper first derives default TX and RX counts for the selected CAN or CAN-FD object sizes. It then derives maximum RX and TX counts while preserving the opposite direction's minimum. If user ring/coalesce parameters are supplied, it normalizes requested RX, computes optional RX coalescing, allocates remaining RAM to requested TX, computes optional TX coalescing, and fills `cur_*` and coalescing fields. Without user parameters, current values equal defaults and coalescing is disabled.

State and persistence behavior: Pure calculation; no global or hardware state is changed. Output is written into the caller-provided `struct can_ram_layout`.

Dependencies and integration points: Used by MCP251xFD ethtool setup and ring allocation. Inputs come from `struct can_ram_config`, `struct ethtool_ringparam`, and `struct ethtool_coalesce`.

Risks: RAM packing bugs can create overlapping FIFOs, under-sized FIFOs, or object counts that break ring masking assumptions. Coalescing reserves up to half a FIFO and changes the number of usable objects, so boundary cases around minimums and max_frames need careful coverage.

Test signals: Unit-style tests can feed representative CAN/CAN-FD object sizes and ethtool requests, then verify defaults, maxima, clamping, power-of-two rounding, coalescing disable convention, and no RAM overcommit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.h

Purpose: Declares generic data structures for laying out CAN controller RAM between RX and TX objects in CAN 2.0 and CAN-FD modes.

Important APIs, types, and functions: Defines `CAN_RAM_NUM_MAX`, `enum can_ram_mode`, `struct can_ram_obj_config`, `struct can_ram_config`, `struct can_ram_layout`, and the `can_ram_get_layout()` prototype.

Control flow: No executable flow. The structs describe object sizes, defaults, min/max counts, FIFO counts, FIFO depth constraints, total RAM size, and computed default/max/current layouts.

State and persistence behavior: The header defines transient configuration/calculation containers only. It does not encode persistence or hardware state by itself.

Dependencies and integration points: Includes `<linux/ethtool.h>` because layout calculation accepts ethtool ring and coalesce parameter structs. MCP251xFD publishes a concrete `mcp251xfd_ram_config` in `mcp251xfd-ring.c`, and ethtool/ring code uses this API.

Risks: Because the helper is generic-looking but currently tailored to controller FIFO constraints, future users must confirm the power-of-two and coalescing assumptions match their hardware. Changing field widths from `u8`/`u16` would affect maximum representable RAM/object counts.

Test signals: Compile coverage through MCP251xFD, static checks for struct initialization completeness, and layout tests that exercise both enum modes and maximum sentinel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-regmap.c

Purpose: Implements custom Linux regmap buses for MCP251xFD SPI access, with and without controller CRC framing, plus errata-specific write splitting and read retry behavior.

Important APIs, types, and functions: `mcp251xfd_regmap_init()` selects and initializes `map_reg` and `map_rx` based on quirk flags. Nocrc paths include gather/write/read/update-bits functions; CRC paths include CRC gather/write/read, `mcp251xfd_regmap_crc_read_check_crc()`, and retrying `mcp251xfd_regmap_crc_read()`. Static regmap configs and buses define endian handling, valid register ranges, value widths, and maximum raw transfer sizes.

Control flow: Initialization creates devm regmaps and DMA-safe buffers only for required modes. Register access through regmap builds SPI command buffers, handles half-duplex controllers with two transfers, and copies data between regmap buffers and caller memory. CRC reads retry up to `MCP251XFD_READ_CRC_RETRIES_MAX`, apply documented TBC and OSC wake exceptions, and return `-EBADMSG` on persistent CRC mismatch. Update-bits may read the original register depending on known register semantics.

State and persistence behavior: Persistent driver state is the selected regmap pointers and reusable RX/TX transfer buffers in `mcp251xfd_priv`. There is no regcache; all accesses hit hardware. Re-detection can destroy unused buffers and switch `map_reg`/`map_rx` from CRC to nocrc or vice versa.

Dependencies and integration points: Depends on SPI, regmap, unaligned endian helpers, the driver's CRC helper, quirk flags, and register constants. It is the main hardware access layer used by core, RX/TEF reads, ring setup, and diagnostics.

Risks: This file is highly sensitive to SPI framing, endian, DMA-safe buffer lifetime, and silicon errata. The IOCON write split avoids clearing LAT bits; removing it can break GPIO/transceiver pins. Wrong `reg_update_bits` read/skip decisions can clear write-one or FIFO control bits. CRC exception handling for TBC/OSC is intentionally narrow and should not mask real corruption elsewhere.

Test signals: Exercise reads/writes/update-bits through both CRC and nocrc modes, full-duplex and half-duplex SPI controllers, raw RAM reads, IOCON updates crossing byte `0xe06`, CRC mismatch retries, OSC wake reads, and fault injection for `-EBADMSG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ring.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ring.c

Purpose: Allocates and initializes the software rings and prebuilt SPI messages that back MCP251xFD TEF, RX FIFO, and TX FIFO operation.

Important APIs, types, and functions: `mcp251xfd_ring_alloc()`, `mcp251xfd_ring_init()`, and `mcp251xfd_ring_free()` are exported to core lifecycle code. Internal helpers prepare register write commands with optional CRC, initialize TEF, TX, and RX ring descriptors, initialize TX object SPI messages, and implement RX/TX coalescing hrtimer callbacks. The file also defines `mcp251xfd_ram_config`.

Control flow: Allocation recomputes object counts when CAN/CAN-FD mode changes, selects CAN or CAN-FD object sizes, allocates RX ring objects across up to three FIFOs, and sets up hrtimers. Initialization resets queue state, lays out TEF first, then RX rings, then TX ring in controller RAM, prebuilds IRQ enable, UINC, and RTS SPI transfers, logs layout, and validates RAM/coalescing constraints.

State and persistence behavior: Ring head/tail counters, object sizes/counts, FIFO numbers, base addresses, prebuilt SPI buffers/transfers, and coalescing timers live in `mcp251xfd_priv`. They are allocated on open and freed on stop; hardware FIFO state is reinitialized each start.

Dependencies and integration points: Uses the RAM layout helper, SPI transfer/message APIs, CRC helper, reg constants, ethtool-derived coalescing settings, and netdev queue helpers. RX/TEF/TX fast paths consume the ring descriptors and prebuilt transfer arrays.

Risks: Ring object counts are used as power-of-two masks; invalid counts can corrupt head/tail arithmetic. The `cs_change` handling is critical because an active chip select after the final transfer causes the controller to interpret later traffic as data. Coalescing changes interrupt enable bits dynamically and requires the first RX FIFO or half TEF buffer assumptions to hold.

Test signals: Verify RAM layout logs for CAN/CAN-FD, open/stop leaks, maximum/minimum ethtool ring values, coalescing frame/time modes, SPI transfer lengths in CRC/nocrc modes, and stress TX/RX wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-rx.c

Purpose: Handles MCP251xFD RX FIFO interrupts by reading hardware RX objects, converting them into SocketCAN SKBs, timestamping them, and advancing hardware/software FIFO tails.

Important APIs, types, and functions: `mcp251xfd_handle_rxif()` is called by the core IRQ handler. Helpers compute FIFO length (`mcp251xfd_get_rx_len()`), optionally sanity-check chip/software tail agreement, bulk-read objects from `map_rx`, convert hardware IDs/flags/DLC/data to `can_frame` or `canfd_frame`, queue SKBs to `can_rx_offload`, and issue batched UINC transfers.

Control flow: For each eligible RX ring, the code reads FIFOSTA, determines pending length using empty/full/head-tail logic, reads linear chunks from RAM at the current tail, processes each object, and advances the FIFO tail in one SPI message per chunk. If a stale timestamp is detected, it advances only the already accepted frames. RX coalescing restarts a timer to re-enable FIFO interrupts after a delay.

State and persistence behavior: Updates `rx_ring->head`, `rx_ring->tail`, and `rx_ring->last_valid`. SKB timestamps are derived from the shared timecounter. Hardware FIFO tail is advanced via prebuilt UINC SPI transfers.

Dependencies and integration points: Depends on `mcp251xfd-ring.c` ring descriptors, `mcp251xfd-timestamp.c` timecounter setup, `can_rx_offload_queue_timestamp()`, CAN/CAN-FD DLC helpers, and regmap RAM reads.

Risks: Erratum handling depends on monotonically increasing converted timestamps; timecounter resets or wrap mistakes could drop valid frames. FIFO length arithmetic relies on power-of-two object counts and an 8-bit shifted subtraction trick. Allocation failures drop frames but still need FIFO advancement to prevent stalls.

Test signals: RX standard/extended/RTR/CAN-FD/BRS/ESI frames, FIFO full/empty/wrap cases, RX coalescing, timestamp ordering across counter wrap, forced SKB allocation failure, and sanity mode tail mismatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tef.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tef.c

Purpose: Handles Transmit Event FIFO interrupts, completing transmitted echo SKBs, applying hardware timestamps, updating TX statistics, advancing TEF/TX tails, and waking the TX queue.

Important APIs, types, and functions: `mcp251xfd_handle_tefif()` is the exported IRQ handler. Helpers read TEF tail from chip, sanity-check tail state, compute TEF length from TX FIFO status, bulk-read TEF objects, process one object through sequence validation and echo completion, and clear ECC tracking after successful TEF handling.

Control flow: The handler determines how many TEF objects are pending, reads the pending range with wraparound support, validates each object's sequence number against the expected software TEF tail, completes echo SKBs via `can_rx_offload_get_echo_skb_queue_timestamp()`, and then batches UINC transfers to advance the hardware TEF tail. It updates `tx_ring->tail`, reports completed queue bytes/frames, wakes the netdev queue when space exists, and restarts TX coalescing timer when configured.

State and persistence behavior: Updates TEF ring head/tail, TX ring tail, netdev TX stats/queue accounting, echo SKB timestamps, and ECC state. State is volatile and reconstructed on open.

Dependencies and integration points: Works with TX object sequence numbers generated in `mcp251xfd-tx.c`, ring UINC transfer arrays from `mcp251xfd-ring.c`, hardware timestamp conversion helpers, and core IRQ handling.

Risks: TEF is the authoritative TX completion path; sequence mismatch handling prevents stale FIFO data from freeing the wrong echo SKB. Incorrect length inference can leave echo SKBs stuck or double-complete them. Queue wake requires a memory barrier so producers see the updated tail.

Test signals: TX completion under wraparound, full FIFO completion, sequence mismatch erratum path, TX coalescing, echo SKB timestamp correctness, sanity tail mismatch, and queue stop/wake stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-timestamp.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-timestamp.c

Purpose: Converts the MCP251xFD 32-bit hardware time base counter into stable nanosecond timestamps for RX, TX echo, and error SKBs.

Important APIs, types, and functions: `mcp251xfd_timestamp_init()` configures the `cyclecounter`; `mcp251xfd_timestamp_start()` initializes the `timecounter` and schedules periodic maintenance; `mcp251xfd_timestamp_stop()` cancels that work. Internal `mcp251xfd_timestamp_raw_read()` reads TBC, and `mcp251xfd_timestamp_work()` periodically calls `timecounter_read()`.

Control flow: On open/start, core initializes and starts the timecounter. The delayed work runs every `MCP251XFD_TIMESTAMP_WORK_DELAY_SEC`, reads the timecounter before half-wrap can occur, and reschedules itself. RX/TEF/core error paths convert raw hardware timestamps through `timecounter_cyc2time()`.

State and persistence behavior: Maintains volatile `cyclecounter`, `timecounter`, and delayed work in `mcp251xfd_priv`. It is started on chip start and stopped on stop/failure. No persistent clock state survives close.

Dependencies and integration points: Uses Linux clocksource/timecounter helpers, workqueue delayed work, and `mcp251xfd_get_timestamp_raw()` from the shared header. The core sets TBC prescaler and starts/stops the worker.

Risks: The periodic interval must remain below half the 32-bit counter wrap at maximum system clock; the header has a static assertion for this. Read errors are logged but return zero, so repeated SPI failures can make timestamps inaccurate while traffic continues.

Test signals: Timestamp monotonicity across long runtime, RX/TX/error SKB hwtstamp presence, stop/open work cancellation, forced TBC read error logging, and validation near counter wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tx.c

Purpose: Implements the MCP251xFD transmit path from SocketCAN SKB to controller TX RAM load and FIFO request-to-send.

Important APIs, types, and functions: `mcp251xfd_start_xmit()` is the netdev transmit entry; `mcp251xfd_tx_obj_write_sync()` is the workqueue fallback for busy SPI controllers. Helpers pick the next TX object, convert SKB fields into raw hardware ID/flags/data, compute optional CRC and transfer length, detect TX ring fullness, and drop/rollback failed submissions.

Control flow: Start-xmit rejects invalid CAN SKBs, checks ring/free work state, builds the next TX object with sequence number equal to software head, stops the queue if the FIFO becomes full, stores echo SKB and queue accounting, then submits the prebuilt SPI message asynchronously. If SPI returns `-EBUSY`, it queues synchronous work; other errors roll back head, free echo SKB, update drop stats, and wake the queue.

State and persistence behavior: Mutates `tx_ring->head`, `priv->tx_work_obj`, echo SKB slots, and netdev TX queue accounting. Actual completion and tail advancement happen in the TEF handler, not here.

Dependencies and integration points: Depends on CAN/CAN-FD SKB helpers, SPI async/sync APIs, CRC helper, ring prebuilt messages, and TEF sequence validation. It is registered as `.ndo_start_xmit` by core.

Risks: TX and TEF must agree on sequence masks; mismatches can stall or free wrong SKBs. The async-to-workqueue fallback has a single `tx_work_obj`, so the queue is held busy while work is pending. Padding/sanitization and CRC length calculations must exactly match object length and RAM command semantics.

Test signals: Standard/extended/RTR/CAN-FD/BRS/ESI transmit, full FIFO queue stop, TEF wakeup, SPI `-EBUSY` fallback, SPI hard error rollback, echo SKB accounting, and CAN FD length sanitization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd.h

Purpose: Central private header for the MCP251xFD driver. It defines register maps, bit masks, SPI command formats, hardware object layouts, ring/private state structures, inline helpers, quirk flags, model IDs, and cross-file function prototypes.

Important APIs, types, and functions: Key types include hardware TEF/TX/RX objects, SPI command buffers, regmap transfer buffers, TEF/TX/RX ring structs, ECC/status structs, `enum mcp251xfd_model`, `struct mcp251xfd_devtype_data`, and `struct mcp251xfd_priv`. Inline helpers build SPI commands, compute RAM addresses, convert timestamps to SKB hwtstamps, inspect model/mode state, and compute ring head/tail/free/linear lengths. Prototypes expose chip FIFO, CRC, ethtool, regmap, ring, RX, TEF, timestamp, dump, and TX functions.

Control flow: No standalone flow, but the header shapes every driver path. Core sets up `mcp251xfd_priv`; regmap uses command buffer helpers; ring/RX/TEF/TX use address and ring arithmetic helpers; timestamp users call the SKB timestamp helpers.

State and persistence behavior: `mcp251xfd_priv` holds all volatile driver state: CAN core/offload/netdev, selected regmaps and buffers, SPI device/speeds, rings, workqueue, flags, coalescing, ECC/status, timestamp counters, GPIO/clock/regulator handles, devtype quirks, saved bus error counters, and optional GPIO chip.

Dependencies and integration points: Includes Linux CAN, netdevice, regmap, SPI, GPIO, regulator, timecounter, and workqueue APIs. It is the internal contract among all MCP251xFD compilation units and also gates devcoredump availability with `CONFIG_DEV_COREDUMP`.

Risks: Register bit definitions and object layouts must match silicon exactly. Ring arithmetic assumes object counts are powers of two. Command buffer unions are cacheline-aligned and packed for SPI/DMA behavior; accidental layout changes can break hardware access. Quirk bits control CRC/ECC/half-duplex behavior across the driver.

Test signals: Build with sparse/packed warnings, run hardware smoke tests for all supported models/quirks, verify CRC/nocrc and CAN/CAN-FD object layouts, and exercise timestamp/ring helpers through RX/TX traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sun4i_can.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sun4i_can.c

Purpose: Platform SocketCAN driver for Allwinner SUN4I/SUN7I/R40/D1 CAN controllers using direct MMIO registers.

Important APIs, types, and functions: `struct sun4ican_priv` stores CAN core state, MMIO base, clock, optional reset control, command-register lock, and acceptance-filter offset. Netdev operations are `sun4ican_open()`, `sun4ican_close()`, and `sun4ican_start_xmit()`. Core helpers handle reset/normal mode transitions, bit timing, start/stop, error counters, RX parsing, error reporting, and `sun4i_can_interrupt()`. Probe/remove wire platform resources, quirks, CAN settings, and OF match data.

Control flow: Probe gets quirk data, optional reset, clock, IRQ, MMIO resource, allocates a one-echo-slot CAN netdev, initializes bit timing and ctrlmode support, and registers the device. Open requests IRQ, deasserts reset, enables clock, starts the controller, and starts the queue. Start enters reset mode, accepts all filters, clears counters, enables interrupts, applies loopback/listen-only and bit timing, then enters normal mode. The ISR loops with a max interrupt count, handles TX complete, drains RX buffers while ready, reports error conditions, clears interrupts, and returns handled status.

State and persistence behavior: Runtime state is register state plus `can.state`, clock/reset enablement, and a spinlock protecting command register writes. There is no persistent configuration beyond device-tree compatible/clock/reset data and userspace CAN settings.

Dependencies and integration points: Uses platform driver APIs, OF match data, clocks, resets, MMIO `readl/writel`, SocketCAN device helpers, CAN error SKBs, ethtool timestamp info, netdev echo SKB, and Linux IRQ handling.

Risks: Mode transition loops test the locally written value before rereading, then validate after the loop; hardware timing regressions can manifest as timeouts. Overrun recovery resets the controller and returns to normal mode inside error handling. The interrupt loop has a cap to prevent livelock but may leave pending interrupts if traffic/error storms exceed it.

Test signals: Probe each compatible quirk including D1 acceptance-filter offset, open/close reset/clock sequencing, standard and extended TX/RX, RTR, loopback/listen-only/3-samples, bus error and bus-off reporting, RX overrun recovery, and interrupt storm cap logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sun4i_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ti_hecc.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/ti_hecc.c

Purpose: Platform SocketCAN driver for TI HECC (High End CAN Controller) hardware. It manages HECC registers, mailbox RAM, timestamped RX offload, prioritized TX mailboxes, transceiver regulator, clocking, and suspend/resume.

Important APIs, types, and functions: `struct ti_hecc_priv` contains CAN core, RX offload, MMIO bases, clock, mailbox spinlock, TX head/tail priority counters, and transceiver regulator. Key routines include `ti_hecc_probe/remove`, `ti_hecc_open/close`, `ti_hecc_start/stop/reset`, `ti_hecc_xmit`, `ti_hecc_interrupt`, `ti_hecc_mailbox_read`, error/state helpers, and PM callbacks. Helper accessors wrap HECC and mailbox register reads/writes.

Control flow: Probe maps named resources (`hecc`, `hecc-ram`, `mbx`), gets IRQ/clock/regulator, initializes RX offload over RX mailbox range, and registers the CAN device. Open requests IRQ, enables transceiver, opens CAN core, starts hardware, enables offload, and starts queue. Start resets/configures timing, initializes TX counters, configures RX mailboxes with masks and overwrite protection, enables TX mailbox interrupts, and routes global interrupts. TX fills the current mailbox, stores echo SKB, decrements priority/head, enables the mailbox, and sets transmit request. IRQ handles bus errors/state changes, TX acknowledgements, RX pending mailbox offload, clears interrupt flags, and finishes RX offload.

State and persistence behavior: TX priority/head/tail counters encode both mailbox index and priority; RX state is in hardware mailboxes plus `can_rx_offload`. The driver keeps no persistent settings. Suspend powers down HECC and clock, resume clears powerdown and restarts queue attachment if needed.

Dependencies and integration points: Uses platform/OF APIs, named MMIO resources, clocks, regulators, SocketCAN, `can_rx_offload_add_timestamp`, netdev echo SKBs, IRQs, and optional PM.

Risks: Mailbox enable (`CANME`) changes require spinlock protection because TX and RX/IRQ paths can race. RX overflow detection intentionally leaves the last mailbox overwrite-unprotected and drops inconsistent frames. The TX priority counter wrap rules are subtle; queue wake logic must match head/tail encoding. Bus-off disables interrupts before handing state to CAN core.

Test signals: TX priority/mailbox wrap, RX timestamp ordering, RX overflow/drop path on last mailbox, bus error/passive/warning/off transitions, transceiver regulator failures, `ti,use-hecc1int` interrupt routing, suspend/resume while running, and shared IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ti_hecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/Kconfig

Purpose: Declares Kconfig options for USB-attached CAN interface drivers under `drivers/net/can/usb`.

Important APIs, types, and functions: The file is declarative Kconfig, not C. It opens `menu "CAN USB interfaces"` with `depends on USB`, then defines tristate symbols for 8devices, EMS, esd, ETAS ES58X, Fintek F81604, GS/candleLight, Kvaser, Microchip CAN BUS Analyzer, Nuvoton NCT6694, PEAK, and Theobroma UCAN drivers. Some entries select dependencies such as `CRC16`, `NET_DEVLINK`, or `CAN_RX_OFFLOAD`, and NCT6694 depends on `MFD_NCT6694`.

Control flow: During kernel configuration, enabled symbols drive compilation in the sibling Makefile. Help text documents supported hardware and module names for users and distributors.

State and persistence behavior: Configuration choices persist in the kernel `.config`, not at runtime. Tristate values determine built-in, module, or disabled build products.

Dependencies and integration points: Integrates with the top-level CAN/USB build system and with driver directories such as `etas_es58x/`, `kvaser_usb/`, and `peak_usb/`. The menu-level USB dependency prevents exposing these drivers without USB support.

Risks: Missing `select` or `depends on` lines can produce link/build failures or unusable options. Help text and module names can drift from Makefile object names. Broad `select` dependencies should be reviewed for Kconfig best practices.

Test signals: Run `make menuconfig`/`olddefconfig` with USB enabled and disabled, build each option as `m` and `y`, verify selected dependencies appear, and compare module names against Makefile outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/Makefile

Purpose: Maps USB CAN Kconfig symbols to the object files or subdirectories built by Kbuild.

Important APIs, types, and functions: Uses standard Kbuild `obj-$(CONFIG_...) += ...` assignments for `usb_8dev.o`, `ems_usb.o`, `esd_usb.o`, `etas_es58x/`, `f81604.o`, `gs_usb.o`, `kvaser_usb/`, `mcba_usb.o`, `nct6694_canfd.o`, `peak_usb/`, and `ucan.o`.

Control flow: Kbuild evaluates each `CONFIG_CAN_*` symbol and includes the corresponding object or subdirectory in the built-in or module build according to the symbol value.

State and persistence behavior: No runtime state. Build outputs are controlled by the persisted kernel configuration.

Dependencies and integration points: Directly paired with `usb/Kconfig`; subdirectory entries rely on nested Kbuild files in the referenced directories. The parent CAN Makefile includes this directory when USB CAN support is in scope.

Risks: Symbol/object mismatches break builds or silently omit selected drivers. Subdirectory entries require the nested directory to provide its own Makefile. License header uses GPL-2.0 while Kconfig uses GPL-2.0-only, which is common but worth preserving intentionally.

Test signals: Build each USB CAN symbol as module and built-in, run `make M=drivers/net/can/usb`, and compare generated modules with Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/Makefile -->

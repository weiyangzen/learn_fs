# subset-b-006385 ASI HPI PCI backend research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6000.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6000.c

## Purpose

`hpi6000.c` is the HPI backend for AudioScience ASI5100/5200/6100/6200 PCI adapters built around TI C6711/C6713 DSPs behind a PCI2040 HPI bridge. It exports `HPI_6000()` as the message entry point used by the higher HPI manager, creates and tears down adapter objects, bootloads DSP firmware, sends command/response messages over DSP mailbox memory, transfers stream payloads through the HPI data window, and maintains an optional DSP-provided mixer control cache.

## Important APIs, types, and functions

The file-local `struct dsp_obj` records the HPI control/address/data MMIO windows for one DSP, the cached DSP-side control-cache location, and its parent adapter. `struct hpi_hw_obj` owns PCI2040 CSR/MMIO bases, up to two `dsp_obj` instances, cached message/response buffer addresses, PCI2040 error accounting, and the local `hpi_control_cache_single` array used by `hpicmn.c`.

The public API is `HPI_6000(struct hpi_message *phm, struct hpi_response *phr)`. It dispatches subsystem, adapter, control, outstream, instream, and fallback hardware messages. Important helpers are `subsys_create_adapter()`, `create_adapter_obj()`, `delete_adapter_obj()`, `hpi6000_adapter_boot_load_dsp()`, `hpi6000_message_response_sequence()`, `hpi6000_send_data()`, `hpi6000_get_data()`, `hpi6000_update_control_cache()`, `hpi6000_dsp_block_write32()`, `hpi6000_dsp_block_read32()`, and low-level `hpi_write_word()`, `hpi_read_word()`, `hpi_write_block()`, and `hpi_read_block()`.

## Control flow

`HPI_6000()` validates the adapter for non-subsystem messages, refuses normal traffic after repeated DSP crashes, initializes a default response, then routes by message object. Adapter creation allocates `hpi_hw_obj`, maps BAR0/BAR1 resources into PCI2040 CSR and DSP HPI windows, bootloads DSP firmware, asks DSP0 and optionally DSP1 for adapter information, initializes the control cache if DSP mailbox fields advertise one, and registers the adapter through `hpi_add_adapter()`.

Bootload flow resets the PCI2040 and DSPs, configures endian/data width, validates HPI register access, programs PLL and EMIF registers, tests internal and SDRAM memory, opens firmware via `hpi_dsp_code_open()`, writes firmware blocks into DSP memory, verifies them, writes mailbox metadata such as DSP number and adapter info, starts the DSP by toggling HPI control, waits for a nonzero host command acknowledgement, and performs PLD read/write checks for relevant families.

Runtime hardware messages enter `hw_message()`, choose DSP0 or DSP1 for multi-DSP adapters, reject inter-DSP stream groups, lock the DSP with `hpios_dsplock_lock()`, run `hpi6000_message_response_sequence()`, and then perform secondary stream payload movement for read/write functions. The command/response sequence waits for idle, writes the message to the DSP message buffer, commands `HPI_HIF_GET_RESP`, waits for the DSP acknowledgement, reads the response length and response data, returns the DSP interface to idle, and validates the response header.

## State and persistence behavior

Persistent driver state lives in `struct hpi_adapter_obj` registered by `hpicmn.c`, the private `hpi_hw_obj`, cached DSP buffer addresses, cached control-cache address/length, `dsp_crashed`, `has_control_cache`, and global PCI read/write assert counters. Hardware state persists in PCI2040 registers, DSP memory, mailbox fields, PLL/EMIF configuration, PLD registers, and loaded firmware. Control cache reads are staged in host memory and synchronized from DSP only when `control_cache_is_dirty` is set. Set-state messages update the host cache from the response via `hpi_cmn_control_cache_sync_to_msg()`.

## Dependencies and integration points

This backend depends on the common HPI ABI in `hpi_internal.h`, response initialization from `hpimsginit.h`, logging from `hpidebug.h`, mailbox layout from `hpi6000.h`, firmware iteration from `hpidspcd.c`, and adapter/cache helpers from `hpicmn.c`. It uses OS hooks from `hpios.h` for locking and microsecond delays, kernel MMIO helpers (`ioread32`, `iowrite32`, repeated I/O), allocation helpers, and PCI device subsystem IDs. It integrates with the ALSA asihpi probe path through `HPI_6000` and with firmware files selected by adapter family.

## Risks and test signals

Risks include tight polling loops with large timeouts, implicit 32-bit alignment of message and stream data, silent low-level read failures returning zero, fragile PCI2040 error recovery, firmware/driver ABI mismatch, multi-DSP routing mistakes, stale cached DSP buffer addresses after a firmware crash, and cache validity depending on DSP-maintained dirty flags. Test signals include successful adapter create/delete, bootload logs, `HPI_ADAPTER_GET_INFO`, DSP assert reads, repeated control cache hits and misses, outstream write and instream read payload transfers, multi-DSP stream routing/group rejection, suspend or device reset recovery, and fault injection for firmware absence, invalid subsystem IDs, timeout paths, and response-size validation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6000.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6000.h

## Purpose

`hpi6000.h` defines the shared host/DSP mailbox contract for the ASI6000-family HPI backend. It is included by `hpi6000.c` and must match the DSP firmware view of the host interface structure.

## Important APIs, types, and functions

The central type is `struct hpi_hif_6000`, whose fields are the DSP mailbox words addressed through `HPI_HIF_ADDR()`: host command, DSP acknowledgement, transfer address and length, message and response buffer addresses, DSP number, packed adapter information, control-cache dirty flag, control-cache address, control-cache size, and control count. The header also defines `HPI_NMIXER_CONTROLS` as 200 for this backend, adapter-info pack/extract macros, and host interface command values such as `HPI_HIF_IDLE`, `HPI_HIF_GET_RESP`, `HPI_HIF_SEND_DATA`, `HPI_HIF_GET_DATA`, `HPI_HIF_SEND_DONE`, and `HPI_HIF_RESET`.

## Control flow

There is no runtime control flow in the header. `hpi6000.c` expands the offsets to read and write mailbox words during boot, message/response exchange, stream payload transfer, and control-cache refresh. The command constants encode the expected state transitions between host and DSP.

## State and persistence behavior

The header stores no state, but it defines state that persists in DSP memory while firmware is running. If the host and DSP disagree about this structure layout, commands, response addresses, control-cache metadata, or adapter-info bit packing, the backend can hang, report invalid responses, or corrupt stream/control data until reset and reload.

## Dependencies and integration points

The header depends on `u32` types from the surrounding kernel/HPI headers and on its inclusion next to `offsetof()` use in `hpi6000.c`. It integrates directly with DSP firmware, the HPI6000 backend, and common HPI control-cache parsing.

## Risks and test signals

Risks are ABI drift with firmware, incorrect command values, changing `HPI_NMIXER_CONTROLS` without matching host memory sizing, and mailbox offset changes that break existing DSP binaries. Test signals are bootload completion, mailbox idle/get-response transitions, stream data transfer, adapter info extraction for one- and two-DSP cards, and control-cache enablement from nonzero cache size/count.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6205.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6205.c

## Purpose

`hpi6205.c` is the HPI backend for AudioScience PCI/PCIe adapters based on a TI TMS320C6205 PCI bus-mastering DSP, often paired with a C6713 floating-point DSP. It exports `HPI_6205()`, bootloads one or two DSP images, manages a DMA-visible bus-master mailbox, supports DSP-driven control caching, implements background bus-master stream buffers, and routes HPI messages to firmware.

## Important APIs, types, and functions

The local `struct hpi_hw_obj` owns C6205 PCI registers (`prHSR`, `prHDCR`, `prDSPP`), the current DSP page, locked DMA memory for `struct bus_master_interface`, stream host-buffer handles and sizes, outstream reset flags, a locked control-cache buffer, and the parsed cache descriptor. Public entry is `HPI_6205()`, with `_HPI_6205()` doing object dispatch once an adapter is resolved.

Key functions include `subsys_create_adapter()`, `create_adapter_obj()`, `adapter_boot_load_dsp()`, `message_response_sequence()`, `hpi6205_transfer_data()`, `wait_dsp_ack()`, `send_dsp_command()`, `adapter_irq_query_and_clear()`, stream host-buffer allocate/get/free handlers, `outstream_write()`, `instream_read()`, `outstream_get_info()`, `instream_get_info()`, and bootloader helpers such as `boot_loader_read_mem32()`, `boot_loader_write_mem32()`, `boot_loader_config_emif()`, `boot_loader_test_internal_memory()`, `boot_loader_test_external_memory()`, and `boot_loader_test_pld()`.

## Control flow

The intended runtime path is adapter-indexed: `HPI_6205()` rejects subsystem messages in this tree version, looks up an adapter, and calls `_HPI_6205()`. Dispatch then routes adapter, control, outstream, instream, or generic messages. Control get-state tries the DMA-updated cache first, with a special meter-peak fallback that returns `HPI_ERROR_CONTROL_CACHING` if hardware fallback succeeds after a cache miss. Set-state synchronizes cached control fields after successful firmware handling.

Adapter creation initializes stream reset flags, maps C6205 BAR1 host status/control/page registers, allocates the bus-master interface as consistent DMA memory, bootloads DSPs, waits for the DSP to signal reset through the DMA mailbox, optionally allocates and grants a DMA control-cache buffer, sends idle, obtains adapter info through a message/response exchange, sets interrupt and host-buffer-status integration pointers, and registers the adapter.

Message transport serializes with `hpios_dsplock_lock()`. `message_response_sequence()` verifies the message fits the mailbox, waits for idle, copies the message into `interface->u.message_buffer`, commands `H620_HIF_GET_RESP`, waits for the DSP to DMA the acknowledgement and response, copies the response out with buffer-size checks, returns the DSP to idle, and validates the response header. For non-background stream transfers, `hw_message()` then calls `hpi6205_transfer_data()` to chunk payloads through the 16 KiB mailbox data area.

Background stream-buffer flow is separate. Host-buffer allocation rounds sizes to powers of two, allocates locked memory or accepts external phases, initializes a DMA-visible `hpi_hostbuffer_status`, grants/revokes the buffer through firmware messages, and returns buffer/status pointers for ALSA-side users. `outstream_write()` copies into the ring buffer and advances `host_index`; `instream_read()` copies out and advances `host_index`; firmware advances `dsp_index` and sample counters.

## State and persistence behavior

Persistent state includes the adapter registry entry, private hardware object, locked DMA areas, stream buffer sizes and handles, DMA-visible `bus_master_interface` fields, control-cache memory and pointer index, `dsp_crashed`, and outstream format/reset flags. Hardware state persists in C6205 HSR/HDCR/DSPP registers, EMIF/PLL registers, C6713 HPI registers, PLD registers, firmware images in DSP memory, and firmware-maintained host-buffer status. Memory barriers (`rmb()`/`wmb()`) are essential because the DSP and host communicate by DMA.

## Dependencies and integration points

The backend depends on `hpi_internal.h` for message/response, stream, buffer, and cache ABI; `hpi6205.h` for the bus-master interface layout; `hpidspcd.c` for firmware loading; `hpicmn.c` for adapter registration and cache parsing; `hpidebug.h`; OS locked-memory and delay hooks from `hpios.h`; PCI resources; Linux firmware loading; and kernel MMIO/DMA primitives. It exposes `irq_query_and_clear` and host-buffer status pointers through `hpi_adapter_obj` for upper asihpi layers.

## Risks and test signals

Risks include the apparent subsystem-message rejection in `HPI_6205()` if no outer layer handles create-adapter differently, DMA coherency mistakes, failure to free locked buffers across partial allocation phases, unchecked external buffer addresses, power-of-two assumptions in ring indexing, wraparound arithmetic on unbounded host/DSP indexes, firmware/header ABI drift, response mailbox size mismatch, bootloader register timing fragility, and a suspicious verify loop that sets `err = 0` on mismatch. Test signals include firmware request names for each adapter family, successful reset acknowledgement, `HPI_ADAPTER_GET_INFO`, control cache DMA population, interrupt query/clear, background playback/capture ring wrap tests, host-buffer allocate/grant/revoke/free phases, fallback mailbox payload transfers, adapter close idle wait, repeated crash counter behavior, and boot failures for EEPROM, DSPP, EMIF, memory, PLD, and firmware-version errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6205.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6205.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6205.h

## Purpose

`hpi6205.h` defines the host/DSP bus-master interface used by the C6205 backend. Unlike the HPI6000 PIO mailbox, this ABI lives in host locked memory and is accessed by the DSP through PCI bus mastering.

## Important APIs, types, and functions

The header defines H620 host-interface command and acknowledgement states (`H620_HIF_RESET`, `H620_HIF_IDLE`, `H620_HIF_GET_RESP`, `H620_HIF_DATA_DONE`, `H620_HIF_SEND_DATA`, `H620_HIF_GET_DATA`, and `H620_HIF_UNKNOWN`), stream/cache sizing constants, and several ABI structs. `struct controlcache_6205` communicates the number, physical address, and byte size of a host control-cache buffer. `struct async_event_buffer_6205` supplies a physical address and FIFO metadata for async events. `struct message_buffer_6205` and `struct response_buffer_6205` wrap common HPI messages/responses with extra data space. `union buffer_6205` supplies a 16 KiB transfer window. `struct bus_master_interface` is the top-level DMA mailbox containing command, ack, transfer size, transfer buffer, control-cache descriptor, async event buffer, and instream/outstream host-buffer status arrays.

## Control flow

There is no direct control flow. The `hpi6205.c` runtime writes `host_cmd`, uses memory barriers, interrupts the DSP, and polls `dsp_ack`. Firmware writes responses, transfer payloads, cache content, async FIFO state, and stream status back into this layout.

## State and persistence behavior

The header defines shared volatile state in consistent DMA memory. Fields persist for the life of an adapter object and are reused across command/response, stream transfer, control-cache, async, and background-buffer operations. Because both sides mutate the same memory, ordering and structure layout are part of the hardware/firmware ABI.

## Dependencies and integration points

It includes `hpi_internal.h` for `struct hpi_message`, `struct hpi_response`, `struct hpi_fifo_buffer`, and `struct hpi_hostbuffer_status`. It integrates with C6205 firmware, the Linux locked-DMA allocation wrappers, and upper stream code that consumes returned host-buffer status pointers.

## Risks and test signals

Risks include ABI drift with firmware, cache/status arrays exceeding `HPI_MAX_STREAMS` assumptions, command value mismatches, insufficient transfer-buffer size for future message formats, and missing barriers around DMA-visible fields. Test signals are reset-to-idle transitions, command/response traffic, 16 KiB chunked data transfer, DMA control cache population, async FIFO behavior, and instream/outstream host-buffer status updates under sustained playback/capture.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi6205.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_internal.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_internal.h

## Purpose

`hpi_internal.h` is the internal ABI hub for the AudioScience HPI driver. It defines OS integration hooks, bus/vendor IDs, message types, object types, function IDs, control attributes, message and response payload layouts, control-cache structures, host-buffer status structures, and internal entry-point declarations used by the asihpi backends.

## Important APIs, types, and functions

The header declares locked DMA memory operations (`hpios_locked_mem_alloc/free/get_phys_addr/get_virt_addr/valid`) and delay hooks, `hpi_handler_func`, compile-time assertion support, HPI bus/subsystem/buffer enums, adapter family macros, all low-level object/function IDs, and common structs such as `hpi_pci`, `hpi_resource`, `hpi_msg_format`, `hpi_msg_data`, `hpi_buffer`, `hpi_hostbuffer_status`, `hpi_message`, and `hpi_response`.

It also defines object-sized message/response tables, v1 payload buffer limits for network transport, adapter debug/Cobranet message formats, handle conversion declarations, the main `hpi_send_recv()` declaration, legacy compatibility declarations, and backend declarations `HPI_6000` and `HPI_6205`. Control-cache ABI types include `hpi_control_cache_info`, per-control cache structs for volume, meter, mux, tuner, AES3, tone/silence detector, sample clock, microphone, PAD strings, and `hpi_fifo_buffer`.

## Control flow

The header itself has no executable control flow, but it dictates runtime dispatch. Function IDs are constructed from object ID times `HPI_OBJ_FUNCTION_SPACING` plus an index; backends switch on `phm->type`, `phm->object`, and `phm->function`. Message and response unions determine how each backend copies payloads to firmware and interprets returned bytes. Buffer command enums define the multi-phase host-buffer allocate/grant/revoke/free workflow used by `hpi6205.c`.

## State and persistence behavior

No storage is allocated here, but the structures define persistent state in adapter objects, HPI messages, DSP responses, DMA host buffers, network packets, and DSP/host control caches. Layout stability is critical because firmware, compatibility ioctls, and possibly 32-bit compatibility paths depend on exact field order, size, and alignment.

## Dependencies and integration points

It includes public `hpi.h` and OS-specific `hpios.h`, and is included by all researched backend/common files. It integrates the Linux PCI/DMA layer, ALSA-facing HPI entry points, firmware DSP protocols, network/Cobranet packet paths, and legacy binary compatibility declarations.

## Risks and test signals

Risks include ABI-breaking structure changes, enum drift from firmware, endian/alignment assumptions, stale compatibility fields, function-count mismatches, payload buffer overflow, and duplicated compile-time-assert definitions across headers. Test signals include compile-time size assertions, successful message initialization and validation, 32-bit compat builds, firmware command/response compatibility, host-buffer status correctness, control-cache parsing across all control types, and broad hardware smoke tests for adapter, stream, mixer, GPIO, async event, and profile objects.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_version.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_version.h

## Purpose

`hpi_version.h` centralizes the HPI driver and library version constants used by the AudioScience driver and firmware loader.

## Important APIs, types, and functions

It defines `HPI_VER` as `HPI_VERSION_CONSTRUCTOR(4, 14, 3)`, `HPI_VER_STRING` as `"4.14.03"`, `HPI_LIB_VER` as `HPI_VERSION_CONSTRUCTOR(10, 4, 0)`, plus helpers `HPI_VERSION_CONSTRUCTOR(maj, min, r)`, `HPI_VER_MAJOR(v)`, `HPI_VER_MINOR(v)`, and `HPI_VER_RELEASE(v)`.

## Control flow

There is no runtime control flow. Consumers expand these macros to compare or display versions. `hpidspcd.c` uses the major version to reject incompatible firmware images and logs a warning when the full DSP image version differs from `HPI_VER`.

## State and persistence behavior

The header stores no mutable state. Version values are compile-time constants embedded into the driver. They become compatibility gates against firmware metadata and can affect whether an adapter boots.

## Dependencies and integration points

The file is included by the DSP-code loader and can be used by HPI API/reporting code. It must stay aligned with firmware file headers generated for `asihpi/dsp*.bin` images and with documented library API versions.

## Risks and test signals

Risks include forgetting to update the version when host/DSP protocol changes, accidental octal literals if leading zeroes are used, and major-version mismatches that prevent firmware loading. Test signals are firmware load acceptance/rejection, mismatch warnings for non-identical minor/release versions, version reporting through subsystem APIs, and build checks for macro extraction.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.c

## Purpose

`hpicmn.c` implements shared HPI backend services: adapter registry management, response-header validation, subsystem common messages, control-cache allocation/parsing, cache hit resolution for common control attributes, and cache synchronization after control set operations.

## Important APIs, types, and functions

The file-local `struct hpi_adapters_list` stores a spinlock, fixed `HPI_MAX_ADAPTERS` array of `hpi_adapter_obj`, and adapter count. Exported functions are `hpi_validate_response()`, `hpi_add_adapter()`, `hpi_delete_adapter()`, `hpi_find_adapter()`, `hpi_check_control_cache_single()`, `hpi_check_control_cache()`, `hpi_cmn_control_cache_sync_to_msg_single()`, `hpi_cmn_control_cache_sync_to_msg()`, `hpi_alloc_control_cache()`, `hpi_free_control_cache()`, and `HPI_COMMON()`.

Important internals are `wipe_adapter_list()`, `subsys_get_adapter()`, `control_cache_alloc_check()`, `find_control()`, and PAD string offset metadata. `control_cache_alloc_check()` lazily walks the DSP-provided cache blob, validates control indexes and entry sizes, and builds `p_info[control_index]` pointers for direct lookup.

## Control flow

Adapter lifecycle flow is guarded by `hpios_alistlock_lock()`. `hpi_add_adapter()` rejects out-of-range indexes, relocates duplicate adapter indexes to the highest free slot, copies the temporary object into the global array, initializes its DSP lock, and increments the count. `hpi_delete_adapter()` clears the registered slot and decrements the count. `hpi_find_adapter()` returns a registered adapter pointer if the index is valid and nonempty.

Control-cache lookup starts with `hpi_check_control_cache()`, which calls `find_control()`. The first lookup initializes cache lookup pointers by scanning the DSP cache blob; later lookups use `p_info` directly. `hpi_check_control_cache_single()` handles common cached control types and attributes, fills the response union, sets response header fields on a hit, and reports invalid attributes for known-but-invalid cached values. Set-state synchronization updates mutable cached values only when the DSP response succeeded.

`HPI_COMMON()` handles subsystem request messages. Driver load wipes and initializes the adapter list; get-adapter enumerates the nth registered adapter; get-num-adapters returns the count; open/close/unload are accepted as no-ops.

## State and persistence behavior

Persistent state is the static adapter list and each allocated `hpi_control_cache` object. Cache objects persist a pointer array, the raw DSP cache buffer pointer supplied by the backend, cache size, control count, adapter index, and an `init` count used as a lazy initialization flag. Cached controls mirror DSP state and are updated from firmware DMA/PIO refreshes or from successful set messages.

## Dependencies and integration points

The file depends on `hpi_internal.h` for ABI types and constants, `hpidebug.h` for logging, `hpimsginit.h` for response initialization, and `hpicmn.h` for declarations. It is used by both `hpi6000.c` and `hpi6205.c` for adapter registry and mixer/control-cache behavior. It integrates with OS locks supplied through `hpios.h`.

## Risks and test signals

Risks include global fixed-size adapter state, shallow-copying adapter objects into the registry, duplicate-index relocation surprising callers, cache blob corruption causing pointer misbuilds, unbounded trust in DSP-provided entry sizes after minimal checks, PAD string termination writes into cache memory, and stale cache data if the backend does not refresh or apply DMA barriers. Test signals include driver-load reset, duplicate adapter insertion, adapter enumeration, invalid index handling, cache allocation failure, cache hits for volume/meter/mux/sampleclock/PAD controls, invalid cached attribute returns, set-state cache synchronization, and response validation errors for corrupted DSP replies.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.h

## Purpose

`hpicmn.h` declares shared adapter and control-cache interfaces used by HPI backend implementations.

## Important APIs, types, and functions

The header forward-declares `struct hpi_adapter_obj`, defines `adapter_int_func`, IRQ result constants (`HPI_IRQ_NONE`, `HPI_IRQ_MESSAGE`, `HPI_IRQ_MIXER`), and declares `struct hpi_adapter_obj` with PCI information, adapter type/index, DSP lock, crash/cache flags, private backend pointer, interrupt callback, and host-buffer status pointers.

It also declares `struct hpi_control_cache`, which stores initialization state, adapter index, control count, raw cache byte size, lookup pointer array, and pointer to the DSP cache memory. Function declarations cover adapter lookup/add/delete, control-cache lookup for whole cache or single entries, allocation/free, set-state cache synchronization, response validation, and `HPI_COMMON`.

## Control flow

There is no executable flow. The declarations define how backend files register adapters, serialize DSP access through the embedded lock, expose optional IRQ and host-buffer status integration, and share control-cache services.

## State and persistence behavior

The struct fields declared here become persistent per-adapter state once copied into the global registry in `hpicmn.c`. `priv` points to backend-specific hardware state allocated by `hpi6000.c` or `hpi6205.c`; `has_control_cache` controls whether backends try cached reads; `dsp_crashed` gates later traffic; host-buffer status pointers persist while DMA buffers are valid.

## Dependencies and integration points

The header depends on `hpi_internal.h` types through includers. It is the contract between backend implementations, common adapter registry/cache code, and upper HPI layers that need interrupt or background-buffer status information.

## Risks and test signals

Risks include lifetime mistakes around `priv` and host-buffer status pointers, backend-private allocation mismatches, stale IRQ callback pointers after delete, and shallow-copy semantics in adapter registration. Test signals are adapter create/delete, lock initialization, crash-threshold handling, IRQ query integration, host-buffer get-info calls after allocate/free, and successful cache allocation and lookup through the common API.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.c

## Purpose

`hpidebug.c` implements the runtime side of the HPI debug macros: global debug-level storage, level getters/setters, initialization logging, compact message logging, and bounded hex dumping.

## Important APIs, types, and functions

It defines the global `int hpi_debug_level`, initialized to `HPI_DEBUG_LEVEL_DEFAULT`. Exported functions are `hpi_debug_init()`, `hpi_debug_level_set()`, `hpi_debug_level_get()`, `hpi_debug_message()`, and `hpi_debug_data()`.

## Control flow

`hpi_debug_level_set()` returns the old level after assigning the new one. `hpi_debug_message()` prints a compact request summary if the message pointer is non-null. `hpi_debug_data()` formats up to eight lines of 16-bit words, eight columns per line, using `DIV_ROUND_UP()` and `printk(KERN_CONT)` continuations. Macro-level filtering happens in `hpidebug.h`; this file assumes callers already decided to log.

## State and persistence behavior

The only persistent state is the global debug level. It affects all asihpi debug macros process-wide/module-wide until changed. The debug functions do not store message history or allocate memory.

## Dependencies and integration points

The implementation includes `hpi_internal.h` and `hpidebug.h`, uses kernel `printk` levels, and is consumed by all backend/common HPI files through macros such as `HPI_DEBUG_LOG`, `HPI_DEBUG_MESSAGE`, and `HPI_DEBUG_DATA`.

## Risks and test signals

Risks include unsynchronized global debug-level changes, log flooding at verbose levels, exposing kernel pointers in data dumps, and `hpi_debug_message()` ignoring its `sz_fileline` argument. Test signals are debug-level sysfs/module-control paths if present, expected filtering by log level, message logging under invalid-response paths, bounded data-dump length, and successful builds with all `SOURCEFILE_NAME` users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.h

## Purpose

`hpidebug.h` defines HPI debug levels, logging/assertion macros, debug function declarations, and a fallback compile-time assertion macro.

## Important APIs, types, and functions

The debug-level enum spans error, warning, notice, info, debug, and verbose. `HPI_DEBUG_LEVEL_DEFAULT` is notice. `FILE_LINE` is built from `SOURCEFILE_NAME` and `__LINE__` when the source defines a name. `HPI_DEBUG_ASSERT()` emits a kernel error if an expression is false. `HPI_DEBUG_LOG(level, ...)`, `HPI_DEBUG_DATA()`, `HPI_DEBUG_MESSAGE()`, and `HPI_DEBUG_RESPONSE()` filter against the global `hpi_debug_level` and use per-level kernel log flags. The header declares `hpi_debug_init()`, `hpi_debug_level_set()`, `hpi_debug_level_get()`, `hpi_debug_message()`, `hpi_debug_data()`, and extern `hpi_debug_level`.

## Control flow

The macros expand into conditional `do { ... } while (0)` blocks. Runtime control is a simple threshold check: messages at or below the current debug level print, with response logging also printing errors at debug level.

## State and persistence behavior

The header owns no storage except through the extern debug-level declaration. Its macros embed file/line strings at compile time and influence all call sites that include it.

## Dependencies and integration points

It includes `hpi_internal.h` for message/response types and uses kernel logging symbols plus `HPI_DEBUG_FLAG_*` definitions expected from OS-specific integration. It is included by the backend, common, and firmware-loader files.

## Risks and test signals

Risks include compile failures if `HPI_DEBUG_FLAG_*` macros are missing, log format drift, assertions that log but do not stop execution, verbose log flooding, and duplicate `compile_time_assert` definitions. Test signals include builds with and without `SOURCEFILE_NAME`, runtime level changes, error-path logging, response logging for DSP errors, and verbose data/message dumps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.c

## Purpose

`hpidspcd.c` provides the DSP firmware reader used by the ASI HPI backends during bootload. It locates `asihpi/dsp%04x.bin` firmware through the Linux firmware loader, validates its header, tracks read position, and exposes word/block iteration helpers for backend bootload loops.

## Important APIs, types, and functions

The private `struct dsp_code_private` stores the `struct firmware *` and `struct pci_dev *`. Exported functions are `hpi_dsp_code_open()`, `hpi_dsp_code_close()`, `hpi_dsp_code_rewind()`, `hpi_dsp_code_read_word()`, and `hpi_dsp_code_read_block()`.

`hpi_dsp_code_open()` builds the firmware path, calls `request_firmware()`, checks that the file contains `struct code_header`, verifies the `"CODE"` tag (`0x45444F43`), adapter ID, total size, and major HPI version, warns on minor/release mismatch, allocates private state, copies the header, and initializes `block_length` and `word_count` just past the header.

## Control flow

Backends call open, then repeatedly read a block length, address, type, and a pointer to a block of `u32` firmware words. A length of `0xFFFFFFFF` terminates the boot image. After writing the image to DSP memory, backends call `hpi_dsp_code_rewind()` and iterate again for verification. Close releases firmware and private memory.

## State and persistence behavior

State lives in the caller-provided `struct dsp_code`: copied header, total word count, current word count, and private firmware pointer. It persists only during bootload. Firmware contents are owned by the kernel firmware subsystem until `release_firmware()`.

## Dependencies and integration points

The file depends on `hpidspcd.h`, `hpidebug.h`, `hpi_version.h`, Linux `request_firmware()`, `release_firmware()`, PCI device structures, and kernel device logging. It integrates with `hpi6000.c` and `hpi6205.c`, which interpret the returned words as DSP memory write records.

## Risks and test signals

Risks include assuming firmware data is safely aligned for `u32 *` access, no checksum validation despite a checksum header field, endianness assumptions, small fixed firmware-name buffer, major-version rejection blocking hardware, minor-version mismatch warnings hiding real ABI changes, and callers needing to close on every open success. Test signals are missing firmware errors, invalid header rejection, major-version mismatch rejection, mismatch warning for nonidentical versions, full bootload plus rewind verification, read past end returning `HPI_ERROR_DSP_FILE_FORMAT`, and leak checks on error paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.h

## Purpose

`hpidspcd.h` declares the DSP firmware-file format and reader API used by ASI HPI backend bootload code.

## Important APIs, types, and functions

`struct code_header` describes firmware files with size, type tag, adapter ID, version, and checksum, and is compile-time asserted to 20 bytes. `struct dsp_code` contains a copied header, total block length in words, current word count, and private reader state. Function declarations cover open, close, rewind, single-word read, and block read.

## Control flow

There is no executable flow in the header. It defines the contract that implementation and backends follow: open a firmware image for an adapter, read sequential words/blocks, rewind for verification, and close when done.

## State and persistence behavior

`struct dsp_code` is transient bootload state owned by backend stack/local variables. The firmware header fields are persistent file metadata and are used to validate adapter/driver compatibility. The checksum field is part of the format even though the current implementation does not verify it.

## Dependencies and integration points

It includes `hpi_internal.h` for types and compile-time assertion support. It integrates with Linux firmware files named by `hpidspcd.c`, and with `hpi6000.c`/`hpi6205.c` bootload loops that consume the record stream.

## Risks and test signals

Risks include file-format ABI drift, unchecked checksum semantics, word-size/endian assumptions, and callers misusing the block pointer after close. Test signals are compile-time header size assertion, firmware open/close, sequential read boundary checks, rewind verification loops, and bootload failure propagation to adapter create responses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidspcd.h -->

# subset-b-003811 research

Grouped source research for Intel ISH ISHTP client/HBM/DMA/loader support and Intel THC QuickI2C/QuickSPI HID transport drivers. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.c

## Purpose
`client.c` implements the ISHTP client-session layer. It allocates and links host clients, connects/disconnects them to firmware clients through HBM, manages RX/TX queues and flow-control credits, sends client payloads over IPC or DMA, receives fragmented or DMA-backed responses, and exposes small client accessors for upper ISHTP client drivers.

## Important APIs, types, and functions
Exported lifecycle APIs are `ishtp_cl_allocate()`, `ishtp_cl_free()`, `ishtp_cl_link()`, `ishtp_cl_unlink()`, `ishtp_cl_connect()`, `ishtp_cl_disconnect()`, `ishtp_cl_establish_connection()`, `ishtp_cl_destroy_connection()`, and `ishtp_cl_flush_queues()`. Data path APIs are `ishtp_cl_send()`, `ishtp_cl_read_start()`, `ishtp_cl_send_msg()`, `recv_ishtp_cl_msg()`, and `recv_ishtp_cl_msg_dma()`. Helpers maintain client state, ring sizes, firmware IDs, private data, and the parent `ishtp_device`.

## Control flow and integration points
Connection starts by linking the client into `dev->cl_list`, reserving a host client ID from `host_clients_map`, locating a firmware client by UUID, then sending `CLIENT_CONNECT_REQ_CMD` and waiting on `wait_ctrl_res` until HBM changes the state to connected or disconnected. Non-reset connection allocates RX/TX rings before starting flow control; reset reconnection reuses existing rings and clears counters/ack state.

Transmit flow enqueues copied payloads into `tx_list`, then sends only when the client is connected, the device is enabled, the payload fits the firmware client's `max_msg_length`, a TX ring entry is free, and `ishtp_flow_ctrl_creds` allows progress. `ishtp_cl_send_msg()` selects DMA only when `dev->transfer_path == CL_TX_PATH_DMA`; otherwise IPC fragments the payload by `dev->mtu`. IPC and DMA are ack-gated against each other via `last_ipc_acked`, `last_dma_acked`, `last_tx_path`, and `last_dma_addr` to avoid mixing outstanding paths.

Receive flow is driven by the HBM/IPC bottom half. `recv_ishtp_cl_msg()` validates the ISHTP header, finds the matching read buffer on `dev->read_list`, copies IPC fragments via `dev->ops->ishtp_read()`, and completes the buffer when `msg_complete` is set. `recv_ishtp_cl_msg_dma()` validates the DMA HBM address/length at the HBM layer, copies the DMA payload into the client's read buffer, and treats it as a complete message. Complete buffers move to `in_process_list` and wake the bus client callback with `ishtp_cl_bus_rx_event()`.

## State and persistence behavior
Persistent runtime state is held in `struct ishtp_cl`: host/firmware IDs, connection state, flow-control credits, RX free buffers, in-process RX list, TX queued/free rings, transmit offsets, ack state, send/receive counters, error counters, and FC timing. `client.c` does not persist data across reboot; it preserves allocated rings across firmware reset when `ishtp_cl_establish_connection(..., reset=true)` is used. Shared device state includes `dev->cl_list`, `dev->read_list`, host-client bitmaps, open-handle count, DMA buffers, and hardware operation callbacks.

## Dependencies
This file depends on `hbm.c` for connect/disconnect/flow-control messages, `dma-if.c` for DMA slot allocation/release, client-buffer helpers for ring objects, `bus.c` for firmware client lookup and RX event dispatch, and low-level `ishtp_hw_ops` for reading/writing hardware IPC. It also uses Linux lists, spinlocks, wait queues, DMA/cache helpers, and exported ISHTP client interfaces consumed by HID and firmware-loader client drivers.

## Risks and edge cases
The largest risks are reset races while a caller waits on `wait_ctrl_res`, stale read buffers left on `dev->read_list`, flow-control credit imbalance, lost DMA/IPC ack sequencing, and queue lock ordering across `read_list_spinlock`, `free_list_spinlock`, `tx_list_spinlock`, and `cl_list_lock`. `ishtp_cl_establish_connection()` returns `-ENOENT` if the UUID is missing but does not unlink the just-linked client in that path, so callers must be robust to failed setup cleanup. RX overflow drops the buffer and withholds new FC, potentially wedging a client. DMA sends rely on coherent buffer allocation plus explicit cache flushing when firmware lacks snooping.

## Test signals
Useful tests are connect/disconnect with valid and missing UUIDs, repeated firmware reset/reconnect, concurrent clients targeting the same firmware client, TX ring exhaustion, payloads at and above max message length, IPC fragmentation across `dev->mtu`, DMA fallback when no DMA slot exists, DMA ACK release validation, RX fragmentation, RX overflow, flow-control timing/counter checks, suspend/resume reset paths, module removal queue flushes, and lockdep/KASAN stress during open/close and interrupt-driven RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.h

## Purpose
`client.h` is the internal ISHTP client contract. It defines the client object, TX ring object, default ring sizes, DMA/IPC path constants, and function declarations used by the ISHTP bus, HBM, DMA, and client-buffer layers.

## Important APIs, types, and functions
`struct ishtp_cl` holds link membership, device pointers, state/status, host and firmware client IDs, inbound/outbound flow-control credits, DMA/IPC ack bookkeeping, RX/TX lists and locks, wait queues, counters, timestamps, and caller-owned `client_data`. `struct ishtp_cl_tx_ring` wraps a list node and `struct ishtp_msg_data`. Declarations cover firmware-client lookup, send/receive dispatch, ring allocation/free, DMA buffer helpers, IO request block helpers, and `ishtp_cl_read_start()`. `ishtp_cl_cmp_id()` compares host/firmware endpoint pairs.

## Control flow and integration points
The header has no executable control flow beyond `ishtp_cl_cmp_id()`. Its fields are directly manipulated by `client.c`, `hbm.c`, `dma-if.c`, `client-buffers.c`, and higher-level ISHTP client drivers. Constants `CL_DEF_RX_RING_SIZE`, `CL_DEF_TX_RING_SIZE`, and max ring sizes define default queue capacities; `CL_TX_PATH_DEFAULT`, `CL_TX_PATH_IPC`, and `CL_TX_PATH_DMA` encode transfer policy and last-transmit path state.

## State and persistence behavior
The header defines in-memory state only. Client objects persist for the lifetime of a bound ISHTP client session, and some state is intentionally reset while buffers persist during firmware reset recovery. No on-disk persistence is present.

## Dependencies
It includes `ishtp-dev.h`, which brings device state, HBM protocol structures, and bus type declarations. It depends on Linux list, spinlock, waitqueue, ktime, GUID, and message data types indirectly through the ISHTP headers.

## Risks and edge cases
Because many fields are shared between IRQ/workqueue/client contexts, misuse of the locks declared here can produce races or credit corruption. The `uint8_t` client IDs and credit fields match the protocol but make overflow/underflow bugs easy to miss. Ring-size setters must respect the declared max sizes in callers, since this header only defines constants and does not enforce them.

## Test signals
Build coverage across ISHTP clients, lockdep stress, ring-size boundary tests, reset reconnection tests that reuse buffers, and allmodconfig builds are the main signals. Static analysis should watch for direct state writes without matching wakeups, list operations outside the proper lock, and credit underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/dma-if.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/dma-if.c

## Purpose
`dma-if.c` manages the shared coherent DMA buffers used for ISHTP-over-DMA transfers. It allocates one host TX buffer and one host RX buffer, tracks 4 KiB TX slots with a bitmap-like byte array, and releases slots when firmware sends DMA transfer acknowledgments.

## Important APIs, types, and functions
`ishtp_cl_alloc_dma_buf()` allocates 1 MiB TX/RX coherent buffers and initializes `ishtp_dma_tx_map` and `ishtp_dma_tx_lock`. `ishtp_cl_free_dma_buf()` releases those buffers and the map. `ishtp_cl_get_dma_send_buf()` finds a contiguous run of free 4 KiB slots for a requested payload and marks them used. `ishtp_cl_release_dma_acked_mem()` validates an acknowledged address and length, then marks the corresponding slots free.

## Control flow and integration points
HBM enables DMA after client enumeration by calling `ishtp_cl_alloc_dma_buf()` and notifying firmware of the RX buffer address. Client transmit uses `ishtp_cl_get_dma_send_buf()` before writing a payload and sending a `DMA_XFER` HBM descriptor. HBM DMA ACK handling calls `ishtp_cl_release_dma_acked_mem()` after validating the acknowledged physical range. The RX buffer is consumed by `hbm.c` when firmware sends `DMA_XFER`.

## State and persistence behavior
DMA state is per `struct ishtp_device`: coherent TX/RX virtual addresses, physical addresses, sizes, slot count, TX slot map, and a spinlock. This is volatile kernel memory and is freed when clients are released or error paths tear down the ISHTP device.

## Dependencies
The file depends on Linux DMA coherent allocation, `DMA_SLOT_SIZE` from `client.h`, and ISHTP device fields from `ishtp-dev.h`. Correct operation also depends on HBM range validation and the client sender's DMA ACK state.

## Risks and edge cases
Allocation is partial-tolerant but does not unwind earlier allocations if a later allocation fails, leaving callers to operate with missing RX or map state. `ishtp_cl_release_dma_acked_mem()` accepts an 8-bit `size`, which can underrepresent larger messages if the protocol length is wider. Slot math must reject unaligned ACK addresses and out-of-range spans; any mismatch leaks TX slots or frees live ones. Cache coherency depends on the coherent allocation and explicit flushes elsewhere when firmware lacks snooping.

## Test signals
Exercise DMA allocation failure at each step, repeated allocate/free cycles, slot exhaustion and contiguous-slot fragmentation, ACKs with unaligned/out-of-range addresses, ACK length edge cases around 4 KiB boundaries, concurrent send/ACK under lockdep, DMA fallback to IPC, and suspend/remove teardown with live outstanding DMA messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/dma-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.c

## Purpose
`hbm.c` implements ISHTP Host Bus Message protocol handling. It starts protocol negotiation, enumerates firmware clients, fetches client properties, handles client connect/disconnect/flow-control messages, enables ISHTP-over-DMA, dispatches DMA transfers and ACKs, handles fixed system/loader clients, and sends suspend/resume system-state notifications.

## Important APIs, types, and functions
Startup APIs include `ishtp_hbm_start_req()`, `ishtp_hbm_start_wait()`, and `ishtp_hbm_enum_clients_req()`. Client-control APIs include `ishtp_hbm_cl_connect_req()`, `ishtp_hbm_cl_disconnect_req()`, and `ishtp_hbm_cl_flow_control_req()`. Dispatch entry points are `recv_hbm()`, `bh_hbm_work_fn()`, `ishtp_hbm_dispatch()`, and `recv_fixed_cl_msg()`. Power/system helpers are `ishtp_query_subscribers()`, `ishtp_send_suspend()`, and `ishtp_send_resume()`.

## Control flow and integration points
The normal HBM boot sequence sends `HOST_START_REQ_CMD`, waits for `HOST_START_RES_CMD`, sends `HOST_ENUM_REQ_CMD`, copies the valid firmware-client bitmap from `HOST_ENUM_RES_CMD`, allocates `dev->fw_clients`, requests properties for each set bit, and finally moves `hbm_state` to `ISHTP_HBM_WORKING` and `dev_state` to `ISHTP_DEV_ENABLED` before creating bus devices with `ishtp_bus_new_client()`.

`recv_hbm()` reads a bus message from hardware. Flow-control is handled immediately so waiting TX queues can resume. Connect/disconnect responses, firmware disconnect requests, and inbound DMA transfers are also dispatched in-order. Other HBM messages are copied into a fixed-size FIFO and processed by `bh_hbm_work_fn()` on the unbound workqueue.

DMA setup happens after all client properties have been fetched and `ishtp_use_dma_transfer()` allows it. The driver allocates RX/TX DMA buffers, notifies firmware of the RX buffer with `DMA_BUFFER_ALLOC_NOTIFY`, marks DMA enabled on `DMA_BUFFER_ALLOC_RESPONSE`, copies inbound DMA data through `recv_ishtp_cl_msg_dma()`, and returns `DMA_XFER_ACK`. Outbound ACKs release TX slots and may trigger the next queued client message.

## State and persistence behavior
The file drives `dev->hbm_state`, `dev->dev_state`, firmware client arrays/bitmaps/indexes, DMA-enabled state, read-message FIFO cursors, loader response flags, and static system-state bitfields. State is volatile and reset-oriented; failures often set `ISHTP_DEV_RESETTING` and call `ish_hw_reset()`.

## Dependencies
It depends on `ishtp_write_message()`, hardware read callbacks, bus client creation, ISHTP client queues, DMA buffer helpers, loader work, and Linux workqueues/waitqueues/spinlocks. It also consumes protocol definitions from `hbm.h` and loader constants from `loader.h`.

## Risks and edge cases
HBM state-machine ordering is strict; unexpected responses trigger hardware reset. The bottom-half FIFO can overflow and drop HBMs. Several routines call `ishtp_write_message()` while holding list locks or flow-control locks, so hardware write latency and lock ordering are important. DMA ACK handling walks `dev->cl_list` without taking `cl_list_lock`, which is a concurrency-sensitive area. Flow-control uses a single outstanding outbound FC credit and can wedge traffic if a receive buffer cannot be replenished. Static system-state variables are global rather than per device.

## Test signals
Probe boot through start/enum/property states, unsupported HBM version handling, malformed property response address/status, FIFO overflow injection, connect/disconnect response wakeups, firmware-initiated disconnect, FC duplicate detection, DMA notify/response, DMA XFER and ACK range validation, loader-client responses, system-state subscribe/suspend/resume messages, reset on unexpected HBM, and lockdep during client removal while DMA ACKs arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.h

## Purpose
`hbm.h` defines the wire-level ISHTP Host Bus Message protocol used by `hbm.c`, `client.c`, DMA transfer paths, system-state fixed clients, and the ISH firmware loader. It contains opcodes, packed message layouts, timeout/version constants, state enums, and public HBM function declarations.

## Important APIs, types, and functions
Important types include `struct ishtp_msg_hdr`, `struct ishtp_bus_message`, `struct hbm_host_version_request/response`, `struct hbm_host_enum_response`, `struct ishtp_client_properties`, `struct hbm_props_request/response`, connect/disconnect request/response structures, `struct hbm_flow_control`, `struct dma_alloc_notify`, `struct dma_xfer_hbm`, and system-state message structures. `enum ishtp_hbm_state` describes HBM progression from idle to working/stopped. `ishtp_hbm_hdr()` initializes host-bus message headers.

## Control flow and integration points
The header has only the inline header initializer. Its declarations are used by the startup path, interrupt RX path, client connection code, suspend/resume notification code, and loader fixed-client handling. Opcode values drive dispatch in `hbm.c`; packed layouts must match firmware exactly.

## State and persistence behavior
The header defines no storage. It defines protocol state values stored in `struct ishtp_device` and state/status bitfields carried in firmware messages. All state is volatile per runtime session.

## Dependencies
It depends on Linux UUID types and ISHTP forward declarations. Its structures intentionally use fixed-width integer types and `__packed` to match the firmware ABI.

## Risks and edge cases
Any layout, opcode, bit-width, or packing drift breaks firmware compatibility. `struct ishtp_msg_hdr` uses bitfields whose ABI depends on compiler/platform assumptions, so this code is tied to the kernel's supported environment. The DMA and system-state structures include reserved fields that must remain zeroed by senders. Timeout constants directly shape probe and client connect failure behavior.

## Test signals
Protocol ABI tests should validate structure sizes and opcode values, HBM startup against real firmware, DMA transfer descriptor parsing, fixed-client system-state exchange, unsupported version handling, and build coverage for endian/packing warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/init.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/init.c

## Purpose
`init.c` initializes the core `struct ishtp_device` software state and starts post-HBM ISHTP processing. It is the common setup code used after a low-level ISH/IPC device allocates its `ishtp_device`.

## Important APIs, types, and functions
`ishtp_device_init()` initializes device state, lists, locks, wait queues, FIFO cursors, the HBM bottom-half work item, host-client bitmap reservation, and firmware-loader work. `ishtp_start()` waits for HBM startup and sends a system-state subscriber query.

## Control flow and integration points
Initialization sets `dev_state = ISHTP_DEV_INITIALIZING`, prepares `cl_list`, `device_list`, `read_list`, locks, HBM receive FIFO, and wait queues. It reserves host client ID 0 for HBM traffic. It also uses `devm_work_autocancel()` so `work_fw_loader` is canceled automatically with the device. `ishtp_start()` is called after the low-level transport has initiated HBM negotiation; it waits through `ishtp_hbm_start_wait()` and then calls `ishtp_query_subscribers()`.

## State and persistence behavior
All state is in-memory per `ishtp_device`. The function establishes initial list/lock/bitmap state but does not allocate firmware clients or persistent storage. Managed loader work lifetime is tied to `dev->devc`.

## Dependencies
This file depends on HBM work/queries, client constants, loader work, Linux device-managed helpers, lists, spinlocks, wait queues, and workqueues. Low-level IPC drivers call into it after allocating the ISHTP device.

## Risks and edge cases
If `devm_work_autocancel()` fails, the code logs but leaves the device otherwise initialized, so later loader-capable firmware may not load correctly. `ishtp_start()` moves to disabled on HBM timeout. Initialization assumes caller has zeroed or otherwise allocated a valid flexible `struct ishtp_device` and installed low-level ops before HBM traffic starts.

## Test signals
Probe success/failure, HBM start timeout, loader-work managed cleanup, host client ID reservation, repeated init after reset paths, and lockdep/KASAN around early interrupt reception are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/ishtp-dev.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/ishtp-dev.h

## Purpose
`ishtp-dev.h` defines the central ISHTP provider-device state, hardware operation callbacks, device state enum, core limits, firmware-client representation, and top-level initialization/start declarations. It is the shared private contract between the ISHTP transport, HBM, bus, client, loader, DMA, and low-level IPC driver code.

## Important APIs, types, and functions
Key constants define IPC payload sizes, RX/TX FIFO capacities, maximum client counts, host client IDs, DMA timing, and resume timeout. `enum ishtp_dev_state` covers initialization, client enumeration, enabled, reset, disabled, and power transitions. `struct ishtp_hw_ops` is the hardware abstraction for reset, IPC header generation, writes, reads, firmware status, clock sync, and DMA cache-snooping checks. `struct ishtp_device` anchors PCI/device pointers, suspend/resume wait state, locks, HBM state, workqueues, loader state, client lists, bus devices, message FIFOs, write queues, firmware client tables, DMA buffers, version info, debug counters, hardware ops, MTU, and hardware-private trailing storage.

## Control flow and integration points
The header has simple inline helpers `ishtp_secs_to_jiffies()` and `ish_ipc_reset()`. The rest of its content is structural: low-level IPC code fills hardware ops and transport fields, `init.c` initializes list/lock/wait state, `hbm.c` transitions HBM/device state and firmware-client tables, `client.c` consumes client lists and DMA buffers, and loader code uses fixed-client response storage.

## State and persistence behavior
`struct ishtp_device` is the primary volatile state container for a live ISH device. It contains no persistent disk-backed state; version fields copied from firmware/manifests remain in memory for reporting while the device is live. Lists, bitmaps, DMA buffers, work items, and wait queues exist until driver removal/reset teardown.

## Dependencies
It includes Linux types/spinlocks, the exported Intel ISH client interface, bus declarations, and HBM protocol definitions. It depends on PCI/device types being available to implementation files and on low-level hardware code supplying `struct ishtp_hw_ops`.

## Risks and edge cases
The structure is broad and heavily shared, so initialization ordering is critical. Interrupts before list/lock/FIFO setup, missed state transitions, or low-level ops installed too late can corrupt startup. Several fields are accessed by IRQ, workqueue, PM, and client contexts, making lock discipline and wakeup pairing important. Fixed FIFO sizes (`RD_INT_FIFO_SIZE`, `IPC_TX_FIFO_SIZE`) create overflow behavior under interrupt storms.

## Test signals
Probe/remove, reset recovery, suspend/resume, HBM enumeration, client open/close stress, loader-capable firmware boot, DMA enablement, debug counter sanity, low-level ops fault injection, and allmodconfig builds should cover this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/ishtp-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.c

## Purpose
`loader.c` implements host-driven main firmware loading for ISH platforms that expose the firmware-loader fixed client. It locates a platform-specific firmware image, allocates DMA fragments, sends loader query/fragment/start commands over ISHTP fixed-client messaging, retries failures, and extracts manifest version information after a successful load.

## Important APIs, types, and functions
The public entry point is `ishtp_loader_work()`, scheduled by HBM when firmware advertises loader capability. Internal helpers are `loader_write_message()`, `loader_xfer_cmd()`, `prepare_dma_bufs()`, `release_dma_bufs()`, `_request_ish_firmware()`, `request_ish_firmware()`, `copy_manifest()`, and `copy_ish_version()`. Firmware naming uses DMI system vendor/product/product-family/SKU CRC32 values plus the generation string from `dev->driver_data->fw_generation`.

## Control flow and integration points
`ishtp_loader_work()` requests firmware using the most-specific DMI-derived filename first and the generation default last. It computes a page-aligned fragment size across `FRAGMENT_MAX_NUM` descriptors, allocates coherent DMA buffers, copies firmware chunks into them, flushes caches, and then retries up to `ISHTP_LOADER_RETRY_TIMES` through `XFER_QUERY`, `XFER_FRAGMENT`, and `START`. Loader responses arrive through `recv_fixed_cl_msg()` in `hbm.c`, which copies data into `dev->fw_loader_rx_buf` and wakes `wait_loader_recvd_msg`.

## State and persistence behavior
Runtime state lives in `struct ishtp_device`: loader wait flags/buffers, base firmware version, and project firmware version. DMA buffers are temporary and released before the work item exits. Firmware files are loaded from the kernel firmware search path but not modified. No driver state is persisted.

## Dependencies
The loader depends on firmware_class, DMI, CRC32, coherent DMA, cache flushing, ISHTP fixed-client writes, HBM loader capability detection, and manifest structures from `loader.h`. It requires `dev_get_drvdata(dev->devc)` to return the `ishtp_device`.

## Risks and edge cases
Missing firmware leaves firmware waiting for host load until drivers are reloaded. DMA allocation failure releases temporary state but cannot recover communication without retrying the driver load. Incorrect firmware may consume all retries and require a platform reset. `request_ish_firmware()` computes CRC variables only when the corresponding DMI string exists; filename branches must only use initialized CRCs. `loader_xfer_cmd()` relies on fixed 100 ms response timeout and a single shared receive buffer, so concurrent loader messages would be unsafe.

## Test signals
Test with default and DMI-specific firmware names, missing firmware, malformed loader responses, timeout/no-response, DMA allocation failure, fragment sizing across small and large firmware images, retry behavior after query/fragment/start failures, manifest present/absent cases, version-field decoding, and removal while loader work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.h

## Purpose
`loader.h` defines the ISHTP firmware-loader fixed-client protocol and manifest structures used by `loader.c` and HBM fixed-client dispatch. It gives the loader command IDs, packed request/response layouts, DMA fragment descriptor shape, retry/timeout constants, loader capability bit, loader fixed-client address, and firmware manifest version layout.

## Important APIs, types, and functions
Important definitions are `LOADER_MSG_SIZE`, `LOADER_CMD_XFER_QUERY`, `LOADER_CMD_XFER_FRAGMENT`, `LOADER_CMD_START`, `LOADER_XFER_MODE_DMA`, `union loader_msg_header`, query/ack structures, `struct loader_capability`, `struct loader_xfer_dma_fragment`, `struct fragment_dscrpt`, `union loader_recv_message`, `ISHTP_LOADER_TIMEOUT`, `ISHTP_LOADER_RETRY_TIMES`, `ISHTP_SUPPORT_CAP_LOADER`, `ISHTP_LOADER_CLIENT_ADDR`, `ISH_MANIFEST_ALIGNMENT`, `ISH_GLOBAL_SIG`, `struct version_in_manifest`, and `struct ish_global_manifest`. It declares `ishtp_loader_work()`.

## Control flow and integration points
The header has no executable control flow. HBM checks `ISHTP_SUPPORT_CAP_LOADER` in the host-start response and schedules `ishtp_loader_work()`. Fixed-client RX dispatch routes messages from address `ISHTP_LOADER_CLIENT_ADDR` into the loader wait buffer. Loader code uses the flexible DMA-fragment table and manifest layouts to transfer and parse firmware.

## State and persistence behavior
No state is stored in this header. It defines volatile protocol messages and the firmware manifest fields copied into `struct ishtp_device` after load.

## Dependencies
It includes Linux bit, jiffies, sizes, and type helpers plus `ishtp-dev.h` for IPC payload sizing. The ABI structures use little-endian integer annotations and flexible arrays.

## Risks and edge cases
`FRAGMENT_MAX_NUM` depends on the loader message size and the flexible descriptor layout; changes to either can alter maximum DMA batching. Packed bitfield header semantics must match firmware. Timeout and retry constants directly influence loader robustness. Manifest parsing assumes 4 KiB alignment and the `ISHG` signature.

## Test signals
Structure size/offset checks, loader-capability probe, fixed-client response routing, fragment-count boundary tests, firmware larger than one fragment, retry timeout behavior, and manifest signature/version parsing are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Kconfig

## Purpose
`Kconfig` declares the Intel Touch Host Controller HID driver menu and the selectable core THC, QuickSPI, and QuickI2C modules. It controls whether the PCI/ACPI THC hardware support and HID-over-SPI/I2C transport drivers are built.

## Important APIs, types, and functions
`CONFIG_INTEL_THC_HID` is a tristate core option depending on `X86_64`, `PCI`, and `ACPI`, and selecting `SGL_ALLOC`. `CONFIG_INTEL_QUICKSPI` and `CONFIG_INTEL_QUICKI2C` are tristate child options that depend on `INTEL_THC_HID`.

## Control flow and integration points
There is no runtime control flow. These symbols feed the kernel build system and gate compilation of `intel-thc.o`, `intel-quickspi.o`, and `intel-quicki2c.o` in the adjacent Makefile. The help text documents THC as a PCH IP block with SPI, I2C, and DMA/sequencer components.

## State and persistence behavior
Kconfig choices persist only in the kernel build configuration. They determine module availability, not runtime device state.

## Dependencies
The menu depends on x86_64 and PCI. The core depends on ACPI and selects scatter-gather allocation support. QuickSPI/QuickI2C depend on the core THC support and the source files' external HID-over-SPI/I2C and Intel THC helper APIs.

## Risks and edge cases
Incorrect dependencies can allow impossible builds, such as transport modules without ACPI/PCI THC support. Selecting `SGL_ALLOC` in the core is needed by THC DMA helpers; removing it could break link or runtime allocation paths. Help text and symbol names must stay aligned with Makefile targets.

## Test signals
Run config/build matrix checks for built-in, module, and disabled combinations; verify transport options disappear when `INTEL_THC_HID` is disabled; and build all three modules under `allmodconfig` and minimal x86_64 PCI/ACPI configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Makefile

## Purpose
`Makefile` maps the THC Kconfig symbols to kernel objects. It builds the shared Intel THC core and the QuickSPI/QuickI2C transport modules with their PCI, HID, and protocol components.

## Important APIs, types, and functions
`obj-$(CONFIG_INTEL_THC_HID)` builds `intel-thc.o` from `intel-thc-dev.o`, `intel-thc-dma.o`, and `intel-thc-wot.o`. `obj-$(CONFIG_INTEL_QUICKSPI)` builds `intel-quickspi.o` from `pci-quickspi.o`, `quickspi-hid.o`, and `quickspi-protocol.o`. `obj-$(CONFIG_INTEL_QUICKI2C)` builds `intel-quicki2c.o` from `pci-quicki2c.o`, `quicki2c-hid.o`, and `quicki2c-protocol.o`. `ccflags-y` adds the shared `intel-thc` include path.

## Control flow and integration points
There is no runtime control flow. The Makefile composes module boundaries: QuickSPI and QuickI2C import symbols from the core THC module namespace, and the include path lets transport code include `intel-thc-dev.h`, `intel-thc-dma.h`, and related headers.

## State and persistence behavior
The file affects build artifacts only. It does not define runtime state.

## Dependencies
It depends on Kconfig symbols and on source file layout under `intel-thc`, `intel-quickspi`, and `intel-quicki2c`. It also assumes the exported THC helper namespace is available to the transport modules.

## Risks and edge cases
Object list drift can omit a required protocol or HID file from a module. Include-path changes can break local header resolution. If the core is built-in and transports are modules, namespace imports and symbol exports must remain valid.

## Test signals
Build each symbol as `y`, `m`, and `n`; inspect module dependencies with `modinfo`; and run link checks for namespace imports and unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/pci-quicki2c.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/pci-quicki2c.c

## Purpose
`pci-quicki2c.c` is the PCI driver for Intel THC QuickI2C. It enables the PCI device, reads ACPI resources for the HID-over-I2C target and THC platform tuning, configures the THC I2C sub-IP, IRQs, wake-on-touch, DMA, HID descriptors, runtime PM, and full system sleep/hibernate transitions.

## Important APIs, types, and functions
Main entry points are `quicki2c_probe()`, `quicki2c_remove()`, `quicki2c_shutdown()`, and the `quicki2c_pm_ops` callbacks. ACPI helpers are `quicki2c_acpi_get_dsm_property()`, `quicki2c_acpi_get_dsd_property()`, and `quicki2c_get_acpi_resources()`. IRQ/data helpers are `quicki2c_irq_quick_handler()`, `quicki2c_irq_thread_handler()`, `handle_input_report()`, and `try_recover()`. Device/DMA helpers include `quicki2c_dev_init()`, `quicki2c_dev_deinit()`, `quicki2c_dma_init()`, `quicki2c_dma_deinit()`, advanced DMA enable/disable, and report-buffer allocation.

## Control flow and integration points
Probe enables PCI, maps BAR 0, chooses a 64-bit or 32-bit DMA mask, allocates one IRQ vector, initializes `quicki2c_device`, requests a threaded IRQ, reads the HIDI2C descriptor, allocates report buffers, configures THC DMA, unquiesces interrupts, powers the device on, resets the HIDI2C device, reads the report descriptor, registers a HID device, marks the state enabled, and enables autosuspend runtime PM.

ACPI parsing fetches the HID descriptor address and LTR values through DSMs, then gets ICRS/ISUB buffers for slave address, connection speed, timing counters, max frame size, and interrupt delay. Only 7-bit addressing is supported. Speed ranges select standard, fast/fast-plus, or high-speed THC I2C modes.

The IRQ top half disables THC interrupts and wakes the threaded handler. The thread resumes runtime PM, calls `thc_interrupt_handler()`, recovers on fatal/transaction/unknown interrupts, drains RXDMA2 via `thc_rxdma_read()`, handles zero-length reset acknowledgments, sends input data to HID only when enabled, re-enables interrupts, optionally reconfigures DMA, and drops the runtime PM reference.

## State and persistence behavior
`struct quicki2c_device` persists as devm-managed driver data for the PCI device. It stores ACPI-derived bus parameters, THC context, HID descriptor, cached report descriptor, input/report buffers, reset wait state, advanced RX configuration, LTR values, and state enum. No disk persistence is present. Runtime PM switches THC LTR mode between active and low power.

## Dependencies
The file depends on PCI core, ACPI DSM/DSD, GPIO wake-on-touch mappings, PM runtime, HID registration through `quicki2c-hid.c`, HIDI2C protocol helpers from `quicki2c-protocol.c`, and exported THC core functions for port selection, I2C timing, interrupts, DMA, WOT, and LTR.

## Risks and edge cases
The ACPI buffer helper copies returned buffers without validating length against the destination structure, making firmware table correctness critical. Probe error paths after DMA configuration often jump to `dev_deinit` rather than `dma_deinit`, so DMA cleanup ordering should be audited. Interrupts are enabled during initialization before all buffers are available; state gating drops samples but reset interrupts must still be handled. Runtime PM is entered with `pm_runtime_put_noidle()`/`put_autosuspend()` without an explicit enable call in this file, relying on inherited PM state conventions. Advanced RX max-size settings clamp invalid ACPI values but may truncate devices with larger real reports.

## Test signals
Test PCI ID matching for LNL/PTL/WCL/NVL ports, ACPI DSM/DSD missing or malformed data, 7-bit versus 10-bit addressing rejection, all supported I2C speed bands, descriptor read/reset/report-descriptor flow, threaded IRQ RXDMA input, reset ACK fallback, fatal interrupt recovery, DMA allocation/configuration failures, WOT GPIO presence/absence, suspend/resume/freeze/thaw/poweroff/restore, runtime autosuspend LTR switching, and HID raw GET/SET report behavior through runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/pci-quicki2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-dev.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-dev.h

## Purpose
`quicki2c-dev.h` defines QuickI2C platform IDs, ACPI method names and function numbers, timing limits, runtime-PM defaults, the QuickI2C state enum, ACPI buffer structures, platform data, and the main `struct quicki2c_device`.

## Important APIs, types, and functions
Constants cover LNL/PTL/WCL/NVL PCI device IDs, HIDI2C DSD methods `ICRS` and `ISUB`, DSM function numbers for HID descriptor address and LTR values, I2C speed thresholds, default LTR and autosuspend values, RX max-detect limits, interrupt-delay limits, and addressing modes. `struct quicki2c_subip_acpi_parameter` describes ICRS data; `struct quicki2c_subip_acpi_config` describes ISUB timing and DMA-advanced controls. `struct quicki2c_ddata` stores platform RX-detection capabilities. `struct quicki2c_device` is the complete PCI device context.

## Control flow and integration points
The header has no executable control flow. `pci-quicki2c.c` fills the device context from PCI and ACPI, protocol code consumes descriptors/buffers/THC handles, and HID glue stores `hid_dev` and uses descriptor fields for HID registration.

## State and persistence behavior
It defines volatile per-device runtime state: ACPI parameters, MMIO, THC/HID/ACPI pointers, buffers, wait queues, reset flag, advanced DMA settings, LTR values, and current state. No persistent storage is defined.

## Dependencies
It includes HID-over-I2C protocol types and Linux workqueue declarations, and forward-declares PCI, ACPI, THC, HID, and device structures. It relies on shared THC constants for I2C mode values in implementation files.

## Risks and edge cases
Packed ACPI structures must match platform firmware exactly. Many ACPI timing fields are `u64` but are later assigned into `u32` device fields, so large values can truncate. PCI ID constants must stay aligned with the PCI match table. Buffer length/report length fields come from device descriptors and need defensive allocation in implementation code.

## Test signals
Compile coverage, ACPI fixture parsing for ICRS/ISUB, platform data selection by PCI ID, max-detect clamping, waitqueue/reset state behavior, and suspend/resume tests using the stored LTR/timing fields are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.c

## Purpose
`quicki2c-hid.c` adapts QuickI2C protocol operations to the HID core's low-level driver interface. It registers a `hid_device`, parses the cached report descriptor, handles HID raw GET/SET/output report requests, and forwards received input reports to HID core.

## Important APIs, types, and functions
The HID callbacks are `quicki2c_hid_parse()`, `quicki2c_hid_start()`, `quicki2c_hid_stop()`, `quicki2c_hid_open()`, `quicki2c_hid_close()`, `quicki2c_hid_raw_request()`, `quicki2c_hid_power()`, and `quicki2c_hid_output_report()`. Public functions are `quicki2c_hid_probe()`, `quicki2c_hid_remove()`, and `quicki2c_hid_send_report()`.

## Control flow and integration points
Probe allocates a HID device, assigns the low-level driver, sets bus to `BUS_PCI`, fills version/vendor/product from the HIDI2C descriptor, sets name/phys, and calls `hid_add_device()`. Raw requests resume runtime PM, dispatch GET/SET to `quicki2c_get_report()` or `quicki2c_set_report()`, then autosuspend. Output reports call `quicki2c_output_report()`. RX data from the PCI IRQ path enters HID core through `hid_input_report()`.

## State and persistence behavior
The HID device pointer is stored in `qcdev->hid_dev` until removal. The file owns no persistent storage beyond HID core registration. Runtime PM references are transient around raw requests.

## Dependencies
It depends on Linux HID/input, PM runtime, `quicki2c_device`, and protocol helpers in `quicki2c-protocol.c`.

## Risks and edge cases
Callbacks are mostly stubs, so open/close do not gate hardware activity. Unsupported raw request types log an error but return the initial zero `ret`, which can look like success. `quicki2c_hid_send_report()` assumes `hid_dev` is valid and registered. Descriptor parsing fails if the report descriptor was not fetched before HID probe.

## Test signals
HID registration/removal, report descriptor parse failure, GET/SET feature and input raw requests, output report writes, runtime PM error propagation, unsupported request type handling, and injected HID input reports from IRQ context are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.h

## Purpose
`quicki2c-hid.h` is the small public declaration header for QuickI2C HID-core integration.

## Important APIs, types, and functions
It forward-declares `struct quicki2c_device` and declares `quicki2c_hid_send_report()`, `quicki2c_hid_probe()`, and `quicki2c_hid_remove()`.

## Control flow and integration points
There is no executable control flow. The PCI driver calls probe/remove, and the IRQ data path calls `quicki2c_hid_send_report()` when HIDI2C input data is available. Protocol/HID code share `struct quicki2c_device` through the forward declaration.

## State and persistence behavior
The header owns no state; the implementation stores HID registration state in `quicki2c_device`.

## Dependencies
It depends only on the QuickI2C device type existing in implementation files. The minimal include surface helps avoid HID header leakage.

## Risks and edge cases
Signature drift between this header and `quicki2c-hid.c` would break callers. There is no compile-time visibility into report buffer size semantics beyond `size_t data_size`.

## Test signals
Build coverage for PCI, HID, and protocol objects; HID probe/remove flow; and input-report forwarding through this declared API are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.c

## Purpose
`quicki2c-protocol.c` implements HID-over-I2C transactions on top of Intel THC PIO, SWDMA, and DMA helpers. It encodes HIDI2C commands, reads device/report descriptors, handles HID GET/SET/output reports, powers the device, and performs reset with interrupt or fallback PIO acknowledgment.

## Important APIs, types, and functions
Public APIs are `quicki2c_set_power()`, `quicki2c_get_device_descriptor()`, `quicki2c_get_report_descriptor()`, `quicki2c_get_report()`, `quicki2c_set_report()`, `quicki2c_output_report()`, and `quicki2c_reset()`. Internal helpers are `quicki2c_init_write_buf()`, `quicki2c_encode_cmd()`, and `write_cmd_to_txdma()`.

## Control flow and integration points
Command construction writes the command register, encoded command, optional data register, and optional length-prefixed payload into `qcdev->report_buf`. `quicki2c_get_device_descriptor()` reads the descriptor from the ACPI-provided HID descriptor address by PIO and validates the HIDI2C BCD version. `quicki2c_get_report_descriptor()` reads from the report descriptor register with SWDMA. GET_REPORT sends a command and reads a `struct hidi2c_report_packet`, validating packet length and report ID before copying to the HID buffer. SET_REPORT and output reports write data through THC DMA.

Reset sends `HIDI2C_RESET`, waits up to five seconds for `reset_ack_wq`, and if no interrupt-driven ACK arrives, reads the input register manually and treats a zero length word as reset response. This integrates with `pci-quicki2c.c`, whose IRQ path sets `reset_ack` when it sees zero-length input during `QUICKI2C_RESETING`.

## State and persistence behavior
The file uses and updates `quicki2c_device` buffers, descriptor fields, reset flag/state, and report length. It does not persist anything outside live driver memory.

## Dependencies
It depends on Linux HID-over-I2C definitions, unaligned little-endian helpers, bitfield helpers, and exported THC APIs: `thc_tic_pio_write_and_read()`, `thc_tic_pio_read()`, `thc_swdma_read()`, and `thc_dma_write()`.

## Risks and edge cases
`quicki2c_init_write_buf()` must size command/data sequences correctly to avoid report-buffer overflow. GET_REPORT requires exact returned length and first data byte matching the report number, which may reject devices with unusual report framing. Reset fallback assumes a zero length word unambiguously means reset response. Unsupported output/input/feature type combinations return `-EINVAL`; unsupported raw request behavior is partly handled in HID glue. Concurrency around shared `report_buf`/`input_buf` is not locally serialized, so HID requests and IRQ/reset paths rely on higher-level sequencing.

## Test signals
Descriptor read and BCD mismatch, command encoding for report IDs below and above `HIDI2C_CMD_MAX_RI`, buffer overflow rejection, GET_REPORT length/ID validation, SET_REPORT and output report DMA writes, reset interrupt ACK and fallback PIO ACK paths, timeout behavior, runtime PM raw requests, and fuzzed device packet lengths should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.h

## Purpose
`quicki2c-protocol.h` declares the QuickI2C HID-over-I2C protocol operations used by PCI probe/PM code and HID low-level callbacks.

## Important APIs, types, and functions
It declares `quicki2c_set_power()`, `quicki2c_get_report()`, `quicki2c_set_report()`, `quicki2c_output_report()`, `quicki2c_get_device_descriptor()`, `quicki2c_get_report_descriptor()`, and `quicki2c_reset()`, and forward-declares `struct quicki2c_device`.

## Control flow and integration points
There is no executable control flow. `pci-quicki2c.c` uses descriptor, reset, power, and report-descriptor functions during probe and PM. `quicki2c-hid.c` uses GET/SET/output functions for HID raw requests.

## State and persistence behavior
The header owns no state. Declared functions operate on volatile `quicki2c_device` state and buffers.

## Dependencies
It includes Linux HID-over-I2C for `enum hidi2c_power_state` and report constants used by callers.

## Risks and edge cases
Signature drift can break the HID and PCI layers. Since the header exposes raw buffer pointers and lengths, callers must provide buffers that match HID/core expectations and device report framing.

## Test signals
Build coverage, probe descriptor/reset flow, HID raw request paths, and PM power-state calls validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/pci-quickspi.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/pci-quickspi.c

## Purpose
`pci-quickspi.c` is the PCI driver for Intel THC QuickSPI. It enables THC hardware in SPI mode, reads HIDSPI/QuickSPI/platform ACPI resources, configures SPI read/write engines, interrupts, wake-on-touch, DMA, HID descriptors, runtime PM, and system sleep/hibernate transitions.

## Important APIs, types, and functions
Main entry points are `quickspi_probe()`, `quickspi_remove()`, `quickspi_shutdown()`, and `quickspi_pm_ops`. ACPI parsing uses `thc_acpi_get_property()` and `quickspi_get_acpi_resources()`. IRQ and recovery functions are `quickspi_irq_quick_handler()`, `quickspi_irq_thread_handler()`, and `try_recover()`. Device/DMA/buffer helpers are `quickspi_dev_init()`, `quickspi_dev_deinit()`, `quickspi_dma_init()`, `quickspi_dma_deinit()`, and `quickspi_alloc_report_buf()`.

## Control flow and integration points
Probe enables PCI, maps BAR 0, sets DMA mask, allocates one IRQ vector, creates and configures `quickspi_device`, requests a threaded IRQ, resets the touch device via `reset_tic()`, allocates report buffers, configures THC DMA, fetches the report descriptor, registers the HID device, marks state enabled, and enables autosuspend runtime PM.

ACPI parsing fetches input header/body/output report addresses, read/write opcodes, read/write IO modes, connection speed, packet-size limit, performance delay, and LTR values through three DSM GUIDs. SPI IO mode bits are decoded into THC read/write mode fields, and packet size is selected from platform driver data unless the device requests limiting.

The IRQ top half disables interrupts and wakes the threaded handler. The thread resumes runtime PM, handles THC fatal/transaction errors through reset and DMA reconfiguration, handles non-DMA interrupts as reset or descriptor-response wakeups, drains RXDMA2 into `input_buf`, and calls `quickspi_handle_input_data()` to parse HIDSPI responses or input reports.

## State and persistence behavior
`struct quickspi_device` is devm-managed per PCI device and stores ACPI-derived SPI parameters, THC/HID pointers, descriptors, report/input buffers, waitqueue flags for reset/non-DMA/report/get/set completion, LTR values, packet-size/performance settings, and state enum. Runtime PM changes THC LTR mode only; no disk persistence exists.

## Dependencies
The driver depends on PCI, ACPI DSMs, GPIO wake-on-touch, PM runtime, HID glue, HIDSPI protocol helpers, and exported Intel THC core functions for port selection, SPI address/config, interrupt handling, DMA, WOT, and LTR.

## Risks and edge cases
ACPI buffer copies assume the returned object is large enough for target fields. Interrupts are enabled during device initialization before every probe-stage buffer exists; state and waitqueue logic must absorb early events. Recovery resets the TIC and reconfigures DMA but disables the device if that fails. System restore must fully reprogram SPI address/read/write settings because hardware may lose state. Shared response flags such as `get_report_cmpl`/`set_report_cmpl` are single-flight and assume serialized HID requests.

## Test signals
Test PCI IDs for MTL/LNL/PTL/WCL/ARL/NVL ports, ACPI resource absence and malformed objects, SPI IO mode decoding, packet-size limit behavior, reset via ACPI `_RST`, non-DMA interrupt handling, RXDMA report parsing, DMA allocation/configuration failure, error recovery, report descriptor retrieval, HID registration, suspend/resume/freeze/thaw/poweroff/restore, runtime autosuspend LTR switching, and raw HID GET/SET report completion waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/pci-quickspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-dev.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-dev.h

## Purpose
`quickspi-dev.h` defines QuickSPI PCI IDs, ACPI DSM function numbers, packet-size defaults, runtime-PM defaults, state enum, platform data, and the main `struct quickspi_device` used by the PCI, protocol, and HID layers.

## Important APIs, types, and functions
Constants enumerate MTL/LNL/PTL/WCL/ARL/NVL SPI port IDs, HIDSPI DSM functions for report addresses/opcodes/IO mode, QuickSPI DSM functions for speed/packet/performance limits, platform DSM LTR functions, IO mode/performance bitfields, and packet-size limits. `enum quickspi_dev_state` describes lifecycle states. `struct quickspi_driver_data` supplies per-platform max packet size. `struct quickspi_device` stores device pointers, THC context, descriptor, SPI addresses/opcodes/modes, packet/performance parameters, LTR values, buffers, report length, and waitqueue completion flags.

## Control flow and integration points
The header has no executable control flow. `pci-quickspi.c` fills ACPI and hardware fields, `quickspi-protocol.c` consumes descriptor/buffer/waitqueue state, and `quickspi-hid.c` registers and uses `hid_dev`.

## State and persistence behavior
It defines volatile per-device runtime state. Completion flags represent one outstanding reset, non-DMA interrupt, report descriptor, GET report, or SET report operation. No persistent storage is defined.

## Dependencies
It includes Linux bit helpers, HID-over-SPI definitions, sizes/waitqueue APIs, and `quickspi-protocol.h`. It forward-declares PCI, ACPI, THC, HID, and generic device types.

## Risks and edge cases
The header includes `quickspi-protocol.h`, which also forward-declares this device type; include ordering should remain acyclic. Single boolean completion flags can be lost if multiple same-type operations overlap. PCI ID constants must stay aligned with the match table. Buffer sizes depend on descriptor fields provided by the device.

## Test signals
Build coverage, platform data selection by PCI ID, ACPI field population, waitqueue/completion behavior under repeated raw requests, and PM tests using stored LTR/SPI config are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.c

## Purpose
`quickspi-hid.c` connects QuickSPI HIDSPI protocol handling to the HID core. It registers a `hid_device`, parses the cached HIDSPI report descriptor, forwards HID raw GET/SET requests to QuickSPI protocol functions, and injects input reports received from the hardware path.

## Important APIs, types, and functions
The low-level HID callbacks are `quickspi_hid_parse()`, `quickspi_hid_start()`, `quickspi_hid_stop()`, `quickspi_hid_open()`, `quickspi_hid_close()`, `quickspi_hid_raw_request()`, and `quickspi_hid_power()`. Public functions are `quickspi_hid_probe()`, `quickspi_hid_remove()`, and `quickspi_hid_send_report()`.

## Control flow and integration points
Probe allocates a HID device, assigns the low-level driver, sets PCI bus/parent/driver_data, fills version/vendor/product/name/phys from the HIDSPI device descriptor, and calls `hid_add_device()`. Raw requests resume runtime PM, dispatch GET/SET through `quickspi_get_report()`/`quickspi_set_report()`, then autosuspend. RX data parsed by `quickspi_handle_input_data()` is sent into HID core by `hid_input_report()`.

## State and persistence behavior
The HID device pointer is stored in `qsdev->hid_dev` until removal. This file does not persist data. Runtime PM references are scoped to raw requests.

## Dependencies
It depends on Linux HID/input, PM runtime, `quickspi_device`, and QuickSPI protocol declarations.

## Risks and edge cases
Open/close/power callbacks are stubs, so they do not control hardware data flow. Unsupported raw request types log once but return zero, which may mask caller misuse. `quickspi_get_report()` returns the cached `qsdev->report_len`, so HID callers rely on protocol parsing to keep that length valid. `quickspi_hid_send_report()` assumes a registered HID device.

## Test signals
HID descriptor parse, HID add/remove, GET/SET report raw requests, unsupported request type behavior, runtime PM failures, RX input injection, and removal while reports are pending are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.h

## Purpose
`quickspi-hid.h` is the small declaration header for QuickSPI HID-core integration.

## Important APIs, types, and functions
It forward-declares `struct quickspi_device` and declares `quickspi_hid_send_report()`, `quickspi_hid_probe()`, and `quickspi_hid_remove()`.

## Control flow and integration points
There is no executable control flow. The PCI driver calls probe/remove, and protocol RX parsing calls `quickspi_hid_send_report()` for input data.

## State and persistence behavior
The header owns no state; implementation state is stored in `quickspi_device` and HID core objects.

## Dependencies
It intentionally depends only on the forward-declared QuickSPI device type.

## Risks and edge cases
Signature drift breaks PCI/protocol callers. The API does not encode report ownership or lifetime, so callers must pass valid buffers for the duration of `hid_input_report()`.

## Test signals
Build coverage and runtime HID probe/remove/input-report forwarding validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.c

## Purpose
`quickspi-protocol.c` implements HIDSPI protocol transactions over Intel THC. It writes HIDSPI output reports through DMA or PIO, reads the device descriptor, retrieves the report descriptor, parses inbound HIDSPI responses/data, resets the touch device through ACPI `_RST`, and implements HID GET/SET report operations with waitqueue completions.

## Important APIs, types, and functions
Public APIs are `quickspi_handle_input_data()`, `quickspi_get_report_descriptor()`, `quickspi_set_power()`, `reset_tic()`, `quickspi_get_report()`, and `quickspi_set_report()`. Internal helpers are `write_cmd_to_txdma()`, `quickspi_get_device_descriptor()`, and `acpi_tic_reset()`.

## Control flow and integration points
`write_cmd_to_txdma()` formats an `output_report` in `qsdev->report_buf` and submits it with `thc_dma_write()`. `quickspi_get_device_descriptor()` sends a `DEVICE_DESCRIPTOR` command by PIO, waits for a non-DMA interrupt, reads interrupt-cause length, reads the input report body, and copies the descriptor from a `DEVICE_DESCRIPTOR_RESPONSE`.

`quickspi_handle_input_data()` parses RXDMA input body headers. It copies report descriptors and wakes `report_desc_got_wq`, records set-power command responses, handles reset responses depending on state, copies GET report responses into `report_buf` and wakes `get_report_cmpl_wq`, wakes SET report completions, and forwards DATA input reports to HID only when the driver is enabled.

`reset_tic()` switches interrupt trigger type, executes ACPI `_RST`, unquiesces interrupts, waits for reset ACK, validates a zero-length reset response body through PIO, sets state reset, and then reads the device descriptor. GET/SET report operations send the appropriate report type and wait up to `QUICKSPI_ACK_WAIT_TIMEOUT` seconds for protocol parsing to set completion flags.

## State and persistence behavior
The file updates `quickspi_device` state, reset/non-DMA/report/get/set completion flags, cached report descriptor, report buffer, report length, and device descriptor. No state is persisted beyond the live device.

## Dependencies
It depends on ACPI, bitfield helpers, HID-over-SPI structures/constants, THC PIO/DMA/interrupt APIs, QuickSPI HID forwarding, and the ACPI companion stored by the PCI driver.

## Risks and edge cases
GET/SET report completion flags are single-flight and not protected by a mutex here. `quickspi_set_report()` skips the first byte of the HID buffer (`buf + 1`) and subtracts one from length, so zero-length or malformed caller buffers would underflow. Device descriptor fetch depends on non-DMA interrupt ordering and exact length from THC interrupt cause. Reset changes interrupt trigger type and must remain synchronized with HIDSPI requirements. DATA reports larger than descriptor max are dropped.

## Test signals
Device descriptor command/response, unexpected input report type, report descriptor length mismatch, set-power response, reset ACK timeout and validation, ACPI `_RST` failure, RXDMA DATA forwarding, GET input/feature report completion, SET output/feature completion, zero/short SET report buffers, and concurrent raw requests are the key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.h

## Purpose
`quickspi-protocol.h` declares the QuickSPI HIDSPI protocol operations shared by the PCI driver and HID glue.

## Important APIs, types, and functions
It defines `QUICKSPI_ACK_WAIT_TIMEOUT` and declares `quickspi_handle_input_data()`, `quickspi_get_report()`, `quickspi_set_report()`, `quickspi_get_report_descriptor()`, `quickspi_set_power()`, and `reset_tic()`.

## Control flow and integration points
There is no executable control flow. The PCI probe/PM/recovery paths call reset, descriptor, and power functions; the IRQ thread calls `quickspi_handle_input_data()`; HID raw requests call GET/SET report functions.

## State and persistence behavior
The header owns no state. Declared functions operate on live `struct quickspi_device` fields and waitqueue flags.

## Dependencies
It includes Linux HID-over-SPI for `enum hidspi_power_state` and HIDSPI constants. It forward-declares `struct quickspi_device`.

## Risks and edge cases
Timeout constant changes alter all report/reset waits. GET report does not take an output length parameter in this API, so callers rely on the protocol layer's cached `report_len` and buffer sizing.

## Test signals
Build coverage, reset/probe flow, IRQ RX parsing, HID raw GET/SET calls, and timeout handling validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.h -->

# subset-b-003860 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd.h

## Purpose

`cmd.h` is the shared command/response contract for the MIPI I3C HCI master driver. It defines descriptor bits that are common to both HCI v1 and v2 command formats, response decoding helpers, HCI response error codes, transfer ID generation, and the `hci_cmd_ops` vtable consumed by the core.

## Important APIs, Types, and Functions

- `CMD_0_TOC`, `CMD_0_ROC`, `CMD_0_ATTR`, and `CMD_0_TID` are descriptor word-0 fields that the core may add after version-specific preparation.
- `RESP_STATUS()`, `RESP_TID()`, and `RESP_DATA_LENGTH()` decode hardware response descriptors used by PIO and DMA backends and by core transfer result handling.
- `enum hci_resp_err` maps HCI status nibbles to success, CRC/parity/frame/NACK/overflow/short-read/terminated/not-supported, and transfer-specific errors.
- `hci_get_tid()` allocates four-bit command transaction IDs from `hci->next_cmd_tid`.
- `struct hci_cmd_ops` abstracts descriptor preparation for CCC, private I3C, private I2C, and DAA operations.
- `mipi_i3c_hci_cmd_v1` and `mipi_i3c_hci_cmd_v2` are the two concrete implementations selected by core capability probing.

## Control Flow

The core calls the chosen `hci->cmd` callbacks when preparing transfers. Version-specific code fills `struct hci_xfer.cmd_desc[]`, assigns `cmd_tid`, and may consume small write payloads into immediate descriptor bytes by clearing `xfer->data`. The core later sets common `ROC` and `TOC` bits and submits descriptors to the selected I/O backend.

## State and Persistence Behavior

This header owns no storage, but its TID macro mutates `hci->next_cmd_tid`. TIDs wrap modulo 16, so correctness depends on the response queues preserving order or matching responses before a wrapped TID can collide with a live descriptor.

## Dependencies and Integration Points

It depends on bit helpers from `hci.h` and Linux bitfield macros included by C files. It is included by command implementations, core transfer paths, PIO/DMA backends, and error handlers.

## Risks and Edge Cases

TID width is only four bits, so stalled or out-of-order hardware responses can make diagnostics ambiguous. Several response enum values are shared by different transfer contexts, requiring callers to interpret status with command type in mind. The common `CMD_0_*` masks must remain synchronized with both descriptor formats.

## Test Signals

Useful signals include descriptor TID/attribute bit validation for v1 and v2 commands, response decoding for every status nibble, timeout/dequeue behavior with wrapped TIDs, and CCC/I3C/I2C transfers that verify `ROC` and `TOC` are applied by the core after version-specific preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v1.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v1.c

## Purpose

`cmd_v1.c` implements HCI v1.0/v1.1 command descriptor generation. It translates Linux I3C core CCC/private-transfer/DAA requests into v1 address-assignment, immediate-data, regular-data, and internal-control descriptor words.

## Important APIs, Types, and Functions

- Descriptor macros define v1 address assignment (`CMD_0_ATTR_A`), immediate transfer (`CMD_0_ATTR_I`), regular transfer (`CMD_0_ATTR_R`), combo transfer, and internal-control fields.
- `enum hci_cmd_mode` maps bus rates to HCI v1 I3C/I2C mode selectors.
- `get_i3c_mode()` and `get_i2c_mode()` derive descriptor mode from `bus->scl_rate`.
- `fill_data_bytes()` packs up to four write bytes into descriptor word 1 and clears `xfer->data` so I/O backends do not transfer a separate data buffer.
- `hci_cmd_v1_prep_ccc()`, `hci_cmd_v1_prep_i3c_xfer()`, and `hci_cmd_v1_prep_i2c_xfer()` prepare transfer descriptors.
- `hci_cmd_v1_daa()` performs one-address-at-a-time ENTDAA using a temporary DAT entry and DCT readback.

## Control Flow

CCC preparation rejects raw CCC framing, resolves directed CCC addresses through the v1 DAT, assigns a TID, and chooses immediate descriptors for writes of four bytes or less, otherwise regular descriptors. Private I3C/I2C preparation follows the same immediate-versus-regular split using the device's allocated DAT index.

DAA allocates one temporary DAT entry per candidate device, asks the core for the next free dynamic address, writes that address into DAT, resets the DCT read index, submits an address-assignment command with `ROC|TOC`, then interprets response status. Address-header/NACK with response length 1 means no more devices; successful assignment reads PID/BCR/DCR from DCT, frees the temporary DAT entry, and registers the new device with the I3C core, which will allocate its persistent DAT entry.

## State and Persistence Behavior

Prepared descriptors are stored in caller-owned `struct hci_xfer`. Persistent device state is the DAT index stored in per-device master data by core attach callbacks. DAA temporarily mutates DAT and DCT state and always frees the temporary DAT slot on exit when allocated.

## Dependencies and Integration Points

This file depends on `dat_v1` for DAT allocation/address lookup, `dct_v1` for DCT identity reads, `i3c_hci_process_xfer()` for synchronous command execution, and I3C core helpers such as `i3c_master_get_free_addr()` and `i3c_master_add_i3c_dev_locked()`.

## Risks and Edge Cases

Raw CCC is unsupported for v1 and returns `-EINVAL` if requested by a quirk. Small write payload packing reads a `u8 *` supplied by the caller; zero-length writes are handled but malformed non-NULL assumptions would be caller bugs. DAA registers devices without passing captured PID/BCR/DCR to the core, leaving the core to rediscover data later. One-at-a-time DAA is simple but slower and has several hardware response interpretations that should be checked on real controllers.

## Test Signals

Test immediate and regular descriptors for broadcast CCC, directed CCC, private I3C, and legacy I2C. Exercise DAA with no devices, one device, multiple devices, DAT exhaustion, DCT readback, and non-success response status. Hardware tests should verify DAT slots are freed after DAA failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v2.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v2.c

## Purpose

`cmd_v2.c` implements command descriptor preparation for MIPI I3C HCI v2.0. It uses v2 unified transfer descriptors, address-assignment descriptors, explicit dynamic addresses instead of v1 DAT indexes for normal transfers, and v2 transfer mode/rate selector definitions.

## Important APIs, Types, and Functions

- Unified descriptor macros `CMD_U*` encode device address, transfer rate, mode index, ID bytes, read/write, data length, and TID across four descriptor words.
- Address assignment macros `CMD_A*` encode v2 DAA read-ID and assign-address commands.
- `get_i3c_rate_idx()` and `get_i2c_rate_idx()` select rate IDs from the bus SCL rates.
- `hci_cmd_v2_prep_private_xfer()` prepares private I3C/I2C descriptors and packs up to five write bytes as immediate data bytes.
- `hci_cmd_v2_prep_ccc()` handles normal and raw CCC framing, including the NXP raw CCC quirk path for directed CCCs.
- `hci_cmd_v2_daa()` performs two-command DAA: read device ID then assign address.

## Control Flow

Private transfer preparation selects mode `XFERMODE_IDX_I3C_SDR` or `XFERMODE_IDX_I2C`, computes the rate index, assigns a TID, and emits either an immediate-data unified command or a data-buffer unified command. CCC preparation uses broadcast or directed CCC address fields directly. For raw directed CCCs, it delegates to private transfer preparation so the CCC byte is treated as part of the caller payload. For non-raw or broadcast CCCs, it inserts the CCC command byte into IDB0 and adjusts IDB count.

DAA allocates two `hci_xfer` entries. The first reads eight bytes of device ID with an address-assignment descriptor; the second assigns the selected dynamic address. It repeats until the first response is not success, then decodes PID/BCR/DCR from the returned ID words and calls `i3c_master_add_i3c_dev_locked()`.

## State and Persistence Behavior

Unlike v1 normal transfers, v2 descriptors use addresses directly and do not depend on per-device DAT indexes for command addressing. Transfer descriptors and response fields are per-xfer. DAA keeps a stack `device_id` buffer for each loop iteration and no persistent local allocation beyond the temporary xfer array.

## Dependencies and Integration Points

It includes `xfer_mode_rate.h` for mode/rate IDs, `cmd.h` for common response/TID fields, and core I3C helpers for address allocation and device registration. The implementation is selected by `core.c` when `HC_CAP_CMD_SIZE` advertises v2 descriptors.

## Risks and Edge Cases

The file explicitly notes that v2.0 spec details were in flux. Immediate CCC IDB count differs for raw and non-raw modes and should be validated against hardware. DAA treats any non-success first response as normal completion, which may hide unexpected bus errors. The two-command DAA sequence relies on both responses arriving and matching the issued TIDs.

## Test Signals

Validate descriptor fields for I3C/I2C rates, immediate writes up to five bytes, longer reads/writes, raw directed CCCs, and broadcast CCCs. DAA tests should cover successful read-ID/assign pairs, no-device completion, assignment failure, and PID/BCR/DCR decoding from returned words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/core.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/core.c

## Purpose

`core.c` is the main MIPI I3C HCI platform driver and the integration layer between HCI hardware and the Linux I3C master framework. It probes HCI capabilities, maps table/register sections, parses extended capabilities, selects v1/v2 command descriptors and DMA/PIO I/O mode, implements `i3c_master_controller_ops`, handles top-level interrupts, and provides runtime/system PM flows.

## Important APIs, Types, and Functions

- Register definitions cover HCI version, control, capabilities, reset, DAT/DCT/PIO/RHS/extended-cap sections, interrupt registers, and master dynamic address.
- `i3c_hci_bus_init()` initializes DAT when needed, assigns the master dynamic address, starts the selected I/O backend, applies AMD response-threshold quirks, enables IRQ activity, and enables the bus with Hot-Join disabled.
- `i3c_hci_process_xfer()` queues transfers through `hci->io`, waits for completion, attempts dequeue on timeout, and delegates backend error recovery.
- CCC/private transfer callbacks (`i3c_hci_send_ccc_cmd()`, `i3c_hci_i3c_xfers()`, `i3c_hci_i2c_xfers()`) allocate `hci_xfer` arrays, call command preparation, set `ROC/TOC`, and decode responses.
- Device attach/detach callbacks allocate `struct i3c_hci_dev_data`, manage v1 DAT entries, and configure I2C/static/dynamic address table fields.
- IBI callbacks update DAT SIR/payload flags and delegate pool management to the chosen I/O backend.
- `i3c_hci_init()` validates HCI version, discovers sections, parses ext caps, selects command model, applies quirks, and calls reset/init.
- PM exports `i3c_hci_rpm_suspend()` and `i3c_hci_rpm_resume()` are used by PCI parent glue.

## Control Flow

Probe allocates `struct i3c_hci`, maps base registers either from platform data or a platform resource, records quirk data, initializes the hardware, requests a shared IRQ, configures runtime PM flags, and registers the I3C master. Hardware initialization validates versions 1.0, 1.1, and 2.0, reads capability and table-section registers, computes DAT/DCT entry counts, discovers RHS/PIO/ext-cap offsets, parses extended capabilities, selects command ops from `HC_CAP_CMD_SIZE`, forces PIO for AMD if requested, resets the controller, sets endian mode, and chooses DMA first when RHS exists or PIO otherwise.

During normal transfers, the I3C core callback prepares an `hci_xfer` list. The selected command ops fill descriptors and TIDs. The core adds response and termination flags, queues the list to the selected I/O backend, waits on the last transfer completion, and checks response statuses. The top-level IRQ handler acknowledges HCI core interrupt status under `hci->lock`, filters inactive shared IRQ calls, logs host-controller errors, then calls the backend IRQ handler.

## State and Persistence Behavior

`struct i3c_hci` stores MMIO section pointers, capability/version fields, command and I/O vtables, DAT/DCT metadata, cached DAT entries, current master dynamic address, quirk flags, IRQ active state, and backend private data. DAT entries persist across attached devices and are restored on runtime resume. `irq_inactive` prevents shared IRQ handling while the controller is suspended or not expected to interrupt.

## Dependencies and Integration Points

The file integrates with the Linux platform driver, I3C master framework, runtime PM, IRQ subsystem, HCI PIO/DMA backends, v1/v2 command implementations, DAT support, extended capability parsing, and PCI glue through exported RPM functions. It also uses platform data for multi-instance PCI children that share a parent MMIO mapping.

## Risks and Edge Cases

Transfer length limit is derived from `HC_CAP_MAX_DATA_LENGTH`; callers at or above the limit fail with `-EFBIG`. `i3c_hci_request_ibi()` assumes v1-style DAT-backed device data and would need review for pure v2 DAT-less operation. Runtime resume unconditionally restores v1 DAT state, so future non-v1 paths need care. Shared IRQ handling depends on precise `irq_inactive` updates around suspend/resume. Hardware reset and bus disable failures can leave the backend with stale queue state.

## Test Signals

Probe tests should cover HCI versions, command size values, DMA/PIO selection, endian toggling, and quirk match data. Transfer tests should verify CCC, I3C, I2C, timeout/dequeue, and response error paths on both PIO and DMA. PM tests should suspend/resume with attached devices, restore DAT, keep shared IRQs quiet while inactive, and run DAA after system resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat.h

## Purpose

`dat.h` defines the shared Device Address Table interface for the HCI driver. It names common DAT flags and declares a vtable for allocation, address programming, flag mutation, lookup, and restore operations.

## Important APIs, Types, and Functions

- `DAT_0_I2C_DEVICE`, `DAT_0_SIR_REJECT`, and `DAT_0_IBI_PAYLOAD` are global DAT word-0 flags used by core attach and IBI control.
- `struct hci_dat_ops` provides `init`, `alloc_entry`, `free_entry`, `set_dynamic_addr`, `set_static_addr`, `set_flags`, `clear_flags`, `get_index`, and `restore`.
- `mipi_i3c_hci_dat_v1` is the concrete v1 DAT implementation.

## Control Flow

Core code calls the v1 operations when HCI v1 descriptors require device indexes rather than direct addresses. Attach paths allocate and program entries; CCC preparation can look up a directed address; IBI enable/disable and request paths mutate flags; runtime resume restores cached entries.

## State and Persistence Behavior

The header describes operations over `hci->DAT`, `hci->DAT_data`, and MMIO `hci->DAT_regs`; actual storage is owned by `struct i3c_hci` and implemented in `dat_v1.c`.

## Dependencies and Integration Points

It depends on `struct i3c_hci` and `struct dat_words` from `hci.h`. It is used by `core.c`, `cmd_v1.c`, and `dat_v1.c`.

## Risks and Edge Cases

The API is index-based and assumes the implementation has initialized DAT metadata before callers allocate or look up entries. v2 direct-address command flow reduces DAT usage, so call sites must avoid assuming DAT exists in all HCI modes.

## Test Signals

Attach/detach tests should confirm entry allocation and freeing. IBI tests should verify SIR reject and payload flags. Resume tests should confirm cached DAT words are written back to hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat_v1.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat_v1.c

## Purpose

`dat_v1.c` implements the v1 HCI Device Address Table as cached 8-byte entries mirrored to MMIO. It provides slot allocation, dynamic/static address programming, flag mutation, address lookup, and runtime restore support.

## Important APIs, Types, and Functions

- DAT field macros describe auto-command fields, NACK retry, ring ID, dynamic address/parity, timestamp, master-request/SIR reject, IBI payload, and static address fields.
- `hci_dat_v1_init()` validates register-backed 8-byte DAT support, allocates the cache array and allocation bitmap, and clears hardware entries.
- `hci_dat_v1_alloc_entry()` finds a free bit, marks it, and initializes default reject flags (`SIR_REJECT | MR_REJECT`).
- `hci_dat_v1_free_entry()` clears cached/hardware words and releases the bitmap slot.
- `hci_dat_v1_set_dynamic_addr()` writes the dynamic address and parity bit.
- `hci_dat_v1_set_static_addr()`, `set_flags()`, `clear_flags()`, `get_index()`, and `restore()` provide the remaining vtable operations.

## Control Flow

Initialization occurs during bus init or lazily on first allocation. Allocation scans the bitmap with `find_first_zero_bit()`, writes default flags, and returns the DAT index to per-device data. Address setters read the cached word, update only the relevant fields, and write through to MMIO. `get_index()` scans allocated entries for a matching dynamic address. `restore()` iterates all cached entries and rewrites both words after controller reset.

## State and Persistence Behavior

`hci->DAT` is the persistent software mirror of hardware DAT words. `hci->DAT_data` is the allocation bitmap. Both are devm-managed and survive controller runtime resets, allowing `restore()` to repopulate hardware.

## Dependencies and Integration Points

The implementation uses Linux bitmap helpers, device-managed allocation, `parity8()`, and MMIO `writel()`. It is used by v1 command preparation, core attach/detach, IBI flag control, DAA, and runtime resume.

## Risks and Edge Cases

Only register-space DAT with 8-byte entries is supported; other HCI DAT storage formats return `-EOPNOTSUPP`. `get_index()` assumes `DAT_data` is initialized. The parity bit uses inverted parity semantics from the HCI format and must not be simplified without spec review. Concurrent DAT mutations rely on higher-level I3C core serialization; this file has no local lock.

## Test Signals

Test DAT init rejection for missing/non-8-byte DAT, bitmap exhaustion, default reject flags, dynamic parity encoding, static I2C entries, set/clear flag preservation, directed address lookup, and restore after simulated hardware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dat_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct.h

## Purpose

`dct.h` declares the HCI Device Characteristic Table read helper used by v1 DAA to retrieve newly assigned device identity fields.

## Important APIs, Types, and Functions

- `i3c_hci_dct_get_val(struct i3c_hci *hci, unsigned int dct_idx, u64 *pid, unsigned int *dcr, unsigned int *bcr)` reads one DCT entry and returns PID, DCR, and BCR.

## Control Flow

The v1 DAA path resets the DCT index, performs address assignment, then calls this helper on DCT index 0 to decode the device that just participated.

## State and Persistence Behavior

The header owns no state. It exposes read-only access to hardware DCT contents through `hci->DCT_regs`.

## Dependencies and Integration Points

It depends on `struct i3c_hci` from `hci.h` and is implemented by `dct_v1.c`. Its main consumer is `cmd_v1.c`.

## Risks and Edge Cases

Callers must ensure the DCT section exists and contains the requested index. The function contract has no explicit error return, so invalid hardware state would surface as decoded garbage or MMIO faults.

## Test Signals

DAA tests should validate PID/BCR/DCR decoding for known DCT words and ensure callers reset the DCT index before reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct_v1.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct_v1.c

## Purpose

`dct_v1.c` implements the single exported helper for reading HCI Device Characteristic Table entries. It decodes the identity data captured by hardware during DAA.

## Important APIs, Types, and Functions

- `i3c_hci_dct_get_val()` reads four 32-bit words at `hci->DCT_regs + dct_idx * 16`.
- It decodes PID from DCT word 0 plus bits 47:32 in word 1, DCR from word 2 bits 71:64, and BCR from word 2 bits 79:72.

## Control Flow

The function performs four consecutive `readl()` operations, then applies `FIELD_GET()` with the HCI word-aware masks from `hci.h`. It writes decoded values through caller-provided output pointers and returns no status.

## State and Persistence Behavior

No software state is stored. Hardware DCT state is consumed as a snapshot at the time of the call.

## Dependencies and Integration Points

It uses Linux MMIO reads and bitfield helpers. It is used by the v1 command DAA implementation for debug logging and potential future identity handoff to the I3C core.

## Risks and Edge Cases

There is no bounds or NULL check for `DCT_regs` or the output pointers. The caller must ensure the table is present, the index is valid, and hardware has populated the entry.

## Test Signals

Unit-style tests can feed known MMIO values through an emulated register area and verify PID/BCR/DCR extraction. Integration tests should compare DCT values with the device information later obtained by the I3C core after DAA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dma.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dma.c

## Purpose

`dma.c` implements the HCI DMA/ring-header I/O backend. It allocates command/response rings and IBI status/data rings, maps transfer buffers with the DMA API, queues descriptors into ring memory, processes completion and IBI interrupts, supports abort/dequeue recovery, and provides suspend/resume hooks for the core.

## Important APIs, Types, and Functions

- `struct hci_rh_data` represents one ring header: MMIO regs, coherent command/response/status memory, mapped IBI data memory, ring sizes, pointers, source-xfer mapping, and operation completion.
- `struct hci_rings_data` owns the DMA-capable system device and all ring headers.
- `hci_dma_init()` discovers ring count, chooses the DMA device (PCI parent when present), allocates coherent rings and IBI buffers, maps IBI data, and initializes hardware rings.
- `hci_dma_queue_xfer()` maps transfer data, writes command descriptors and data buffer descriptors to ring entries, stores source xfer pointers, and advances enqueue pointers.
- `hci_dma_dequeue_xfer()` aborts a running ring, replaces pending descriptors with no-op internal-control descriptors, unmaps buffers, and restarts the ring.
- `hci_dma_xfer_done()` consumes response ring entries, validates TID, unmaps data, stores responses, completes waiters, and updates software dequeue pointers.
- `hci_dma_process_ibi()` assembles IBI payloads from status and chunk rings and queues generic IBI slots.
- `mipi_i3c_hci_dma` exports the backend vtable.

## Control Flow

Initialization disables any old state, allocates software ring structures, reads hardware descriptor sizes, allocates coherent command/response/status rings, allocates and maps the IBI data chunk ring, registers a devm cleanup action, then writes base addresses and setup registers. Transfer queueing maps each data buffer, checks ring space under `hci->lock`, writes v1 or v2 descriptors, writes block size/IOC and DMA address fields, records each source xfer by ring entry, and updates `RING_OPERATION1.CR_ENQ_PTR`.

IRQ handling loops over rings. IBI-ready status calls `hci_dma_process_ibi()`. Transfer completion or transfer error calls `hci_dma_xfer_done()`, which drains all hardware-dequeued responses until `done_ptr == CR_DEQ_PTR`. Ring-operation status completes abort waiters. IBI processing scans status descriptors until a `LAST_STATUS` segment is found, validates address consistency and payload length, copies possibly wrapped chunk data into a generic IBI slot, advances IBI dequeue and chunk pointers, and releases chunks to hardware.

## State and Persistence Behavior

Ring memory and source-xfer arrays persist for the device lifetime and are freed by `hci_dma_free()`. Ring runtime pointers (`done_ptr`, `ibi_chunk_ptr`, `xfer_space`) are reset on init/resume. Individual `hci_xfer` objects remember their ring number and entry until completion or dequeue clears them.

## Dependencies and Integration Points

The backend depends on the HCI core for locking, resume signaling, and command descriptor format. It uses DMA mapping helpers from the I3C core (`i3c_master_dma_map_single()`), generic IBI pools, Linux coherent DMA APIs, and PCI parent detection for correct IOMMU context.

## Risks and Edge Cases

Only ring 0 is used despite possible hardware support for more rings. Ring abort failure logs a critical warning because hardware might still write memory. IBI zero-copy is avoided; payloads are copied due to ring wrap and delayed recycle issues. Short read buffers with IOMMU mapping can need bounce buffering when length is not word-aligned. TID mismatch is logged but not otherwise recovered in completion processing.

## Test Signals

Exercise DMA probe on platform and PCI-backed devices, ring-size boundary failures, queue full (`-EBUSY`), descriptor contents for v1/v2, timeout abort/dequeue, response TID mismatch, transfer-error recovery, IBI payload wraparound, oversized/unknown-device IBI drops, suspend/resume ring reinitialization, and DMA unmap leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.c

## Purpose

`ext_caps.c` parses the MIPI I3C HCI extended capability area. It records vendor identity, validates master-mode support, logs optional transfer mode/rate capabilities, captures base pointers for auto-command and debug sections, handles known standard capability IDs, and supports a small vendor-specific parser table.

## Important APIs, Types, and Functions

- Capability header fields `CAP_HEADER_LENGTH` and `CAP_HEADER_ID` drive table walking.
- Standard parsers include hardware ID, master config, multi-bus, transfer modes, transfer rates, auto-command, debug, scheduled command, non-current master, CCC response config, global DAT, and multilane capability handlers.
- `struct hci_ext_caps` and `EXT_CAP()` define standard capability metadata and minimum lengths.
- `hci_extcap_hardware_id()` stores vendor MIPI/version/product IDs and sets the raw CCC quirk for NXP.
- `hci_extcap_vendor_specific()` dispatches vendor capabilities, currently NXP cap `0xc0`.
- `i3c_hci_parse_ext_caps()` is the exported parser called by core initialization.

## Control Flow

The parser starts at `hci->EXTCAPS_regs` and walks until a zero ID/length or a fixed 0x1000-byte guard limit. Each header is decoded and checked so `curr_cap + cap_length * 4` stays under the guard. Vendor IDs `0xc0..0xcf` are matched against the vendor-specific table. Standard IDs are looked up in `ext_capabilities`; unknown capabilities are ignored with debug logging, too-short known capabilities fail with `-EINVAL`, and recognized parsers may record state or reject unsupported modes.

## State and Persistence Behavior

The parser persists vendor identity in `hci->vendor_mipi_id`, `vendor_version_id`, and `vendor_product_id`, may set `hci->quirks`, and stores MMIO base pointers in `AUTOCMD_regs`, `DEBUG_regs`, and `vendor_data`. Most other capabilities are only logged.

## Dependencies and Integration Points

It depends on HCI core state, `ext_caps.h` vendor IDs, transfer mode/rate bit definitions, MMIO reads/writes, and device logging. Core calls it before selecting descriptors and I/O mode so quirks can affect initialization.

## Risks and Edge Cases

The 0x1000-byte limit is arbitrary. Some parsers are placeholders and do not enforce all advertised capability constraints. The NXP vendor parser writes `0xdeadbeef` to a vendor register to reset an FPGA, which is highly device-specific. Operation mode accepts any mode with bit 0 set and rejects target-only operation.

## Test Signals

Feed synthetic ext-cap blocks with zero terminators, unknown IDs, too-short lengths, vendor IDs before/after hardware ID, master-only and target-only modes, rate/mode tables, and bounds at the 0x1000 limit. Hardware tests should verify NXP raw CCC quirk behavior and auto-command/debug base capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.h

## Purpose

`ext_caps.h` exposes the extended capability parser and shared vendor ID constants for the MIPI I3C HCI driver.

## Important APIs, Types, and Functions

- `MIPI_VENDOR_NXP` defines the NXP MIPI vendor ID used by the hardware-ID and vendor-specific capability parsers.
- `i3c_hci_parse_ext_caps()` parses `hci->EXTCAPS_regs` and updates `struct i3c_hci` capability-derived fields.

## Control Flow

Core initialization calls the parser after discovering the extended capability section and before final command/I/O mode setup.

## State and Persistence Behavior

The header has no storage. The parser it declares persists vendor IDs, quirk flags, and optional capability register bases in `struct i3c_hci`.

## Dependencies and Integration Points

It depends on `struct i3c_hci` from `hci.h` and is included by `core.c` and `ext_caps.c`.

## Risks and Edge Cases

Adding vendor-specific support requires keeping IDs and parser tables synchronized. Unknown vendors must remain harmless unless a parser explicitly claims them.

## Test Signals

Build coverage should catch parser signature drift. Ext-cap tests should validate that NXP hardware ID sets `HCI_QUIRK_RAW_CCC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ext_caps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci.h

## Purpose

`hci.h` is the central internal header for the MIPI I3C HCI driver. It defines register bit helpers, MMIO access macros, the main controller structure, the transfer structure shared by command and I/O backends, backend operation vtables, per-device private data, quirk flags, and cross-file function declarations.

## Important APIs, Types, and Functions

- `W0_MASK` through `W3_MASK` and `W*_BIT_` adapt 128-bit descriptor bit positions to 32-bit descriptor words.
- `reg_read()`, `reg_write()`, `reg_set()`, and `reg_clear()` are core-register MMIO helpers assuming a local `hci` variable.
- `struct i3c_hci` persists all core controller state: `i3c_master_controller`, MMIO sections, selected `hci_io_ops`/`hci_cmd_ops`, locks, TID counter, quirks, DAT/DCT metadata, HCI version/vendor IDs, and vendor data.
- `struct hci_xfer` represents a master transfer descriptor plus response, payload, completion, timeout, and backend-specific PIO or DMA linkage.
- `struct hci_io_ops` abstracts PIO and DMA operations including queue/dequeue/error, IBI pool operations, init/cleanup, and PM hooks.
- `struct i3c_hci_dev_data` stores per-device DAT index and IBI backend data.
- Quirk bits model raw CCC, AMD PIO/timing/threshold needs, and runtime PM behavior.

## Control Flow

Core code allocates `hci_xfer` arrays with `hci_alloc_xfer()`, command ops fill descriptors, and I/O ops consume the same structure for queueing and completion. The selected backend stores either PIO linked-list fields or DMA ring fields in the union. Attach callbacks store `i3c_hci_dev_data` on I3C/I2C descriptors, making DAT and IBI state available to later command and IBI paths.

## State and Persistence Behavior

`struct i3c_hci` is device-lifetime state. Its DAT cache and backend `io_data` survive across transfer calls and are restored or reinitialized across PM transitions. `struct hci_xfer` is request-lifetime state and must remain valid until the backend completes or dequeues it.

## Dependencies and Integration Points

The header is included by every HCI implementation file. It integrates with Linux I3C master structures, completions, spinlocks, mutexes, atomic counters, MMIO APIs, PIO/DMA backends, PCI glue PM exports, and AMD quirk helpers.

## Risks and Edge Cases

The PIO/DMA union means a transfer cannot be owned by both backends. MMIO helper macros depend on local variable naming. Device-data `dat_idx` is meaningful mainly for v1 descriptors, so users must account for v2. Quirk combinations affect initialization and PM behavior across several files.

## Test Signals

Compile-time tests should catch structure member drift across all HCI files. Runtime signals include correct backend selection, transfer completion with both union layouts, DAT persistence, quirk-specific register writes, and shared IRQ inactive synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci_quirks.c

## Purpose

`hci_quirks.c` contains hardware-specific register programming for AMD MIPI I3C HCI platforms. It adjusts open-drain/push-pull timing registers and response-buffer threshold behavior when matching quirks are set.

## Important APIs, Types, and Functions

- AMD timing constants program 9 MHz-related values into `HCI_SCL_I3C_OD_TIMING` and `HCI_SCL_I3C_PP_TIMING`.
- `amd_set_od_pp_timing(struct i3c_hci *hci)` writes OD/PP timing registers and sets the SDA hold/switch delay timing field to the maximum TX hold value.
- `amd_set_resp_buf_thld(struct i3c_hci *hci)` accesses `QUEUE_THLD_CTRL` through the core register helper and clears the response-buffer threshold field.

## Control Flow

Core initialization calls `amd_set_od_pp_timing()` after reset/init if `HCI_QUIRK_OD_PP_TIMING` is set. Bus init calls `amd_set_resp_buf_thld()` if `HCI_QUIRK_RESP_BUF_THLD` is set, after backend initialization has made PIO registers available.

## State and Persistence Behavior

The functions directly mutate hardware registers. The timing values are not cached in software and must be reapplied after resets, which core does during init/resume through the quirk path.

## Dependencies and Integration Points

The file depends on `hci.h` for controller state and is selected through ACPI match data in `core.c` for AMD IDs. It assumes the relevant AMD register offsets are valid for matched hardware.

## Risks and Edge Cases

These writes are platform-specific and bypass generic capability-derived timing calculation. `amd_set_resp_buf_thld()` assumes the AMD threshold register is reachable at the hard-coded core-space offset. Register offsets must track vendor hardware revisions.

## Test Signals

On AMD-matched systems, verify timing registers after probe and resume, response threshold behavior with one response available, and no register writes on non-quirked platforms. Regression tests should cover ACPI quirk matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ibi.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ibi.h

## Purpose

`ibi.h` defines HCI In-Band Interrupt status descriptor bits and provides a helper to map an IBI target address to a Linux I3C device descriptor.

## Important APIs, Types, and Functions

- `IBI_STS`, `IBI_ERROR`, `IBI_STATUS_TYPE`, `IBI_HW_CONTEXT`, `IBI_TS`, `IBI_LAST_STATUS`, `IBI_CHUNKS`, `IBI_ID`, `IBI_TARGET_ADDR`, `IBI_TARGET_RNW`, and `IBI_DATA_LENGTH` decode IBI status words.
- `i3c_hci_addr_to_dev()` iterates the current I3C bus and returns the device whose dynamic address matches the supplied address.

## Control Flow

PIO and DMA IBI handlers decode target addresses from IBI status descriptors, call `i3c_hci_addr_to_dev()`, then use the returned descriptor to allocate/queue generic IBI slots or drop unknown-device interrupts.

## State and Persistence Behavior

The helper reads the current I3C bus device list and stores no state. It depends on device dynamic addresses being current after DAA or reattach.

## Dependencies and Integration Points

It depends on the Linux I3C bus iteration macros and `struct i3c_hci`. It is included by both PIO and DMA backend implementations.

## Risks and Edge Cases

Lookup is linear across bus devices. If an IBI arrives while device attach/detach or address change is in progress, higher-level locking must keep the bus list stable. Unknown addresses are normal for stale or rejected IBIs and must be handled by callers.

## Test Signals

IBI tests should cover known device lookup, unknown address drops, address changes after DAA, and both payload and no-payload IBI status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/ibi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/mipi-i3c-hci-pci.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/mipi-i3c-hci-pci.c

## Purpose

`mipi-i3c-hci-pci.c` is PCI glue for Intel LPSS MIPI I3C HCI controllers. It maps the PCI BAR, performs Intel-specific reset/LTR/debugfs setup, creates one or two platform/MFD child instances of the generic `mipi-i3c-hci` driver, and coordinates parent-managed runtime/system PM for those children.

## Important APIs, Types, and Functions

- `struct mipi_i3c_hci_pci` stores the PCI device, shared base mapping, instance metadata, per-instance operational flags, and vendor private data.
- `struct mipi_i3c_hci_pci_info` describes SoC-specific child instance offsets, IDs, name, count, and PM ownership.
- Intel private registers cover reset and active/idle LTR programming.
- `intel_i3c_init()` sets a 64-bit DMA mask, removes D3 delays, resets the Intel host block, exposes PM QoS latency tolerance, and creates debugfs LTR files.
- `mipi_i3c_hci_pci_add_instances()` builds `mfd_cell` entries with platform data pointing at per-instance base offsets and a shared IRQ.
- Parent PM callbacks call exported `i3c_hci_rpm_suspend()`/`i3c_hci_rpm_resume()` on operational child platform devices.
- The PCI ID table covers Wildcat Lake, Panther Lake, and Nova Lake variants with one or two instances.

## Control Flow

Probe enables the PCI device, sets bus mastering, maps BAR 0, allocates one IRQ vector, selects the `pci_info` from `driver_data`, runs vendor init, adds MFD children, stores driver data, and allows runtime PM. Each child platform device receives `mipi_i3c_hci_platform_data.base_regs` pointing into the shared BAR at the configured instance offset. Remove calls vendor exit, forbids runtime PM, and removes MFD children.

For PM, the parent walks child devices. Suspend iterates in reverse and records children whose HCI bus was operational before calling child RPM suspend. If one suspend fails, previously suspended children are resumed. Resume walks forward and resumes only children recorded as operational, with rollback on failure.

## State and Persistence Behavior

Intel LTR register values are cached in `struct intel_host` and exposed read-only in debugfs. Per-child `operational` flags remember whether the child bus was enabled before parent suspend. Platform data references the shared BAR mapping and remains valid for child lifetime.

## Dependencies and Integration Points

This file integrates PCI, MFD, platform data, debugfs, PM QoS, runtime PM, and the generic HCI platform driver. It depends on `core.c` exporting RPM helpers and on the generic HCI platform driver matching child name `intel-lpss-i3c`.

## Risks and Edge Cases

`mipi_i3c_hci_pci_find_instance()` assigns the first empty instance slot while checking PM state; unexpected child ordering or more than `INST_MAX` children would fail. Parent-managed PM assumes children with disabled bus do not need RPM suspend/resume. Intel reset ignores the poll return value. Cell platform data is passed to `mfd_add_devices()` from scoped allocations, relying on MFD copying `platform_data` by `pdata_size`.

## Test Signals

Test PCI probe/remove, child count/offset/ID per PCI ID, shared IRQ delivery, DMA mask selection with IOMMU, debugfs LTR values, PM QoS writes changing LTR registers, parent suspend/resume rollback, and child HCI transfers after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/mipi-i3c-hci-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/pio.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/pio.c

## Purpose

`pio.c` implements the HCI Programmed I/O backend. It drives command, response, data, and IBI FIFOs through MMIO ports, manages linked software queues of `hci_xfer` objects, services FIFO threshold interrupts, handles PIO error recovery, and provides generic IBI pool integration.

## Important APIs, Types, and Functions

- PIO register macros define command/response/data/IBI ports, queue/data thresholds, queue sizes, PIO interrupt status/enable registers, and FIFO level fields.
- `struct hci_pio_data` stores current and tail pointers for command, RX, TX, and response queues, IBI assembly state, threshold sizes, cached threshold register, and enabled IRQ mask.
- `__hci_pio_init()` configures FIFO thresholds, enables status bits, disables signals, and initializes error IRQ tracking.
- `hci_pio_queue_xfer()` links transfer arrays, initializes data counters, queues them under `hci->lock`, starts command processing, and enables needed IRQs.
- `hci_pio_process_cmd()`, `hci_pio_process_tx()`, `hci_pio_process_rx()`, and `hci_pio_process_resp()` move descriptors/data/responses between software queues and FIFOs.
- `hci_pio_err()` completes or discards pending transfers, resets PIO FIFOs, and resumes the HCI controller after errors.
- IBI helpers assemble segmented payloads from `PIO_IBI_PORT` and queue generic IBI slots.

## Control Flow

Initialization derives RX/TX thresholds from hardware queue sizes, writes threshold registers, and records the maximum IBI threshold. Queueing links xfers through `next_xfer`, sets `data_left`, and if no command is active starts processing immediately. Command processing first queues data buffers so TX data or RX space is ready, queues expected responses for `ROC` descriptors, writes descriptor words to the command queue, and advances to the next xfer.

RX/TX processing drains or fills FIFO words while threshold status permits. Response processing reads response descriptors, checks TID against the expected xfer, stores response, handles trailing or over-read RX data, advances data/response queues, and completes waiters. The IRQ handler filters enabled statuses, services IBI/RX/TX/response/error/command-ready events, acknowledges warnings and errors, updates the signal-enable register, and returns whether it handled work.

## State and Persistence Behavior

PIO queue state persists in `hci->io_data` for backend lifetime. Individual xfers remain caller-owned but are referenced by linked lists until completion or dequeue. IBI slot/payload assembly persists across interrupts until the last segment is queued or dropped. Suspend disables PIO signals and marks IRQ inactive; resume reinitializes thresholds.

## Dependencies and Integration Points

PIO uses command descriptor definitions, response decoding, IBI status bits, generic IBI pools, the HCI core spinlock, and core reset/resume helpers. It supports both v1 two-word and v2 four-word descriptors by checking `hci->cmd`.

## Risks and Edge Cases

The backend performs complex recovery for short reads, over-read data pushed into following RX xfers, partial trailing bytes, and timeout dequeue. `hci_pio_do_tx()` may read a full word from memory for trailing bytes beyond the exact buffer length, relying on harmless over-read. Error recovery is intentionally coarse and resets PIO queues. IBI handling must drain payloads even when no slot is available or an error occurred.

## Test Signals

Exercise immediate and buffered transfers, multi-xfer sequences, short reads, odd-length RX/TX, timeout dequeue before and after command submission, TID mismatch, latency warnings, programming errors, FIFO reset recovery, segmented IBI payloads, no-slot IBI drops, unknown IBI addresses, and suspend/resume threshold reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/pio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/xfer_mode_rate.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/xfer_mode_rate.h

## Purpose

`xfer_mode_rate.h` defines HCI v2 transfer mode table indexes, transfer mode entry bit fields, transfer rate selector IDs, and transfer rate table entry fields. It is the shared vocabulary for parsing extended mode/rate capabilities and creating v2 command descriptors.

## Important APIs, Types, and Functions

- `XFERMODE_IDX_I3C_SDR`, `XFERMODE_IDX_I3C_HDR_DDR`, `XFERMODE_IDX_I3C_HDR_T`, `XFERMODE_IDX_I3C_HDR_BT`, and `XFERMODE_IDX_I2C` identify fixed transfer modes.
- `XFERMODE_*` masks describe supported flag, mode, multilane, and additional-function fields in mode table entries.
- `XFERRATE_I3C_*` and `XFERRATE_I2C_*` constants are descriptor `XFER_RATE` selector values used by `cmd_v2.c`.
- `XFERRATE_*` fields decode data transfer rate table entries, including actual kHz, rate ID, mode ID, and mode-specific data.

## Control Flow

`cmd_v2.c` selects fixed mode indexes and rate selector values from bus SCL rates. `ext_caps.c` parses rate/mode capability tables and logs advertised entries using these definitions.

## State and Persistence Behavior

The header contains constants only. It stores no state and performs no runtime discovery itself.

## Dependencies and Integration Points

It depends on Linux bit macros via includers. It is specific to HCI v2.0 and later.

## Risks and Edge Cases

Mandatory versus optional rates are represented as constants, but current code does not validate that optional advertised tables actually support selected values. Future HDR or multilane support must use the mode/rate tables rather than hard-coded SDR/I2C selections.

## Test Signals

Descriptor tests should verify rate IDs selected by `cmd_v2.c` match requested bus speeds. Ext-cap tests should decode synthetic mode/rate table entries and confirm logged mode IDs and kHz values are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/xfer_mode_rate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/renesas-i3c.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/renesas-i3c.c

## Purpose

`renesas-i3c.c` implements a Renesas I3C controller master driver for RZ-family SoCs. It registers an I3C master, programs bus timing and device address table registers, supports DAA, selected CCCs, private I3C transfers, legacy I2C transfers, interrupt-driven FIFO/response handling, and noirq system suspend/resume.

## Important APIs, Types, and Functions

- Register macros cover protocol mode, bus control, master dynamic address, reset, timing, command/response queues, data FIFO, status/interrupt enables, and per-device `DATBAS` entries.
- `struct renesas_i3c` stores controller state: I3C core object, internal transfer state, address slots, cached I2C/I3C timing registers, clocks/resets, DAT backup, and xfer queue.
- `struct renesas_i3c_xfer` and `struct renesas_i3c_cmd` model one queued transfer and command payload/counters.
- `renesas_i3c_bus_init()` resets hardware, derives clock divisors and standard/extended bit-rate settings, initializes interrupts/FIFOs, assigns the master dynamic address, and registers master info.
- `renesas_i3c_daa()` preprograms DATBAS entries with candidate addresses, issues ENTDAA, and registers newly detected devices.
- `renesas_i3c_send_ccc_cmd()`, `renesas_i3c_i3c_xfers()`, and `renesas_i3c_i2c_xfers()` implement I3C core operations.
- ISR functions handle response, RX, TX, start, stop, transfer-end, and NACK events.

## Control Flow

Probe maps registers, enables clocks, deasserts optional resets, initializes the queue, resets hardware, requests named IRQs, initializes slot state, allocates DAT backup storage, and registers the I3C master. Bus init computes timing from the TCLK rate and requested bus rates, programs bitrate/timing registers, initializes status/interrupt control, assigns the master dynamic address, and sets master info.

I3C and CCC transfers create a one-command xfer, set `internal_state`, build a normal command queue descriptor, optionally prefill TX FIFO for writes larger than four bytes, enqueue the transfer, and wait up to one second. The response ISR decodes response status, reads remaining RX bytes, disables TX/RX interrupts, clears abort/error flags, completes the xfer, and advances the queue. Legacy I2C transfers switch protocol mode, use bus condition registers for START/repeated START/STOP, and let start/RX/TX/TEND/STOP ISRs drive byte-level progress.

## State and Persistence Behavior

Address slots are tracked in `free_pos` and `addrs[]`. Per-device master data stores the slot index. `DATBASn[]` backs up hardware DAT registers during noirq suspend; resume restores reference clock, master dynamic address, DATBAS entries, and common hardware init. `internal_state` guides ISR interpretation of the current transfer.

## Dependencies and Integration Points

The driver depends on platform resources, named IRQs, bulk clocks, optional resets, device tree matches, I3C core helpers, I2C timing parsing, and internal FIFO helpers from `../internals.h`.

## Risks and Edge Cases

IBI, Hot-Join, and target support are explicitly TODO. CCC support is restricted to one destination and an allowlist. `renesas_i3c_i3c_xfers()` allocates one command but loops over `i3c_nxfers`, reusing the same command structure sequentially, so multi-transfer behavior should be tested carefully. Several paths return 0 after transfer loops without propagating `xfer->ret`. I2C flow is byte-interrupt driven and sensitive to NACK/STOP ordering. PM resume restores DAT values but does not rerun full bus init timing calculation.

## Test Signals

Hardware tests should cover bus init at pure and mixed rates, DAA with zero and multiple devices, SETDASA and supported CCC read/write commands, private reads/writes including > FIFO-depth writes, legacy I2C read/write/repeated-start/NACK, named IRQ ordering, timeout dequeue, suspend/resume with attached devices, and unsupported CCC rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/renesas-i3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/svc-i3c-master.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/svc-i3c-master.c

## Purpose

`svc-i3c-master.c` implements the Silvaco dual-role I3C master driver, including support for SDR private transfers, limited HDR-DDR transfers, CCCs, DAA, IBI and Hot-Join handling, I2C transfers, runtime PM, and Nuvoton NPCM845-specific hardware quirks.

## Important APIs, Types, and Functions

- Register macros cover master configuration/control/status, interrupt/status bits, IBI rules, error/warning flags, FIFO data/control, dynamic address, and timing fields.
- `struct svc_i3c_master` stores the I3C core object, MMIO regs, saved PM registers, address/descriptor slots, work item for Hot-Join DAA, clocks, transfer queue, IBI slot tracking, global mutex, quirks, enabled event mask, and cached `MCONFIG`.
- Quirks cover FIFO-empty transfer corruption, false `SLVSTART`, and DAA corruption when `SKEW/ODHPP` are both zero.
- `svc_i3c_master_bus_init()` computes `MCONFIG` timing for pure/mixed bus modes, assigns the master dynamic address, and advertises HDR-DDR capability.
- `svc_i3c_master_do_daa_locked()` drives the hardware ProcessDAA sequence, handles IBI arbitration during DAA, prefills dynamic addresses, copes with address NACKs, and returns discovered addresses.
- `svc_i3c_master_xfer()` is the common low-level SDR/I2C/DDR transfer engine.
- IBI functions implement manual ACK/NACK, payload fetch, generic IBI queueing, and Hot-Join work scheduling.

## Control Flow

Probe obtains match data, maps registers, gets clocks and the fast clock, requests the IRQ with `IRQF_NO_SUSPEND`, initializes queues/locks/IBI slots, enables runtime PM, resets the controller, and registers the I3C master. Bus init resumes the device, derives push-pull/open-drain/I2C timing fields from the fast clock and bus mode, writes `MCONFIG`, assigns a master dynamic address, writes `MDYNADDR`, and stores the timing register for later speed changes.

Transfers allocate a flexible `svc_i3c_xfer`, populate one command per requested xfer, serialize through `master->lock`, enqueue under `xferqueue.lock`, and wait for completion. `svc_i3c_master_start_xfer_locked()` executes queued commands synchronously while holding the spinlock, using `svc_i3c_master_xfer()` to emit START/address, handle IBIWON arbitration, handle NACK retry via repeated START, read/write FIFOs, wait for COMPLETE, then emit STOP or DDR force-exit unless the command is continued.

IBI handling starts from `SLVSTART` IRQ. The ISR clears false events, manually emits broadcast address for arbitration, waits for IBIWON, ACKs or NACKs based on IBI type and enabled events, fetches payload into a generic IBI slot, emits STOP, queues the IBI, or schedules Hot-Join DAA work.

## State and Persistence Behavior

Slot allocation is stored in `free_slots`, `addrs[]`, and `descs[]`; per-device private data stores slot index, IBI slot index, and IBI pool. Runtime suspend saves `MCONFIG` and `MDYNADDR`, disables clocks, and selects pinctrl sleep state. Runtime resume restores clocks, pinctrl default, and saved registers if needed. `enabled_events` combines IBI and Hot-Join enable state and controls `SLVSTART` interrupt masking.

## Dependencies and Integration Points

The driver integrates with platform/OF probing, clock and pinctrl PM APIs, runtime PM, I3C master ops, I2C adapter timeout, generic IBI pools, and the I3C core workqueue for Hot-Join DAA. Device-specific quirks are selected by OF match data.

## Risks and Edge Cases

The low-level transfer path polls while holding `xferqueue.lock` with IRQs disabled in several paths, intentionally minimizing IBI arbitration latency but raising latency concerns. DDR support rejects transfers larger than FIFO capacity minus command overhead. `enabled_events++` for IBI enable mixes counter and bitmask semantics with `SVC_I3C_EVENT_HOTJOIN`; this works only if event bits do not conflict with the count range. IBI max payload is limited to FIFO size. DAA intentionally ignores individual `i3c_master_add_i3c_dev_locked()` return values to avoid address reuse hazards.

## Test Signals

Cover timing calculation in all bus modes, `set_speed()` transitions, DAA with NACK/retry and IBIWON arbitration, Nuvoton quirk paths, SDR private multi-transfer continued sequences, I2C repeated starts, DDR size limits and CRC errors, CCC broadcast/direct flows, IBI with and without payload, Hot-Join work scheduling, runtime suspend/resume register restore, and no lockdep/IRQ-latency regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/svc-i3c-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/idle/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/idle/Kconfig

## Purpose

`drivers/idle/Kconfig` exposes the `INTEL_IDLE` kernel configuration option for the Intel-specific cpuidle driver.

## Important APIs, Types, and Functions

- `config INTEL_IDLE` is a boolean option titled "Cpuidle Driver for Intel Processors".
- It depends on `CPU_IDLE`, `X86`, and `CPU_SUP_INTEL`.
- Help text explains that `intel_idle` uses native Intel hardware idle knowledge and can coexist with `acpi_idle` for unsupported processors.

## Control Flow

Kconfig evaluates dependencies during kernel configuration. When enabled, the Makefile in the same directory builds `intel_idle.o`.

## State and Persistence Behavior

The file defines build-time configuration state only. It does not create runtime state.

## Dependencies and Integration Points

It integrates with the kernel Kconfig system, cpuidle subsystem, x86 architecture selection, and Intel CPU support option. The resulting symbol controls compilation in `drivers/idle/Makefile`.

## Risks and Edge Cases

Incorrect dependencies could expose Intel-specific code on unsupported architectures or hide it on valid systems. Since `acpi_idle` can also be configured, runtime driver selection remains outside this file.

## Test Signals

Configuration tests should verify `INTEL_IDLE` is visible only when all dependencies are enabled and that enabling it causes `intel_idle.o` to be built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/idle/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/idle/Makefile -->
# sources/distributed-fs/ceph-client/drivers/idle/Makefile

## Purpose

`drivers/idle/Makefile` builds idle-driver objects for this directory, currently the Intel cpuidle driver, and applies a compile flag when branch profiling is enabled.

## Important APIs, Types, and Functions

- `ccflags-$(CONFIG_TRACE_BRANCH_PROFILING) += -DDISABLE_BRANCH_PROFILING` disables branch profiling instrumentation for this directory when branch profiling is configured.
- `obj-$(CONFIG_INTEL_IDLE) += intel_idle.o` includes the Intel idle driver object when `INTEL_IDLE` is enabled.

## Control Flow

The kernel build system expands conditional variables from active Kconfig symbols. If trace branch profiling is enabled, compilation receives `-DDISABLE_BRANCH_PROFILING`; if Intel idle is enabled, `intel_idle.o` is added to built objects.

## State and Persistence Behavior

The Makefile has build-time effects only and stores no runtime state.

## Dependencies and Integration Points

It depends on Kbuild conditional variable semantics and the `INTEL_IDLE`/`TRACE_BRANCH_PROFILING` symbols. It integrates with `drivers/idle/Kconfig` and the `intel_idle.c` source in the same directory.

## Risks and Edge Cases

The branch profiling flag is safety-related because the comment notes branch profiling is not `noinstr` safe. Removing or scoping it incorrectly could instrument code that must remain noinstr-safe. Missing `obj-$(CONFIG_INTEL_IDLE)` would silently drop the driver from builds.

## Test Signals

Build with `CONFIG_INTEL_IDLE=y` and verify `intel_idle.o` is compiled. Build with `CONFIG_TRACE_BRANCH_PROFILING=y` and inspect compile commands for `-DDISABLE_BRANCH_PROFILING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/idle/Makefile -->

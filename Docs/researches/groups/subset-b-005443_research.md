# subset-b-005443 Research

Grouped source research for Thunderbolt/USB4 NHI, NVM, path, property, quirk, retimer, sideband-register, and switch management files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c` is the PCI driver for the Thunderbolt/USB4 Native Host Interface. It owns host-controller probing, interrupt setup, NHI DMA rings, NHI mailbox commands, controller quirks, host-router reset, and system/runtime PM handoff to the Thunderbolt domain. The source was read as a complete 1585-line file.

## Important APIs, Types, and Functions

Exported ring APIs are `tb_ring_alloc_tx()`, `tb_ring_alloc_rx()`, `tb_ring_start()`, `tb_ring_stop()`, `tb_ring_free()`, `__tb_ring_enqueue()`, `tb_ring_poll()`, and `tb_ring_poll_complete()`. Firmware mailbox APIs are `nhi_mailbox_cmd()` and `nhi_mailbox_mode()`. Internal ring plumbing includes `ring_write_descriptors()`, `ring_work()`, `ring_interrupt_active()`, `ring_msix()`, `nhi_interrupt_work()`, `ring_request_msix()`, and `nhi_alloc_hop()`. PCI/PM flow is rooted in `nhi_probe()`, `nhi_remove()`, `nhi_init_msi()`, `nhi_reset()`, `nhi_select_cm()`, and the `nhi_pm_ops` callbacks. Static state includes the `host_reset` module parameter and NHI-local quirk bits `QUIRK_AUTO_CLEAR_INT` and `QUIRK_E2E`.

## Control Flow

Probe rejects invalid firmware images, enables the PCI function, maps BAR0, reads `REG_CAPS` for hop count, allocates TX/RX ring pointer arrays, applies quirks, checks DMA protection, optionally resets the host router, initializes MSI-X or MSI, sets a 64-bit DMA mask, runs generation-specific ops, selects either native software connection management or ICM, and finally adds the Thunderbolt domain. Ring allocation builds coherent descriptor memory, optionally requests an MSI-X vector, and reserves a HopID. Starting a ring writes descriptor base/count/options registers, enables raw or frame mode, optionally enables end-to-end flow control, unmasks interrupts, and marks the ring running.

At interrupt time MSI-X handlers clear only the ring-specific source and drive `__ring_interrupt()`, while shared MSI schedules `nhi_interrupt_work()` to scan TX, RX, and RX-overflow notify bitfields. Rings either schedule `ring_work()` for callback-driven completion or call a polling starter and mask the interrupt until `tb_ring_poll_complete()`. `ring_work()` moves completed descriptors from `in_flight` to a local done list, posts queued descriptors, then invokes callbacks outside the spinlock. Stop disables the hardware ring, clears descriptor/options registers, marks queued/in-flight frames canceled, and flushes work.

## State and Persistence Behavior

Runtime state lives in `struct tb_nhi`, per-ring `struct tb_ring`, coherent descriptor arrays, IDA-allocated MSI-X vectors, and PCI/MMIO registers. There is no file-backed persistence. State crosses sleep through PM callbacks that delegate to `tb_domain_*` and optional `tb_nhi_ops`; resume re-enables interrupt throttling and handles controllers that disappear while suspended by setting `going_away`. The `host_reset` module parameter persists for the loaded module lifetime and controls whether v2+ host routers are reset during probe.

## Dependencies and Integration Points

This file integrates with Linux PCI, DMA, IRQ, runtime PM, IOMMU/property APIs, `tb_domain_*`, `tb_probe()`, `icm_probe()`, ACPI native control checks, and generation-specific `icl_nhi_ops`. Register definitions come from `nhi_regs.h`; public IDs/ops come from `nhi.h`; domain and ring data structures come from `tb.h`. Consumers of ring APIs include Thunderbolt control, XDomain, DMA tunnels, and other protocol paths that exchange frames over NHI HopIDs.

## Risks and Edge Cases

High-risk areas are interrupt masking/clearing differences between Intel auto-clear and other routers, the Falcon Ridge E2E HopID workaround, concurrent callback and stop/free ordering, controllers disappearing during suspend, host-router reset timing, and fallback from MSI-X to single MSI. DMA protection detection is heuristic and segment based. Ring callbacks may reenqueue or free frames, so holding frame pointers after callbacks is unsafe. HopID allocation must avoid reserved IDs and must unwind on failures.

## Test Signals

Useful signals include boot/probe on supported PCI IDs, MSI-X and MSI fallback coverage, ring enqueue/completion under TX/RX load, `start_poll` polling users, suspend/resume/runtime PM with connected and disconnected devices, hot-unplug during sleep, `host_reset=0/1`, DMA/IOMMU protection logging, and fault injection around IRQ allocation, DMA allocation, mailbox timeout, and domain add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h` is the local NHI contract for firmware mailbox modes/commands, optional controller-generation hooks, PCI device IDs, and the USB4 PCI class used by the NHI PCI driver. The source was read as a complete 103-line file.

## Important APIs, Types, and Functions

The header defines `enum nhi_fw_mode` (`SAFE`, `AUTH`, endpoint, and connection-manager modes), `enum nhi_mailbox_cmd` for firmware commands such as save devices, disconnect PCIe paths, driver unload, disconnect paths A/B, and allow all devices, and declares `nhi_mailbox_cmd()` and `nhi_mailbox_mode()`. `struct tb_nhi_ops` supplies optional hooks for controller-specific initialization, suspend/resume, runtime suspend/resume, and shutdown. `icl_nhi_ops` is declared as the Ice Lake and later implementation. The rest of the file is an ID catalog for Intel Thunderbolt/USB4 NHI and bridge parts through Panther/Lunar/Barlow Ridge era IDs plus `PCI_CLASS_SERIAL_USB_USB4`.

## Control Flow

This header has no executable control flow. It shapes control flow in `nhi.c` by making per-device `driver_data` point to `tb_nhi_ops`, and by defining mailbox operation values sent through NHI MMIO registers.

## State and Persistence Behavior

No storage is owned here. The enum values are protocol constants, while PCI IDs participate in module device matching for the lifetime of the driver.

## Dependencies and Integration Points

The only direct include is `<linux/thunderbolt.h>`. The header is consumed by `nhi.c`, `nhi_ops.c`, and any local code needing NHI mailbox helpers or PCI IDs. Its PCI ID constants are also referenced by quirk and switch generation logic.

## Risks and Edge Cases

Incorrect PCI IDs break device binding, quirk matching, or generation classification. Changing mailbox numeric values would send the wrong firmware commands. `tb_nhi_ops` hook semantics must stay aligned with `nhi.c` PM ordering: hooks run around domain suspend/resume and must not assume unavailable MMIO or an already resumed domain unless the caller guarantees it.

## Test Signals

Compile coverage for every user of the header, PCI modalias/module table checks, probe tests on each ID class, and PM tests for devices using `icl_nhi_ops` are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c` implements Ice Lake style NHI operations used by integrated Thunderbolt/USB4 controllers. Its main job is force-power sequencing, link-controller mailbox handshakes, LTR programming, and PM/shutdown hooks. The source was read as a complete 185-line file.

## Important APIs, Types, and Functions

The exported object is `icl_nhi_ops`. Internal helpers include `icl_nhi_is_device_connected()`, `icl_nhi_force_power()`, `icl_nhi_lc_mailbox_cmd()`, `icl_nhi_lc_mailbox_cmd_complete()`, `icl_nhi_set_ltr()`, `icl_nhi_suspend()`, `icl_nhi_suspend_noirq()`, `icl_nhi_resume()`, and `icl_nhi_shutdown()`. `ICL_LC_MAILBOX_TIMEOUT` bounds link-controller mailbox waits.

## Control Flow

Initialization and resume call `icl_nhi_resume()`: assert force power via PCI VSEC `VS_CAP_22`, wait for firmware-ready in `VS_CAP_9`, then program snoop/no-snoop LTR from `VS_CAP_16` into `VS_CAP_15`. Runtime suspend checks for connected devices; if none are present and the root switch is ICM-controlled, it sends `ICL_LC_PREPARE_FOR_RESET` through the LC mailbox, waits for `VS_CAP_18_DONE`, then clears force power. System suspend-noirq either follows normal suspend when not firmware-assisted, or sends `GO2SX`/`GO2SX_NO_WAKE` depending on wake requirements. Shutdown clears force power.

## State and Persistence Behavior

State is held in PCI config/VSEC registers, not in heap objects. Force-power and LC mailbox bits persist in controller config space until cleared or reset. The device-connected predicate reads current children under `tb->root_switch->dev`, so behavior changes with the live topology.

## Dependencies and Integration Points

The file depends on PCI config-space accessors, sleep timing, Linux suspend helpers, `nhi.h`, `nhi_regs.h`, and `tb.h`. It is selected from the NHI PCI ID table through `driver_data`, and called by `nhi.c` around domain PM transitions. It also depends on `tb_switch_is_icm()` because the LC mailbox sequence differs for firmware-managed controllers.

## Risks and Edge Cases

Timeouts waiting for `VS_CAP_9_FW_READY` or `VS_CAP_18_DONE` can block probe/resume. The suspend path intentionally skips force power down when devices are connected, so false device detection affects power use. Firmware-assisted suspend only sends LC commands for ICM roots. Misprogramming force-power or DMA-delay fields can leave integrated controllers inaccessible until another power transition.

## Test Signals

Probe and runtime PM on Ice Lake/Tiger Lake/Alder Lake and newer integrated controllers; suspend-to-idle and firmware-assisted sleep with and without connected devices; timeout injection on VSEC ready/done bits; LTR register readback; and shutdown/poweroff tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h` defines the MMIO and PCI VSEC register contract for NHI rings, interrupts, mailbox, reset, firmware status, and Ice Lake link-controller registers. The source was read as a complete 179-line file.

## Important APIs, Types, and Functions

Important definitions include `enum ring_flags`, packed `struct ring_desc`, TX/RX ring base offsets, TX/RX options bases, interrupt notify/mask/clear bases, vector allocation fields, interrupt throttling, `REG_CAPS`, `REG_DMA_MISC`, `REG_RESET`, in/out mailbox registers, firmware status bits, Ice Lake VSEC offsets `VS_CAP_9` through `VS_CAP_22`, and `enum icl_lc_mailbox_cmd`.

## Control Flow

There is no runtime flow in this header. `nhi.c` uses the register constants to program ring descriptors, enable/disable interrupts, allocate MSI-X vectors, read firmware mode, issue mailbox commands, and reset host routers. `nhi_ops.c` uses the VSEC constants for force-power, firmware-ready, LTR, and LC mailbox sequences.

## State and Persistence Behavior

The file describes hardware state. Ring descriptor base/head/tail/count registers, options registers, interrupt status/mask registers, and mailbox bits reflect live controller state. The packed descriptor layout is DMA-visible and must match hardware.

## Dependencies and Integration Points

It includes `<linux/types.h>` and assumes bit helpers such as `BIT()`, `GENMASK()`, and `FIELD_GET()` are available through the wider kernel include context. It depends on `enum ring_desc_flags` being visible through included Thunderbolt headers when `struct ring_desc` is used. It is tightly coupled to NHI hardware documentation and the register accessors in `nhi.c`.

## Risks and Edge Cases

Wrong bit positions or offsets can corrupt DMA rings, mask the wrong interrupt, or wedge firmware mailbox commands. `RING_NOTIFY_REG_COUNT()` and `RING_INTERRUPT_REG_COUNT()` depend on `nhi->hop_count`; off-by-one errors would skip status words. The packed bitfield descriptor has compiler/ABI sensitivity but is in kernel style for this hardware interface.

## Test Signals

Build coverage on supported architectures, ring bring-up on hardware with different hop counts, MSI-X vector allocation readback, mailbox command success/failure paths, host reset on v2+ routers, and Ice Lake force-power/LTR PM tests validate this register contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c` provides generic and vendor-specific Thunderbolt/USB4 NVM helper logic. It allocates `struct tb_nvm`, determines vendor support, reads active NVM versions, validates new images, registers active/non-active nvmem devices, caches writes before authentication, and provides block-oriented read/write helpers for switches and retimers. The source was read as a complete 644-line file.

## Important APIs, Types, and Functions

Vendor dispatch uses `struct tb_nvm_vendor_ops` and `struct tb_nvm_vendor`. Public helpers include `tb_nvm_alloc()`, `tb_nvm_read_version()`, `tb_nvm_validate()`, `tb_nvm_write_headers()`, `tb_nvm_add_active()`, `tb_nvm_write_buf()`, `tb_nvm_add_non_active()`, `tb_nvm_free()`, `tb_nvm_read_data()`, `tb_nvm_write_data()`, and `tb_nvm_exit()`. Intel switch and retimer paths parse `INTEL_NVM_FLASH_SIZE`, `INTEL_NVM_VERSION`, FARB/header offsets, digital section size, and device IDs. ASMedia switch versioning reads date/version offsets and assumes a 512 KiB active image.

## Control Flow

`tb_nvm_alloc()` first determines whether the device is a switch or retimer, matches its vendor against supported tables, allocates a unique ID from `nvm_ida`, and stores the selected ops. Version reading delegates to vendor ops. Validation first checks that a buffer exists and the image is between 32 KiB and 1 MiB, then lets vendor validation adjust `buf_data_start` and `buf_data_size` to skip headers when required. Intel validation checks header pointer bounds, 4 KiB alignment, digital-section size, and device ID unless a switch is in safe mode. Header writing is special for pre-generation-3 Intel switches, where CSS headers are written before the data section.

Nvmem registration exposes `nvm_active` as read-only and `nvm_non_active` as root-only writable. Writes to `nvm_non_active` are buffered by `tb_nvm_write_buf()` and later authenticated by switch or retimer code. Generic `tb_nvm_read_data()` and `tb_nvm_write_data()` split byte-oriented requests into 16-dword blocks, handle unaligned offsets, and retry selected failures.

## State and Persistence Behavior

Persistent hardware state is the device flash, but this file only stages data in memory and registers nvmem devices. `nvm->buf`, `buf_data_size`, `buf_data_start`, `major`, `minor`, `active_size`, `flushed`, and `id` represent current kernel-side state. The global `nvm_ida` persists for the module lifetime and is destroyed by `tb_nvm_exit()`.

## Dependencies and Integration Points

The file depends on `tb.h`, Linux IDA, nvmem provider callbacks, `vmalloc`, and vendor-specific switch/retimer read/write functions supplied by `switch.c`, `retimer.c`, DMA-port code, and USB4 helpers. It is not a standalone updater: actual flash writes/authentication are driven by sysfs flows in switch and retimer code.

## Risks and Edge Cases

Image validation does raw unaligned casts from the uploaded buffer and trusts vendor layout assumptions. `tb_nvm_write_buf()` does not enforce `offset + bytes <= NVM_MAX_SIZE` locally, relying on nvmem bounds. In `tb_nvm_write_data()`, partial unaligned writes need careful scrutiny because `nbytes` includes the offset and the copied region starts at `data + offset`; callers should avoid sizes that produce non-dword write counts. Vendor tables intentionally disable upgrades for unknown vendors. Safe-mode switches skip device-ID matching because active NVM may be inaccessible.

## Test Signals

Nvmem read/write smoke tests, validation tests for too-small/too-large images, bad FARB offsets, misalignment, wrong device ID, Intel generation-2 CSS header writes, ASMedia version parsing, retimer validation, retry behavior for `-ENODEV`/`-ETIMEDOUT`, and memory-leak checks around add/remove are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c` owns Thunderbolt tunnel path discovery, allocation, activation, deactivation, HopID reservation, NFC credit accounting, and path membership checks. The source was read as a complete 618-line file.

## Important APIs, Types, and Functions

Public APIs are `tb_path_discover()`, `tb_path_alloc()`, `tb_path_free()`, `tb_path_deactivate_hop()`, `tb_path_deactivate()`, `tb_path_activate()`, `tb_path_is_invalid()`, and `tb_path_port_on_path()`. Important helpers include `tb_path_find_dst_port()`, `tb_path_find_src_hopid()`, `tb_dump_hop()`, `__tb_path_deactivate_hop()`, `__tb_path_deactivate_hops()`, and `__tb_path_deallocate_nfc()`.

## Control Flow

Discovery follows enabled hop entries from a source port/HopID through path config space until a disabled entry, missing remote port, or `TB_PATH_MAX_HOPS`. It can infer the source HopID by scanning possible source HopIDs until a path ends at the requested destination/HopID. After counting hops, it allocates a flexible `struct tb_path`, optionally reserves exact in/out HopIDs for each discovered hop, records ports and next HopIDs, and marks the path already activated.

Allocation builds a new path between two ports by walking the topology with `tb_next_port_on_path()`, choosing the requested link on non-bonded dual-link segments, reserving the requested source/destination HopIDs and intermediate HopIDs, and filling `path->hops`. Activation runs backward: clear counters, add NFC credits, deactivate any stale hop, populate `struct tb_regs_hop`, set flow-control/shared-buffer bits according to source/internal/destination masks, write hop registers, and unwind written hops/credits on failure. Deactivation clears enable bits, waits for pending to drain, optionally clears flow-control bits, releases NFC credits, and marks the path inactive.

## State and Persistence Behavior

The owned state is heap-allocated `struct tb_path` with flexible hop array plus HopID reservations held in per-port IDAs. Hardware-visible persistent state is the path config space written to each input port. NFC credit changes mutate `port->config.nfc_credits` and hardware `ADP_CS_4` values until reversed.

## Dependencies and Integration Points

The file depends on `tb.h`, port read/write helpers, switch topology helpers from `switch.c`, and constants for path config space. It is used by tunnel builders for PCIe, DisplayPort, USB3, DMA, and XDomain traffic to create hardware routes through the fabric.

## Risks and Edge Cases

Backward activation is intentional to avoid traffic entering an incomplete path; changing order is risky. Failure unwinds must match exactly or leak HopIDs/NFC credits. Incomplete paths are discoverable and callers must validate destination/last port. USB4 and pre-USB4 flow-control clearing differ. Timeout draining disabled hops can leave stale hardware state. Dual-link and bonded/non-bonded transitions can select the wrong lane if link metadata is stale.

## Test Signals

Path allocation/free leak checks, activation/deactivation with injected write failures, discovery of complete and incomplete paths, HopID exhaustion, dual-link lane selection, bonded link transitions, NFC credit accounting, and tunnel-level PCIe/DP/USB3 traffic tests are important validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/property.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/property.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/property.c` implements Thunderbolt XDomain property directory parsing, formatting, copying, mutation, lookup, and iteration. It converts between packed big-endian dword property blocks exchanged over the fabric and in-kernel `tb_property_dir`/`tb_property` lists. The source was read as a complete 770-line file.

## Important APIs, Types, and Functions

Internal packed formats are `struct tb_property_entry`, `struct tb_property_rootdir_entry`, and `struct tb_property_dir_entry`. Public APIs are `tb_property_parse_dir()`, `tb_property_create_dir()`, `tb_property_free_dir()`, `tb_property_format_dir()`, `tb_property_copy_dir()`, `tb_property_add_immediate()`, `tb_property_add_data()`, `tb_property_add_text()`, `tb_property_add_dir()`, `tb_property_remove()`, `tb_property_find()`, and `tb_property_get_next()`. Helpers include `parse_dwdata()`, `format_dwdata()`, `tb_property_entry_valid()`, `tb_property_key_valid()`, `tb_property_alloc()`, `tb_property_parse()`, `__tb_property_parse_dir()`, `tb_property_dir_length()`, and `__tb_property_format_dir()`.

## Control Flow

Parsing starts at a root block, verifies the root magic and length, then recursively parses directory entries. Each property validates bounds according to type, decodes the eight-byte key from big-endian dwords, allocates a property object, and either recurses into a child directory, copies data/text payloads with endian conversion, stores an immediate value, or marks unknown type. Formatting computes directory and payload lengths, lays out root/child headers, writes entries first, writes leaf payloads after entries, and appends child directories after the current directory with padding reserved after directory properties. Passing `NULL` as the format destination returns the required dword count.

Mutation helpers allocate properties, validate key length, copy data/text into dword-padded buffers, append to the parent list, or remove/free entries. `tb_property_copy_dir()` performs a deep copy across nested directories, data, text, and immediates.

## State and Persistence Behavior

All state is heap allocated and list based. The code has no file-backed persistence; packed property blocks persist only in caller-provided memory or on the wire through XDomain protocols. Text properties are forced null-terminated after parsing and padded when formatting.

## Dependencies and Integration Points

The file depends on Linux list/slab/string/UUID helpers and `<linux/thunderbolt.h>` for public property types and sizes. It exports helpers for XDomain service discovery and inter-domain metadata exchange.

## Risks and Edge Cases

Bounds validation is central: directory lengths, entry value+length pairs, and root magic must reject malformed remote input. Text copy in `tb_property_copy_dir()` uses `strcpy()` into a padded buffer sized from stored length, so parsed or constructed text must remain null-terminated. `tb_property_remove()` frees only the property object directly and does not use the recursive/data-aware helper, so removing directory/data/text properties can leak nested allocations unless callers avoid those types or free payloads separately. Unknown property types are preserved only as type unknown without payload.

## Test Signals

Round-trip parse/format tests for nested directories, immediate/data/text properties, endian conversion checks, malformed block fuzzing for bounds failures, key length validation, deep-copy independence, iterator behavior, and leak detection around removal/free are the most relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c` centralizes router-specific workarounds matched by hardware/vendor/device IDs. It mutates `struct tb_switch` fields after switch identification to compensate for known platform or firmware issues. The source was read as a complete 144-line file.

## Important APIs, Types, and Functions

The public function is `tb_check_quirks()`. `struct tb_quirk` describes match fields and a hook. Hooks are `quirk_force_power_link()`, `quirk_dp_credit_allocation()`, `quirk_clx_disable()`, `quirk_usb3_maximum_bandwidth()`, and `quirk_block_rpm_in_redrive()`. The `tb_quirks[]` table covers Dell WD19TB self-authentication, Titan Ridge CLx, Intel Goshen Ridge DP buffer reporting, selected Intel USB4 host/hub bandwidth limits, Barlow Ridge DP redrive runtime PM behavior, and AMD Yellow Carp/Pink Sardine CLx.

## Control Flow

`tb_check_quirks()` scans the table and applies every entry whose nonzero hardware vendor/device and vendor/device fields match the switch. Hooks set switch quirk bits, reduce DP main credits from 56 to 18, disable CL states except for Titan Ridge firmware >= 0x65, cap downstream USB3 max bandwidth on non-ICM routers, or mark DP redrive runtime PM as blocked.

## State and Persistence Behavior

State changes are in-memory fields on `struct tb_switch` and its ports: `sw->quirks`, `sw->min_dp_main_credits`, and `port->max_bw`. They persist until the switch object is removed and are recomputed on rediscovery.

## Dependencies and Integration Points

The file depends on `tb.h` for switch/port helpers and PCI ID constants. It is called from `tb_switch_add()` after DROM/ports are initialized and before later link/tunnel policy relies on those fields.

## Risks and Edge Cases

Quirks can stack because the scan does not stop at first match. ID matching must distinguish NHI IDs, bridge IDs, USB4 vendor IDs, and DROM vendor/device IDs. Incorrectly applying bandwidth or CLx quirks can reduce performance or power savings; failing to apply them can cause unstable links, bad DP allocation, or broken wake/authentication flows.

## Test Signals

Unit-style table match tests, boot logs on affected docks/controllers, DP tunnel allocation on Goshen Ridge, CLx entry/exit on Titan Ridge and AMD platforms, USB3 bandwidth reporting on listed Intel hosts, and runtime PM behavior in Barlow Ridge DP redrive mode are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c` discovers USB4 retimers under ports, registers retimer devices, exposes retimer sysfs attributes, and supports on-board retimer NVM read/write/authentication through USB4 sideband transactions. The source was read as a complete 600-line file.

## Important APIs, Types, and Functions

Public APIs are `tb_retimer_nvm_read()`, `tb_retimer_scan()`, and `tb_retimer_remove_all()`. Device lifecycle helpers include `tb_retimer_add()`, `tb_retimer_remove()`, `tb_port_find_retimer()`, `retimer_match()`, and `tb_retimer_release()`. NVM helpers include `tb_retimer_nvm_add()`, `tb_retimer_nvm_validate_and_write()`, `tb_retimer_nvm_authenticate()`, `nvm_read()`, and `nvm_write()`. Sideband helpers include `tb_retimer_nvm_authenticate_status()`, `tb_retimer_set_inbound_sbtx()`, and `tb_retimer_unset_inbound_sbtx()`. Sysfs exposes `device`, `vendor`, `nvm_version`, and `nvm_authenticate`, with visibility gated by `retimer_is_visible()`.

## Control Flow

Scanning broadcasts retimer enumeration on the USB4 port, immediately samples NVM authentication status, enables inbound sideband transactions, queries each possible retimer index for last/cable status, and registers missing on-board retimers when requested. Cable retimers are skipped. Registration reads vendor/product sideband registers, allocates a `tb_retimer`, determines whether NVM upgrade is allowed by on-board status and sector-size support, registers the device under the USB4 port, adds NVM devices, enables runtime PM, and initializes debugfs.

NVM reads runtime-resume the retimer device, try-lock the domain, call USB4 retimer NVM read, and autosuspend. Writes stage data in `tb_nvm` under the domain lock. Writing `nvm_authenticate` can perform authenticate-only, write-only, or write-and-authenticate. Authentication may make the retimer inaccessible, so inbound sideband transactions are left enabled except on validation/write-only failure paths.

## State and Persistence Behavior

Retimer state lives in registered `struct tb_retimer` devices with vendor/device/index/auth status, `no_nvm_upgrade`, `nvm`, `port`, and domain pointers. NVM images are staged in memory until written/authenticated; firmware flash persists on the retimer after a successful update. Authentication status is captured before old devices disappear and stored in the new retimer object.

## Dependencies and Integration Points

The file depends on USB4 sideband helpers, `sb_regs.h`, `tb.h`, `tb_nvm_*`, runtime PM, device core, sysfs, and debugfs margining. It integrates with switch port lifecycle: `tb_retimer_scan()` runs for USB4 ports, and `tb_retimer_remove_all()` is called during switch removal.

## Risks and Edge Cases

The maximum scanned retimer index is larger when debugfs margining is enabled, otherwise scanning trims to on-board retimers up to `last_idx`. Sideband state must be set/unset according to online/offline port state; authentication deliberately disrupts access. Sysfs operations use `mutex_trylock()` and return `restart_syscall()` to avoid deadlocks. Only on-board retimers support upgrade. Failure to remove reverse child order can leave stale children under USB4 ports.

## Test Signals

Retimer enumeration with zero, on-board, cable, and multiple retimers; NVM sysfs visibility with and without sector-size support; authenticate-only/write-only/write-and-authenticate flows; runtime PM/autosuspend around nvmem reads; sideband transaction failures; hot-unplug removal; and debugfs margining configurations are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/retimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h` defines USB4 sideband register offsets, sideband opcodes, metadata fields, and lane-margining bit masks used for routers and retimers. The source was read as a complete 112-line file.

## Important APIs, Types, and Functions

The header defines sideband registers such as `USB4_SB_VENDOR_ID`, `USB4_SB_PRODUCT_ID`, `USB4_SB_FW_VERSION`, `USB4_SB_OPCODE`, `USB4_SB_METADATA`, `USB4_SB_LINK_CONF`, `USB4_SB_VERSION`, and `USB4_SB_DATA`. `enum usb4_sb_opcode` covers command/status values for errors, online status, router offline, enumerate retimers, inbound SBTX set/unset, last/cable retimer queries, NVM sector/offset/block/auth/read operations, and lane-margining operations. The rest of the file defines capability/result/control masks for hardware and software lane margining.

## Control Flow

There is no executable flow. USB4 sideband accessors use these offsets/opcodes to construct transactions and parse returned metadata/data for retimer discovery, NVM operations, and margining.

## State and Persistence Behavior

The file describes live sideband register state. It does not own memory. Sideband commands may change retimer/router state, NVM offsets, inbound SBTX mode, or margining operation state in hardware.

## Dependencies and Integration Points

The header is included by `retimer.c` and USB4 sideband/margining code. It assumes bit helpers such as `BIT()` and `GENMASK()` are available. It is a protocol contract between the kernel and USB4 sideband targets.

## Risks and Edge Cases

Opcode constants are four-character little-endian command encodings; wrong values can trigger the wrong sideband operation. Margining masks have overlapping per-capability semantics, so code must use the mask set for the specific opcode/result. Metadata `USB4_SB_METADATA_NVM_AUTH_WRITE_MASK` constrains auth-write lengths.

## Test Signals

Sideband read/write tests for vendor/product/version, retimer enumeration, NVM read/write/authentication, inbound SBTX set/unset, and debugfs lane-margining capability/result parsing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c` is the main Thunderbolt/USB4 router and port utility implementation. It manages router allocation/configuration/add/remove, port initialization and adapter control, HopID allocation, link width/bonding/asymmetric links, NVM sysfs/authentication, authorization sysfs, DROM/UUID identity, PM resume/suspend, wake programming, DP resources, retimer removal integration, lookup helpers, and selected generation-specific PCIe/xHCI flows. The source was read as a complete 4038-line file.

## Important APIs, Types, and Functions

Switch lifecycle APIs include `tb_switch_alloc()`, `tb_switch_alloc_safe_mode()`, `tb_switch_configure()`, `tb_switch_configuration_valid()`, `tb_switch_add()`, `tb_switch_remove()`, `tb_sw_set_unplugged()`, `tb_switch_resume()`, and `tb_switch_suspend()`. Port APIs include `tb_port_state()`, `tb_wait_for_port()`, `tb_port_add_nfc_credits()`, `tb_port_clear_counter()`, `tb_port_unlock()`, `tb_port_enable()`, `tb_port_disable()`, HopID alloc/release helpers, `tb_next_port_on_path()`, link speed/generation/width helpers, adapter enable helpers for USB3/PCIe/DP, and DP HPD/hop helpers. Link APIs include `tb_switch_set_link_width()`, `tb_switch_configure_link()`, and `tb_switch_unconfigure_link()`. NVM APIs include `tb_switch_nvm_read()` plus internal authentication/status helpers. Lookup/special APIs include `tb_switch_find_by_link_depth()`, `tb_switch_find_by_uuid()`, `tb_switch_find_by_route()`, `tb_switch_find_port()`, `tb_switch_query_dp_resource()`, `tb_switch_alloc_dp_resource()`, `tb_switch_dealloc_dp_resource()`, `tb_switch_pcie_l1_enable()`, `tb_switch_xhci_connect()`, and `tb_switch_xhci_disconnect()`.

## Control Flow

Allocation unlocks the downstream port for non-root routes, reads switch config space, determines generation, fills route/depth/upstream fields, checks topology depth, allocates and minimally initializes ports/IDAs, discovers VSE capabilities, initializes the device object, and leaves hardware programming to `tb_switch_configure()`. Configuration marks the router enabled, writes USB4 or legacy switch config fields, runs USB4 setup when needed, and enables plug events for legacy routers. Adding a switch first creates any DMA/NVM access path, initializes USB4 credits, reads DROM, sets UUID, initializes all ports, applies quirks, links default dual-lane ports, updates link attributes, initializes CLx/TMU, enables USB4 hotplug, registers the device, adds USB4 child ports and nvmem devices, enables wake/runtime PM, and initializes debugfs.

Removal walks downstream switches and XDomain children, removes retimers for every port, disables plug events if still present, removes NVM and USB4 ports, logs disconnects, and unregisters the device. Resume verifies non-root identity by reading config and UID, reconfigures the switch, handles wake notifications, disables wakes, reinitializes TMU, then recursively resumes surviving downstream routers or marks lost children unplugged. Suspend disables CLx, disables plug events, recursively suspends children, programs wake flags according to runtime/system suspend, and sets USB4 or LC sleep.

Port control reads/writes adapter config space for lane state, NFC credits, USB3/PCIe/DP enable bits, DP HPD, and DP HopIDs. Link width control handles pre-Gen4 bonding, Gen4 dual/asymmetric widths, credit refresh, and userspace change notification. NVM sysfs stages writes through `tb_nvm_write_buf()`, validates/writes flash on authentication, handles USB4 vs DMA-port flashing, and caches authentication status across switch power cycles by UUID.

## State and Persistence Behavior

`struct tb_switch` owns router config, identity, UUID, DROM data, ports, quirks, NVM, DMA port, link attributes, authorization/key state, runtime PM flags, and unplug state. Each port owns config snapshots, capabilities, HopID IDAs, remote/XDomain pointers, dual-link metadata, credits, and bandwidth limits. Hardware-persistent state includes router config space, path registers, link width/bonding state, wake/sleep settings, NVM flash, and authorization side effects mediated by the connection manager. The static `nvm_auth_status_cache` persists authentication failure status by switch UUID beyond switch power cycles while the module remains loaded.

## Dependencies and Integration Points

The file depends on `tb.h`, Linux device/sysfs/runtime PM/nvmem/IDA APIs, DMA-port helpers, DROM code, USB4 router/port helpers, LC helpers, CLx/TMU/debugfs helpers, retimer management, path deactivation, domain approval/disapproval APIs, and connection-manager PM callbacks. It is the central integration point for most higher-level Thunderbolt tunnel managers.

## Risks and Edge Cases

This file has many hardware-ordering risks: NVM authentication can intentionally make routers disappear; host NVM update keeps the PCIe root port in D0; switch add may return `-ESHUTDOWN` after power cycling; safe-mode switches expose only limited NVM paths; plug events differ for ICM/USB4/legacy; UID mismatch on resume means a different device is present; recursive remove/resume must handle already unplugged children; link width changes must keep both ends and credits consistent; Gen4 cannot switch to single lane; sysfs uses `mutex_trylock()` and `restart_syscall()` to avoid domain-lock deadlocks; `switch_attr_is_visible()` hides attributes depending on security, safe mode, route, NVM support, and quirks.

## Test Signals

Validation should cover root and device router add/remove, safe mode, DROM failures, UUID generation from UID/LC, USB4 and legacy config, authorization/key sysfs, NVM active/non-active sysfs and authentication statuses, hotplug plug-event behavior, runtime/system suspend with child routers and XDomain, wake flag programming, link bonding/asymmetric transitions, DP resource allocation, retimer removal, lookup helpers, Titan Ridge PCIe L1 writes, Alpine/Titan Ridge xHCI connect flows, and fault injection around config-space reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c -->

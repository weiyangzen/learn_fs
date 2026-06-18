# Research: subset-b-004590

Grouped research for the Netronome/Corigine NFP CPP, NSP, NIC DCB, and NI Ethernet build entries. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.c

Purpose: Implements the NFP6000/NFP3800 PCIe transport for the generic `nfp_cpp` bus. It multiplexes PCIe BAR apertures into CPP targets, maps reserved CSR/SRAM/explicit regions, and supplies `struct nfp_cpp_operations` callbacks used by `nfp_cppcore.c`.

Important APIs/types/functions: `struct nfp_bar` tracks BAR config, base, aperture mask, refcount, iomem, and PCI resource. `struct nfp6000_pcie` owns PCI device state, BAR lock/waitqueue, reserved mappings, and explicit transaction slot state. `compute_bar()`, `matching_bar()`, `find_unused_bar_noblock()`, and `nfp_alloc_bar()` are the allocation core. `enable_bars()` configures reserved BAR0 slices for MSI-X SRAM, XPB, and explicit access. `nfp6000_area_*()` implements normal CPP area mapping/read/write. `nfp6000_explicit_*()` implements explicit CPP transactions. `nfp_cpp_from_nfp6000_pcie()` is the exported construction path.

Control flow: probe allocates `nfp6000_pcie`, validates the PCI interface encoded in the DSN, calls `enable_bars()`, then creates a generic CPP handle with `nfp_cpp_from_operations()`. Area acquisition first tries an existing compatible BAR, then finds or waits for a free BAR, writes the BAR CSR, computes the physical/iomem offset, and increments private and BAR refcounts. Aligned reads/writes use raw 32/64-bit MMIO; unaligned requests fall back to explicit transactions. Explicit access picks a free group/slot, writes three explicit BAR CSRs, kicks the transaction by reading the mapped address, and exchanges data through the reserved SRAM data window.

State and persistence: State is kernel-resident only: BAR config cache, atomic BAR refcounts, per-area refcounts, wait queues, and explicit slot bitmaps. Hardware-visible state includes PCIe BAR CSR programming and explicit command CSRs. No filesystem persistence is used.

Dependencies/integration: Depends on Linux PCI/MMIO APIs, `nfp_cpp.h` operation contracts, `nfp_dev_info` offsets, and target width decoding from `nfp_target_pushpull()`. It is the low-level backend for all CPP users including resources, NSP, firmware tables, and NIC DCB symbol mapping.

Risks: BAR allocation is concurrency-sensitive; missed refcount drops can starve later CPP users. Incorrect width/action decoding can cause invalid or partial device transactions. Explicit access relies on bounded slot availability and correct signal/data reference calculation. The source snapshot contains duplicated-looking lines in comments/near surrounding copied code, so build validation is an important signal.

Test signals: PCI probe should log NFP card probe, link status, reserved BAR layout, and model information. Exercise `nfp_cpp_readl/writeq`, unaligned explicit reads/writes, resource acquisition, NSP commands, and driver unload to confirm iounmap/refcount cleanup without dangling area warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.h

Purpose: Declares the PCIe-to-CPP constructor for NFP6000-family PCI devices.

Important APIs/types/functions: `nfp_cpp_from_nfp6000_pcie(struct pci_dev *pdev, const struct nfp_dev_info *dev_info)` returns a `struct nfp_cpp *` or `ERR_PTR()`.

Control flow/state: The header has no runtime state. It lets the PCI probe layer pass chip-specific `nfp_dev_info` into the PCIe backend implemented in `nfp6000_pcie.c`.

Dependencies/integration: Includes `nfp_cpp.h` and relies on visible `struct pci_dev` and `struct nfp_dev_info` declarations from users including this header. It connects PCI device discovery to the generic CPP subsystem.

Risks: Signature drift with `nfp6000_pcie.c` or missing forward declarations in include users will break the driver build.

Test signals: Compile coverage of the NFP PCI probe path and successful link of the constructor symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_arm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_arm.h

Purpose: Defines ARM island memory-space offsets, GCSR register offsets, and bitfield helper macros for ARM-side BAR and explicit CPP access configuration.

Important APIs/types/functions: Key macro groups include `NFP_ARM_GCSR_BULK_BAR`, `NFP_ARM_GCSR_EXPA_BAR`, `NFP_ARM_GCSR_EXPL[0-2]_BAR`, `NFP_ARM_GCSR_EXPL_POST`, `NFP_ARM_GCSR_*_CSR()` composers, and fixed sizes such as `NFP_ARM_GCSR_SIZE`, `NFP_ARM_MPCORE_SIZE`, and `NFP_ARM_PCSR_SIZE`.

Control flow/state: Header-only register definitions. Runtime users compose CSR values and decode fields; this file does not allocate or mutate state directly.

Dependencies/integration: Used by CPP core/model detection and any ARM-interface CPP implementation. It shares the same CPP target/action/token semantics as `nfp_cpp.h` and NFP6000 register definitions.

Risks: Bitfield macros directly encode hardware ABI. A wrong shift/mask can route accesses to the wrong target or corrupt explicit transaction setup. Since many macros use plain integer shifts, callers must provide already-sanitized values.

Test signals: Build tests catch syntax only; hardware tests should verify ARM GCSR reads, model autodetection, explicit transaction setup, and BAR CSR composition against known-good hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpp.h

Purpose: Main public/internal interface for low-level NFP CPP bus access. It defines CPP ID packing, interface IDs, area APIs, raw read/write helpers, mutex APIs, explicit transaction APIs, and the backend operation table.

Important APIs/types/functions: Macros `NFP_CPP_ID()`, `NFP_CPP_ISLAND_ID()`, `NFP_CPP_ID_*_of()`, `NFP_CPP_INTERFACE()`, and interface extractors define addressing. `struct nfp_cpp_operations` is the transport vtable. Area APIs include `nfp_cpp_area_alloc*()`, acquire/release, read/write, iomem/resource access, and scalar helpers. Other groups cover XPB access, CPP mutexes, explicit transactions, model detection, and `nfp_cpp_map_area()`.

Control flow/state: The header describes object lifetimes owned by `nfp_cppcore.c`: a CPP handle owns transport state, areas must be acquired before access, explicit handles are acquired/released per transaction sequence, and mutexes represent hardware MU atomic locks.

Dependencies/integration: Included by nearly every nfpcore and NFP NIC file. Backends such as `nfp6000_pcie.c` implement `struct nfp_cpp_operations`; higher layers such as resources, NSP, runtime symbols, and DCB build on these APIs.

Risks: CPP ID and interface packing are contract-critical. The area API allows direct device access, so misuse of alignment, width, or acquire/release ordering can produce hardware faults or BAR leaks. Logging macros assume `nfp_cpp_device(cpp)->parent` is valid.

Test signals: Compile all NFP modules, run probe/unload, exercise scalar and bulk CPP reads/writes, XPB read-modify-write, mutex locking, explicit read/write, and area mapping consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cppcore.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cppcore.c

Purpose: Implements the generic CPP bus object, area lifetime, resource bookkeeping, hot area cache, XPB helpers, model/interface discovery, and explicit transaction wrapper methods.

Important APIs/types/functions: `struct nfp_cpp` embeds a Linux device and owns model/interface/serial, IMB CAT table, resource list, waitqueue, and area cache. `struct nfp_cpp_area` tracks a mapped CPP region and private backend data. `nfp_cpp_from_operations()` constructs the bus from backend ops. `nfp_cpp_area_alloc*()`, `nfp_cpp_area_acquire*()`, `nfp_cpp_area_release*()`, `nfp_cpp_read/write()`, and scalar helpers are core access paths. `area_cache_get/put()` implements LRU cached windows. `nfp_xpb_*()` converts XPB addressing to CPP. `nfp_cpp_explicit_*()` wraps backend explicit operations.

Control flow: Construction initializes locks/lists/device, calls backend init, autodetects model, reads IMB mapping via XPB, and computes MU locality. Normal reads/writes split requests at `NFP_CPP_SAFE_AREA_SIZE` boundaries, use cached acquired areas where possible, otherwise allocate/acquire/release short-lived areas. Area acquisition increments a logical refcount and waits until backend resources are available; final release wakes waiters.

State and persistence: State is in-memory: resource list, area krefs/refcounts, cached area list, IMB table, and embedded device registration. Device state is accessed through backend ops but not persisted by this file.

Dependencies/integration: Depends on `nfp_cpp_operations` backend implementations, target translation from `nfp_target_cpp()`, scalar helpers from `nfp_cpplib.c`, ARM register constants, and Linux device/kref/waitqueue primitives. All nfpcore higher layers use these functions.

Risks: Resource cleanup is delicate; dangling areas are logged and force-cleaned during `nfp_cpp_free()`. Area cache reinitialization must not leak acquired backend windows. Pointer arithmetic on `void *` buffers and copied-source duplicate lines in this snapshot should be compile-checked. XPB island conversion is hardware-specific.

Test signals: Probe should log model, serial, and interface. Stress repeated CPP reads/writes across safe-window boundaries, cached and uncached areas, nonblocking acquire, unload with no dangling area warnings, and XPB read/write on ARM/non-ARM interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cppcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpplib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpplib.c

Purpose: Provides convenience CPP access helpers above `nfp_cpp_read/write()`: little-endian scalar reads/writes, model autodetection, explicit read/write chunking, and area mapping.

Important APIs/types/functions: `nfp_cpp_readl/writel/readq/writeq()` marshal little-endian scalar values. `nfp_cpp_model_autodetect()` reads XPB PL device ID and adjusts NFP6000-family model IDs. `nfp_cpp_explicit_read/write()` acquire an explicit handle, set target/posting, transfer up to 128-byte chunks, and release. `nfp_cpp_map_area()` allocates and acquires a CPP area and returns iomem.

Control flow/state: Scalar helpers perform one bulk CPP transaction and translate short transfers to `-EIO`. Explicit helpers validate length alignment, translate `NFP_CPP_ACTION_RW` to read or write action, calculate byte masks, loop over chunks, and unwind the explicit handle on failure. No persistent state is owned here.

Dependencies/integration: Depends on `nfp_cppcore.c` APIs, explicit backend ops, NFP6000 XPB register constants, Linux unaligned and bitfield helpers. Used throughout resource, NSP, runtime symbol, and NIC code.

Risks: Explicit byte masks are address/width-sensitive; wrong masks can corrupt adjacent bytes. Explicit acquisition can fail under slot pressure. `nfp_cpp_map_area()` returns `ERR_PTR(-EIO)` for several allocation/mapping failures, losing some detail.

Test signals: Validate scalar endian behavior, explicit unaligned read/write fallback from PCIe area code, model autodetect on NFP3800 and NFP6000-family IDs, and map/unmap through `nfp_cpp_area_release_free()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpplib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.c

Purpose: Defines chip-family-specific static parameters for supported NFP PF and VF device IDs.

Important APIs/types/functions: `nfp_dev_info[NFP_DEV_CNT]` supplies DMA masks, queue-controller index/address limits, queue size bounds, PF chip names, PCIe explicit BAR config offsets, explicit data offsets, and queue-controller area sizes.

Control flow/state: No runtime control flow beyond static table access. Values are selected by PCI ID mapping elsewhere and passed into low-level PCIe setup.

Dependencies/integration: Used by PCI probe/transport setup, queue controller allocation code, and `nfp6000_pcie.c` for BAR CSR offsets and explicit data layout.

Risks: Wrong offsets or masks break DMA capability setup, queue controller addressing, or explicit PCIe access. VF entries intentionally omit PF-only fields; callers must avoid using PF-only fields for VFs.

Test signals: Probe each supported PF/VF ID, verify DMA mask setup, queue allocation bounds, and PCIe explicit access on PF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.h

Purpose: Declares supported Netronome/Corigine PCI IDs, the internal `enum nfp_dev_id`, and `struct nfp_dev_info` consumed by probe and low-level transport code.

Important APIs/types/functions: Defines `PCI_VENDOR_ID_CORIGINE`, PF/VF device IDs for NFP3800/NFP4000/NFP5000/NFP6000, `enum nfp_dev_id`, and `extern const struct nfp_dev_info nfp_dev_info[]`.

Control flow/state: Header-only constants and type declarations. Runtime behavior comes from table consumers.

Dependencies/integration: Included by `nfp_dev.c`, PCI probe code, and `nfp6000_pcie.c`.

Risks: Device ID or enum/table order mismatch can select wrong chip parameters. PF-only fields must be treated as unavailable for VF entries.

Test signals: PCI ID table compile/link checks and probe tests confirming the correct `nfp_dev_info` index for each device ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_hwinfo.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_hwinfo.c

Purpose: Reads and validates the firmware-built HWInfo key/value table, then provides lookup and packed-string accessors.

Important APIs/types/functions: `struct nfp_hwinfo` models the v2 header and packed string data. `nfp_hwinfo_read()` fetches and validates the table. `nfp_hwinfo_lookup()` searches unsorted packed `key\0value\0` pairs. `nfp_hwinfo_get_packed_strings()` and `_size()` expose raw packed data.

Control flow: Fetch first tries `NFP_RESOURCE_NFP_HWINFO`; if absent it falls back to a classic MU island address. `hwinfo_fetch()` polls up to `HWINFO_WAIT` while the table is updating or unavailable. Validation checks declared size, POSIX CRC32, and key/value string bounds before returning the allocated table.

State and persistence: Returned table is a heap snapshot of firmware data; caller owns freeing. Persistent data lives on device firmware/scratch memory, not in kernel state.

Dependencies/integration: Uses CPP reads, resource acquisition, CRC32 helper, NFP resource names from `nfp.h`, and logging macros from `nfp_cpp.h`. Higher layers use HWInfo for board policy/defaults.

Risks: Bad firmware tables can fail CRC or bounds checks. The walker must avoid reading past `size`; lookup assumes validated data. Waiting is interruptible and can fail during boot timing issues.

Test signals: Test valid/invalid CRC tables, updating-bit polling, resource-table and classic-location fetch paths, null lookup handling, and boundary cases with unterminated keys/values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_hwinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mip.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mip.c

Purpose: Locates and reads the firmware MIP metadata structure, which points to runtime symbol and string tables.

Important APIs/types/functions: `struct nfp_mip` mirrors firmware metadata including signature, version, symbol table address/size, string table address/size, and name/toolchain. `nfp_mip_open()` returns a copied MIP, `nfp_mip_close()` frees it, `nfp_mip_name()`, `nfp_mip_symtab()`, and `nfp_mip_strtab()` expose fields.

Control flow: `nfp_mip_open()` allocates a MIP buffer, opens NFFW info, finds the first loaded firmware MIP location, reads it via CPP, validates signature/version, terminates the name, and returns it. Errors close the NFFW resource and free memory.

State and persistence: The returned MIP is a heap copy of firmware metadata. Device firmware owns the persistent source; the kernel only snapshots it.

Dependencies/integration: Depends on `nfp_nffw_info_open()`/`nfp_nffw_info_mip_first()` and CPP reads. `nfp_rtsym.c` uses this file to locate runtime symbol tables.

Risks: Only the first loaded firmware MIP is used. Unsupported MIP versions or bad signatures disable runtime symbol access. Table addresses are trusted after MIP validation and are later read from MU.

Test signals: Load firmware with known MIP, verify name and table addresses, test missing/bad MIP signatures, and confirm NFFW lock release on error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mutex.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mutex.c

Purpose: Implements NFP hardware mutexes using MU atomic read/write/test-set operations, keyed by a 32-bit resource key and owned by the current CPP interface ID.

Important APIs/types/functions: `struct nfp_cpp_mutex` tracks CPP handle, MU target, recursion depth, address, and key. Public APIs are `nfp_cpp_mutex_init()`, `_alloc()`, `_free()`, `_lock()`, `_unlock()`, `_trylock()`, and `_reclaim()`.

Control flow: Allocation validates interface/target/address alignment and checks the stored key. `trylock()` verifies the key, performs MU `test_set_imm`, writes the owner if unlocked, and supports recursive locking by the same handle. `lock()` polls `trylock()` with warning/error timeouts. `unlock()` verifies key and owner, writes the unlocked value, and decrements recursion. `reclaim()` clears locks owned by the local interface.

State and persistence: Mutex state is device memory: owner/locked bits and key at a 64-bit MU location. Kernel state is only the handle depth and metadata.

Dependencies/integration: Used by `nfp_resource.c` to serialize resource table and resource entry access. Requires CPP scalar access and MU atomic target semantics from `nfp_target.c`.

Risks: Only MU target and 64-bit aligned addresses are supported. Force reclaim is dangerous if local users still exist. Recursive depth is per handle, not global. Timeout waits are polling-based because unlockers may be remote.

Test signals: Lock/unlock/trylock contention, recursion depth overflow, key mismatch, invalid target/address, timeout warning paths, and resource-table reclaim during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.c

Purpose: Reads the `nfp.nffw` firmware-info resource and finds the MIP address for loaded firmware.

Important APIs/types/functions: Versioned firmware info layouts `nfp_nffw_info_v1/v2`, `struct nffw_fwinfo`, and `struct nfp_nffw_info` model the resource. Public APIs are `nfp_nffw_info_open()`, `_close()`, and `nfp_nffw_info_mip_first()`.

Control flow: Open allocates state, acquires the `NFP_RESOURCE_NFP_NFFW` lock, reads the whole known structure, verifies initialized flag and supported version, then keeps the resource locked until close. MIP lookup chooses the first loaded firmware info entry and returns CPP ID and offset, forcing MU direct access bits when the firmware entry marks MU direct addressing.

State and persistence: Kernel state is a locked resource handle plus copied firmware info. Persistent state lives in the device resource table and firmware-managed NFFW resource.

Dependencies/integration: Uses `nfp_resource_acquire()`, CPP reads, NFP6000 MU locality helpers, and is consumed by `nfp_mip.c`.

Risks: Unsupported future NFFW versions fail open. The file reads `sizeof(*fwinf)` and requires resource size to cover it, which may reject smaller valid future/variant layouts. Only the first loaded firmware is surfaced.

Test signals: Test NFFW v1/v2 initialized resources, uninitialized/future-version failure, loaded-entry selection, MU direct-address adjustment, and lock release on all exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.h

Purpose: Declares firmware metadata, MIP, and runtime symbol table APIs shared across nfpcore and NIC code.

Important APIs/types/functions: Declares `nfp_nffw_info_*`, `nfp_mip_*`, `enum nfp_rtsym_type`, `struct nfp_rtsym`, `struct nfp_rtsym_table`, runtime symbol lookup/read/write/map APIs, and target sentinel values such as `NFP_RTSYM_TARGET_LMEM` and `NFP_RTSYM_TARGET_EMU_CACHE`.

Control flow/state: Header-only API contract. Symbol tables are heap snapshots returned by implementation files; mapped symbols return acquired CPP areas that callers must release.

Dependencies/integration: Used by firmware metadata readers, PF/app code, and DCB mapping through runtime symbols.

Risks: Callers must respect object lifetimes and symbol bounds. Special negative target encodings are not universally mappable; implementation rejects unsupported targets.

Test signals: Compile consumers, read runtime symbol tables after firmware load, map known symbols, and validate scalar read/write helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.c

Purpose: Implements the NFP Service Processor command protocol for firmware loading, flash writing, Ethernet table access, sensor/identify queries, HWInfo operations, version strings, media data, and module EEPROM reads.

Important APIs/types/functions: `struct nfp_nsp` holds CPP, locked NSP resource, ABI version, and Ethernet config staging state. `struct nfp_nsp_command_arg` and `_buf_arg` describe commands. Public APIs include `nfp_nsp_open/close/wait`, reset/MAC/FW commands, HWInfo lookup/set, firmware-loaded query, versions parsing, module EEPROM, media reads, and lower-level Ethernet table read/write functions.

Control flow: `nfp_nsp_open()` acquires `NFP_RESOURCE_NSP` and validates magic/ABI/busy state. `__nfp_nsp_command()` writes buffer and command registers, waits for command start to clear, waits for status busy to clear, extracts return option/result, and maps NSP errors to negative errno. Buffer commands use the default NSP buffer when large enough, otherwise DMA/SG descriptors when supported. Firmware load and flash write wrap buffer commands with command-specific options and timeouts.

State and persistence: The NSP resource lock serializes command access. Device registers and default buffers hold transient command state. Firmware load/flash/HWInfo/ETH control commands may change persistent device or flash configuration depending on command. `state->entries`, `idx`, and `modified` stage Ethernet table edits for `nfp_nsp_eth.c`.

Dependencies/integration: Depends on CPP scalar/bulk access, resource locking, DMA mapping, firmware blobs, and ABI feature tests in `nfp_nsp.h`. Used by Ethernet port discovery/configuration, hwmon, firmware management, and NIC probe flows.

Risks: DMA buffer alignment and SG capability handling are hardware/firmware-sensitive. Long flash writes have large timeout windows. Buffer zeroing and size caps protect firmware ABI but need tests. ABI minor checks gate optional features. This source snapshot has a few duplicated/truncated-looking lines, so compile validation is essential.

Test signals: NSP open on supported/unsupported ABI, NOOP wait, default-buffer and DMA-buffer commands, firmware load result messages, flash write timeout behavior, HWInfo null termination, version-string bounds, EEPROM partial-read errors, and concurrent NSP resource serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.h

Purpose: Declares the NSP command API, ABI feature predicates, Ethernet port/config structures, firmware policy constants, identify/sensor interfaces, media buffers, and version parsing helpers.

Important APIs/types/functions: `nfp_nsp_*()` covers lifecycle and commands. Inline `nfp_nsp_has_*()` predicates encode ABI minor thresholds. `enum nfp_eth_interface/media/aneg/fec`, FEC bit masks, `struct nfp_eth_table` and nested port structure define the Ethernet table contract. Config helpers include `nfp_eth_config_start()`, commit/cleanup, and `__nfp_eth_set_*()`.

Control flow/state: Header documents staged Ethernet configuration: callers open config state, mutate entries through helper setters, then commit or cleanup. NSP handles also carry ABI version used by feature predicates.

Dependencies/integration: Used by `nfp_nsp.c`, `nfp_nsp_eth.c`, `nfp_nsp_cmds.c`, NIC probe, ethtool, hwmon, and firmware management code.

Risks: ABI thresholds must match management firmware behavior. Ethernet table fields mix raw firmware state and computed driver state; callers must not assume all fields are valid on older ABI versions.

Test signals: Compile all NSP consumers, run ABI-minor feature matrix tests, verify port table parsing, config commit/cleanup behavior, and version/media/sensor query paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_cmds.c

Purpose: Implements smaller NSP-derived commands for board identity and hardware monitor sensors.

Important APIs/types/functions: `struct nsp_identify` mirrors the firmware identify buffer. `__nfp_nsp_identify()` converts it into `struct nfp_nsp_identify`. `struct nfp_sensors` mirrors sensor readings. `nfp_hwmon_read_sensor()` opens NSP, reads selected sensors, and returns one value.

Control flow: Identify requires ABI minor >= 15, allocates raw and public structures, calls `nfp_nsp_read_identify()`, converts endian fields, and frees raw memory. Sensor reads open NSP, issue `nfp_nsp_read_sensors()` with `BIT(id)`, close NSP, then select the requested little-endian value.

State and persistence: No persistent kernel state. Values are snapshots from NSP firmware.

Dependencies/integration: Depends on `nfp_nsp.c` command functions and `nfp_nsp.h` public structs/enums. Used by version reporting and hwmon integration.

Risks: Sensor ID bounds are checked only after command completion, so invalid IDs can request an invalid bit before returning `-EINVAL`. Identify returns NULL on unsupported ABI or errors, so callers must distinguish unavailable from allocation/read failure only by context.

Test signals: ABI <15 identify returns NULL; valid identify converts strings and fields; each sensor ID returns expected value; invalid sensor ID returns `-EINVAL`; NSP open/read failures propagate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_eth.c

Purpose: Parses and mutates the NSP Ethernet table that describes physical ports, media, speed, FEC, pause, autonegotiation, and split configuration.

Important APIs/types/functions: `union eth_table_entry` mirrors raw NSP table entries. `nfp_eth_read_ports()` and `__nfp_eth_read_ports()` build `struct nfp_eth_table`. `nfp_eth_config_start()`, `_commit_end()`, and `_cleanup_end()` stage and finalize table edits. Setters include `nfp_eth_set_mod_enable()`, `nfp_eth_set_configured()`, `nfp_eth_set_idmode()`, `nfp_eth_set_fec()`, `nfp_eth_set_pauseparam()`, and internal `__nfp_eth_set_aneg/speed/split()`.

Control flow: Reading fetches a fixed-size table, counts entries with lane bits set, validates optional returned count, allocates a flexible table, translates raw fields according to ABI minor, computes port geometry/split state, port type, and optional media link modes. Configuration reads the table, validates the target entry, records mutations in raw state/control bits, marks the NSP state modified, then writes the whole table back only if changed.

State and persistence: Parsed tables are heap snapshots. Configuration writes can alter persistent firmware/HWInfo overrides for FEC, speed, split, and autoneg as described by comments. NSP config state owns the temporary raw entries until commit/cleanup.

Dependencies/integration: Depends on NSP buffer commands, ethtool constants, NFP FEC/link-mode definitions, and CPP logging. NIC and ethtool paths consume the parsed port table and setters.

Risks: ABI-minor gates are critical; older firmware lacks reliable configured/idmode/pause/media fields. Raw bitfield mutation must preserve unrelated fields. Port index bounds are assumed by callers. The snapshot contains duplicated-looking braces/lines around one ABI check, so build validation is important.

Test signals: Read tables with zero/nonzero returned counts, ABI minor 16/22/33/37 feature matrices, split-port geometry and duplicate subport warning, every setter no-change vs modified commit path, unsupported ABI errors, invalid speed mapping, and media read failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_resource.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_resource.c

Purpose: Provides named resource discovery and locking over the NFP firmware resource table in MU memory.

Important APIs/types/functions: `struct nfp_resource_entry` mirrors firmware table entries with mutex and region descriptors. `struct nfp_resource` stores name, CPP ID, address, size, and lock handle. Public APIs include `nfp_resource_acquire/release/wait`, accessors, and `nfp_resource_table_init()`.

Control flow: Acquire allocates a resource handle, allocates the main table mutex, repeatedly locks the table, scans entries for a CRC32(name) key, creates a per-resource mutex, trylocks it, then releases the table mutex. Release unlocks/frees the per-resource mutex. Table init reclaims stale local locks on the main table and each resource entry under the table lock.

State and persistence: Persistent resource entries and lock words live in device MU memory at `NFP_RESOURCE_TBL_BASE`. Kernel state is the acquired resource handle and mutex objects.

Dependencies/integration: Depends on CPP reads, CRC32, and `nfp_cpp_mutex`. Used by HWInfo, NFFW, NSP, and other firmware-owned resources.

Risks: Resource lookup uses only the CRC key and does not compare the stored name bytes after key match in this file. Lock contention uses polling/timeouts. Incorrect reclaim can break active local users if called outside start-of-day conditions.

Test signals: Acquire/release known resources, wait for delayed resource creation, timeout and interrupt paths, table init reclaim warnings, missing-resource `-ENOENT`, and contention between two clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_rtsym.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_rtsym.c

Purpose: Reads firmware runtime symbol tables and provides lookup, bounded read/write, scalar little-endian access, and direct mapping for object symbols.

Important APIs/types/functions: `struct nfp_rtsym_entry` mirrors raw firmware entries. `struct nfp_rtsym_table` owns CPP pointer, symbol count, string table, and flexible symbol array. Public APIs include `nfp_rtsym_table_read()`, `__nfp_rtsym_table_read()`, count/get/lookup, read/write variants, scalar helpers, and `nfp_rtsym_map()`.

Control flow: Table read opens MIP, gets symtab/strtab addresses and sizes, aligns sizes, reads both from MU EMEM0, null-terminates the string table, and converts each raw entry into `struct nfp_rtsym`. Access checks symbol type and bounds, maps absolute symbols specially for reads, translates object targets/domains to CPP IDs, adjusts EMU cache direct MU addressing, and then calls CPP read/write/map helpers.

State and persistence: Runtime symbol tables are heap snapshots; mapped symbols return acquired CPP areas managed by the caller. Persistent source data lives in loaded firmware memory.

Dependencies/integration: Depends on MIP/NFFW, CPP access, MU locality, and NFP6000 target constants. NIC code uses runtime symbol mapping for firmware ABI tables such as DCB config.

Risks: String offsets are modulo `strtab_size`, preventing OOB but potentially hiding malformed tables. Negative targets other than handled EMU cache/LMEM are rejected. Write helpers reject unsupported/non-object targets but scalar ABS writes are invalid. Caller must free the symbol table with `kfree()` externally where appropriate.

Test signals: Known firmware symbol lookup, ABS read/readq behavior, object bounds checks, 4/8-byte scalar read/write, map minimum-size failure, EMU cache direct-address adjustment, and bad MIP/table size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_rtsym.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_target.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_target.c

Purpose: Encodes hardware knowledge for CPP target/action push-pull widths and translates island CPP IDs/addresses into target CPP IDs/addresses using IMB address-mode tables.

Important APIs/types/functions: `nfp_target_pushpull()` returns encoded read/write widths for NBI, QDR, ILA, MU, PCIe, ARM, crypto, CT XPB, CLS, and target 0. `nfp_target_cpp()` translates island IDs through `nfp_cppat_addr_encode()`. Helpers implement basic target and MU address encoding for IMB modes 0-3.

Control flow: Width decoding switches on target and action/token combinations, returning 32-bit, 64-bit, read-only, write-only, or invalid encodings used by PCIe area setup. Address translation leaves island 0 unchanged; otherwise it reads the target's IMB mode/address width/island fields and rewrites address bits so target-level CPP access reaches the requested island.

State and persistence: Stateless pure translation logic. It consumes the IMB table snapshot stored in `struct nfp_cpp`.

Dependencies/integration: Used by `nfp_cpp_area_alloc_with_name()` before backend area init and by `nfp6000_pcie.c` to determine access width. Depends on NFP6000 target constants and MU locality helper semantics.

Risks: Incorrect address bit encoding routes transactions to wrong islands. QDR and MU special cases intentionally reject or only validate some encodings. Unsupported target/action pairs return `-EINVAL`, which can make higher-level accesses fail at area allocation.

Test signals: Unit-style tests for each target/action width, island 0 passthrough, IMB mode 0-3 translation, MU direct/locality cases, CT XPB constraints, and invalid target/action rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/dcb.c

Purpose: Implements DCBNL IEEE 802.1Qaz support for the NFP NIC app by mapping user DCB settings into a firmware runtime symbol table and notifying firmware through the netdev mailbox.

Important APIs/types/functions: `struct nfp_dcb` is defined in `main.h`; this file operates on it via `get_dcb_priv()`. DCBNL ops include ETS get/set, maxrate get/set, DSCP app set/delete. Helpers write PCP/DSCP-to-TC indexes, TSA, bandwidth percentage, max rates, enable/trust fields, and mailbox update masks. `nfp_nic_dcb_init()` maps `net.dcbcfg_tbl`; `nfp_nic_dcb_clean()` releases it.

Control flow: Init maps the firmware DCB config table runtime symbol for each vNIC and initializes default TC/prio/rate/TSA state before attaching `dcbnl_ops`. Set ETS validates bandwidth rules, updates cached arrays, refreshes strict-priority TC index mapping, writes firmware table fields, ensures rate/trust/enable state, then sends `NFP_NET_CFG_MBOX_CMD_DCB_UPDATE`. Maxrate and DSCP app paths similarly update the mapped table and notify firmware.

State and persistence: Driver keeps per-vNIC DCB arrays and flags in `app_priv`. Firmware-visible state is written into mapped CPP memory and committed through mailbox commands. DSCP app entries are also tracked by the kernel DCB app list.

Dependencies/integration: Depends on `CONFIG_DCB`, net/dcbnl, NFP app/net structures, runtime symbol mapping via `nfp_pf_map_rtsym()`, CPP area cleanup, and NFP net mailbox APIs.

Risks: Mapped table offsets are ABI-sensitive (`NFP_DCB_CFG_STRIDE`, field offsets, update masks). Trust mode changes depend on DSCP count. Maxrate conversion uses kbps-to-mbps and reserves `0xffff` for unlimited. Mailbox lock/reconfig failures must avoid diverging cached state from firmware.

Test signals: DCB init with present/missing `net.dcbcfg_tbl`, ETS validation failure for bad bandwidth sums, maxrate boundary `>=0xffff` Mbps, DSCP set/delete and trust fallback, mailbox failure propagation, and cleanup releasing the mapped CPP area.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.c

Purpose: Defines the NFP core NIC app type and wires generic app lifecycle hooks to NIC-specific vNIC allocation, DCB initialization, and cleanup.

Important APIs/types/functions: `nfp_nic_init()` validates Ethernet table count against max data vNICs. `nfp_nic_vnic_alloc()` calls common NIC allocation then allocates `struct nfp_app_nic_private`. `nfp_nic_vnic_init/clean()` call DCB init/clean. `app_nic` registers callbacks for app selection.

Control flow: App init runs after PF data is available and rejects ETH/vNIC count mismatch. Each vNIC allocation runs common allocation first, then allocates per-vNIC private data. vNIC init attaches optional DCB support; clean releases it; free releases private memory. SR-IOV enable/disable hooks are stubs returning success/no-op.

State and persistence: Per-vNIC `nn->app_priv` owns NIC private state, including DCB state under `CONFIG_DCB`. No persistent storage.

Dependencies/integration: Depends on NFP app framework, PF ETH table discovery, `nfp_app_nic_vnic_alloc()`, and `main.h` DCB helpers.

Risks: If private allocation fails after common vNIC allocation, this function returns `-ENOMEM` without local rollback of the common allocation in this file. ETH table count validation only runs when `pf->eth_tbl` exists. SR-IOV hooks are placeholders.

Test signals: App selection/probe, ETH table count mismatch, vNIC allocation failure injection, DCB init/clean calls with and without `CONFIG_DCB`, and unload freeing `app_priv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.h

Purpose: Declares NIC app private data and, when DCB is enabled, the per-vNIC DCB state layout and init/clean hooks.

Important APIs/types/functions: Defines DCB sizes (`NFP_NET_MAX_DSCP`, `NFP_NET_MAX_TC`, `NFP_NET_MAX_PRIO`, `NFP_DCB_CFG_STRIDE`), `struct nfp_dcb`, `nfp_nic_dcb_init()`, `nfp_nic_dcb_clean()`, and `struct nfp_app_nic_private`.

Control flow/state: Header-only declarations. With `CONFIG_DCB`, each NIC private object embeds `struct nfp_dcb`; otherwise DCB init/clean are inline no-ops and the private structure is empty.

Dependencies/integration: Included by NIC main and DCB implementation. Depends on Linux netdevice/DCB constants and NFP CPP area forward declarations through included implementation context.

Risks: Empty `struct nfp_app_nic_private` under no DCB interacts with allocation logic that checks `sizeof(*app_pri)`. DCB field layout must match `dcb.c` expectations.

Test signals: Build with `CONFIG_DCB=y` and disabled, verify vNIC private allocation behavior, DCB init/clean symbol availability, and no-op behavior when DCB is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Kconfig

Purpose: Adds the National Instruments Ethernet vendor menu and the NI XGE management Ethernet driver configuration option.

Important APIs/types/functions: `config NET_VENDOR_NI` controls visibility of NI Ethernet drivers and defaults to `y`. `config NI_XGE_MANAGEMENT_ENET` is a tristate depending on `HAS_IOMEM && HAS_DMA`, selecting `PHYLIB` and `OF_MDIO` when OF is enabled.

Control flow/state: Kconfig-only build selection. It does not create runtime state; it controls whether `nixge.o` can be built.

Dependencies/integration: Integrated under the kernel Ethernet vendor tree. The selected driver depends on MMIO, DMA, PHY library, and optionally Open Firmware MDIO.

Risks: Missing dependency selections would surface as link/runtime failures in `nixge.c`. Defaulting vendor menu to yes exposes the prompt but does not force the driver.

Test signals: Run Kconfig/menuconfig coverage for `NET_VENDOR_NI=y/n`, module and built-in builds for `NI_XGE_MANAGEMENT_ENET`, and OF/non-OF dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Makefile

Purpose: Connects the NI XGE management Ethernet Kconfig symbol to its object file.

Important APIs/types/functions: `obj-$(CONFIG_NI_XGE_MANAGEMENT_ENET) += nixge.o`.

Control flow/state: Build-system rule only. Runtime behavior comes from `nixge.c` when the symbol is enabled.

Dependencies/integration: Consumed by Kbuild under `drivers/net/ethernet/ni`; paired with `Kconfig`.

Risks: Symbol/file name drift would silently omit or fail the driver build. There are no multi-object rules here.

Test signals: Build with `CONFIG_NI_XGE_MANAGEMENT_ENET=m` and `=y`, verify `nixge.o` is compiled/linked in the expected target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ni/Makefile -->

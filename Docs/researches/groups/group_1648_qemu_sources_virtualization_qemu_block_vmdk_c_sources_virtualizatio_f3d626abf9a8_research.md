# Group Research: group_1648_qemu_sources_virtualization_qemu_block_vmdk_c_sources_virtualizatio_f3d626abf9a8

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/qemu`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vmdk.c -->
# File Research: sources/virtualization/qemu/block/vmdk.c

QEMU block format driver for VMware VMDK images. It supports descriptor-based VMDKs, monolithic sparse, flat and split extents, VMFS sparse, streamOptimized compressed images, zeroed-grain sparse images, and read-only seSparse extents.

Key responsibilities:
- Detect VMDK images via VMDK3/VMDK4 magic or descriptor `version=` lines.
- Parse descriptor files, `createType`, extent lines, parent hints, CID and parent CID fields.
- Open and manage multiple ordered `VmdkExtent` objects, each with its own child file, L1/L2 tables, cluster geometry, compression flags, and flat/sparse/seSparse mode.
- Validate backing image CID before reading or copying from the parent.
- Implement cluster lookup and allocation through L1/L2 grain tables, including L2 cache management and zeroed-grain handling.
- Implement COW allocation through `get_whole_cluster()`, preserving backing data outside the written byte range.
- Support zlib-compressed streamOptimized grain reads/writes with `VmdkGrainMarker`.
- Create VMDK images and extents for monolithic/split, flat/sparse, streamOptimized, backing-file, compat6, hwversion, toolsVersion, and zeroed-grain options.
- Report block status, allocated file size, zero initialization, driver-specific image info, and block driver info.
- Register the `vmdk` format `BlockDriver`.

Important structures:
- `VMDK3Header`, `VMDK4Header`: on-disk sparse headers.
- `VMDKSESparseConstHeader`, `VMDKSESparseVolatileHeader`: seSparse header validation structures.
- `VmdkExtent`: per-extent state, child file, table offsets, cache, geometry, flags.
- `BDRVVmdkState`: whole-image state, extent array, CID state, migration blocker, create type.
- `VmdkMetaData`: L1/L2 indices used when updating an allocation.
- `VmdkGrainMarker`: compressed stream grain header.

Core flow:
- `vmdk_open()` opens the primary child, reads either sparse header or text descriptor, parses extents, opens parent hints, reads CIDs, initializes locking, and installs a migration blocker.
- Sparse opens go through `vmdk_open_vmfs_sparse()`, `vmdk_open_vmdk4()`, or `vmdk_open_se_sparse()`.
- I/O uses `find_extent()` plus `get_cluster_offset()` to map guest offsets to extent offsets. Reads fall back to backing or zeroes. Writes allocate clusters, perform COW, write data, update L2 tables, and update CID on first write.
- Creation is centralized in `vmdk_co_do_create()` with callback-based extent provisioning for legacy option creation and QAPI blockdev creation.

Notable constraints and risks:
- seSparse is opened read-only; dirty journal replay is explicitly unsupported.
- VMDK disables live migration through a migration blocker.
- StreamOptimized writes only allow whole-cluster compressed writes and reject rewrites to allocated compressed clusters.
- Descriptor parsing uses fixed-size buffers and explicit validation for extent syntax, paths, and supported types.
- L1 size, cluster size, sector limits, footer validity, VMDK version, and table sizes are guarded to reject corrupt images.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vmdk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vpc.c -->
# File Research: sources/virtualization/qemu/block/vpc.c

QEMU block format driver for Connectix/Microsoft Virtual PC VHD images. It handles fixed and dynamic VHDs, including footer/header validation, dynamic BAT mapping, block allocation, and create paths.

Key responsibilities:
- Probe VHD images using the `conectix` footer/header signature.
- Parse VHD footers and dynamic disk headers, with big-endian field conversion and checksum validation.
- Determine visible disk size using Virtual PC CHS rules or footer `current_size`, with creator-app heuristics and runtime override via `force_size_calc`.
- Open fixed VHDs where data is directly addressed and dynamic VHDs with a Block Allocation Table.
- For dynamic images, maintain `pagetable`, `bat_offset`, `block_size`, `bitmap_size`, and `free_data_block_offset`.
- Map guest offsets to image offsets through `get_image_offset()`, including block bitmap updates for writes.
- Allocate new dynamic VHD blocks by writing bitmap, moving footer, and updating BAT.
- Create dynamic and fixed VHD images with valid footer, UUID, CHS geometry, dynamic header, and initial BAT.
- Register the `vpc` format `BlockDriver`.

Important structures:
- `VHDFooter`: 512-byte VHD hard disk footer, checked at compile time.
- `VHDDynDiskHeader`: 1024-byte dynamic disk header.
- `BDRVVPCState`: driver state for footer, BAT, block allocation metadata, runtime sizing overrides, and migration blocker.

Core flow:
- `vpc_open()` opens the file child, absorbs runtime options, reads the footer from the start or end depending on disk type, validates checksum, computes `bs->total_sectors`, and initializes dynamic BAT state when needed.
- `vpc_co_preadv()` returns direct reads for fixed disks. Dynamic reads return zeroes for unallocated blocks or read mapped image blocks.
- `vpc_co_pwritev()` writes directly for fixed disks. Dynamic writes allocate missing blocks and update block bitmaps/BAT/footer before writing data.
- `vpc_co_block_status()` reports fixed images as recursively mapped data and dynamic images as allocated data or zero regions.
- `vpc_co_create()` and `vpc_co_create_opts()` convert QAPI/legacy options, round sizes, calculate CHS-compatible geometry, and create fixed or dynamic images.

Notable constraints and risks:
- Maximum image size is capped at VHD’s 2040 GiB limit.
- Live migration is blocked for VPC/VHD images.
- The dynamic block bitmap is written as all-used for any block written, prioritizing correctness over sparse-read optimization.
- Geometry compatibility matters: without `force-size`, create rejects sizes not representable by the VHD CHS algorithm.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/vvfat.c -->
# File Research: sources/virtualization/qemu/block/vvfat.c

QEMU `vvfat` block/protocol driver that exposes a host directory as a synthetic FAT disk image. It can run read-only directly over host files or writable through a temporary qcow overlay that is reconciled back to the host directory after consistency checks.

Key responsibilities:
- Parse `fat:` filenames and runtime options: `dir`, `fat-type`, `floppy`, `label`, and `rw`.
- Build an in-memory MBR, boot sector, FAT, root directory, directory entries, and cluster-to-host-file mappings from a host directory tree.
- Generate FAT short names and long filename entries, including UTF-8/UTF-16 conversion, 8.3 lossy conversion, numeric tails, checksums, timestamps, and volume labels.
- Serve sector reads from synthetic first sectors, FAT copies, directory arrays, host file clusters, or the qcow write overlay.
- In writable mode, create a temporary qcow write target backed by the virtual `fat:` image, stage guest writes there, and try to commit changes back to host files/directories.
- Validate modified FAT and directory state before commit, including used-cluster tracking, long/short filename parsing, directory recursion, file size versus FAT chain length, duplicate cluster detection, and filename validity.
- Reconcile guest changes by scheduling and applying renames, mkdirs, new files, writeouts, and deletes.
- Register the `vvfat` format/protocol driver and private qcow child permissions.

Important structures:
- `bootsector_t`, `mbr_t`, `partition_t`, `direntry_t`: packed FAT/MBR on-disk structures synthesized in memory.
- `array_t`: small growable array used for FAT, directory, mapping, and commit lists.
- `mapping_t`: maps a FAT cluster range to a host file or directory segment.
- `BDRVVVFATState`: full driver state, geometry, FAT/directory/mapping arrays, current open host file, qcow overlay, commit list, used cluster map, and migration blocker.
- `commit_t`: queued host-side operation for rename, writeout, new file, or mkdir.
- `long_file_name`: parser state for VFAT long filename chains.

Core flow:
- `vvfat_open()` parses options, chooses floppy/disk geometry and FAT type, enables write target if requested, calls `init_directories()`, optionally initializes MBR, and installs a migration blocker for rw mode.
- `init_directories()` scans the host tree, builds directory entries and mappings, allocates FAT chains, fills boot sector fields, and establishes root mapping.
- `vvfat_read()` resolves sectors to first sectors, FAT copies, directory clusters, host file data, or qcow overlay data.
- `vvfat_write()` rejects protected boot-sector/FAT misuse, enforces read-only host-file constraints, writes sectors to qcow, marks modified clusters, and invokes `try_commit()`.
- `is_consistent()` copies the modified FAT from the overlay, marks existing mappings deleted, recursively checks the root directory, and verifies used cluster counts.
- `do_commit()` applies scheduled filesystem mutations, copies the modified FAT into the live FAT, commits directory entries and file contents, deletes removed mappings, empties qcow, and clears used-cluster state.

Notable constraints and risks:
- FAT32 is warned as untested and several comments note FAT32-specific inaccuracies.
- Writable mode is conservative and fragile: many inconsistency paths abort or refuse to commit.
- Writes are sector-aligned only; request alignment is forced to 512 bytes.
- Host files larger than 2 GiB are rejected while building mappings.
- Live migration is blocked only when writable qcow mode is enabled.
- The driver deliberately protects boot sectors, read-only files, and read-only directory entries from guest writes.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/vvfat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/win32-aio.c -->
# File Research: sources/virtualization/qemu/block/win32-aio.c

Windows asynchronous I/O backend for QEMU raw/block file operations. It wraps Windows overlapped I/O and IO completion ports into QEMU’s AIO callback model.

Key responsibilities:
- Maintain `QEMUWin32AIOState` with IOCP handle, event notifier, in-flight count, and attached `AioContext`.
- Represent each request with `QEMUWin32AIOCB`, including overlapped state, request context, QEMUIOVector, temporary linear buffer, operation type, and result.
- Submit reads/writes through `ReadFile()`/`WriteFile()` with `OVERLAPPED`.
- Use a temporary block-aligned buffer for multi-iovec requests, copying into/out of the QEMU iovec as needed.
- Process IOCP completions from `win32_aio_completion_cb()`, complete callbacks in the original request `AioContext`, and free AIOCBs.
- Attach file handles to an IOCP and attach/detach event notifier handling from QEMU AIO contexts.
- Initialize and clean up the backend state.

Important functions:
- `win32_aio_submit()`: creates AIOCB, prepares buffer and overlapped offset, starts Windows async read/write, and returns `BlockAIOCB`.
- `win32_aio_process_completion()`: translates Windows completion to QEMU status, zero-pads short reads, rejects short writes, copies read data back for non-linear buffers, and schedules callback.
- `win32_aio_attach()`: binds a Windows handle to the IOCP.
- `win32_aio_init()` / `win32_aio_cleanup()`: lifecycle management.

Notable constraints and risks:
- Short reads are treated as EOF and zero-filled; short writes are errors.
- Completion callback execution is redirected when the completing backend context differs from the original request context.
- The file is Windows-specific and depends on `<windows.h>`, `<winioctl.h>`, event notifiers, and QEMU AIO internals.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/win32-aio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/write-threshold.c -->
# File Research: sources/virtualization/qemu/block/write-threshold.c

Small block-core helper for write-threshold notifications. It stores a threshold in `BlockDriverState` and emits a QAPI event when a write crosses it.

Key responsibilities:
- Get and set `bs->write_threshold_offset`.
- Implement QMP command `block-set-write-threshold` by looking up a node name and storing the threshold.
- Check writes via `bdrv_write_threshold_check_write()` and send `BLOCK_WRITE_THRESHOLD` with excess bytes and threshold value.
- Auto-disable the threshold after the first event to avoid monitor flooding.

Important functions:
- `bdrv_write_threshold_get()`
- `bdrv_write_threshold_set()`
- `qmp_block_set_write_threshold()`
- `bdrv_write_threshold_check_write()`

Notable constraints:
- Threshold comparison uses write end offset, `offset + bytes`.
- A zero threshold disables notifications.
- Missing nodes are reported through `Error **errp`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/write-threshold.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/Kconfig -->
# File Research: sources/virtualization/qemu/hw/virtio/Kconfig

Kconfig declarations for QEMU virtio and vhost-user/vhost-vdpa device families.

Key contents:
- Base `VIRTIO` symbol selected by virtio transports.
- Transport symbols: `VIRTIO_PCI`, `VIRTIO_MMIO`, `VIRTIO_CCW`.
- Core virtio devices: RNG, NSM, IOMMU, balloon, crypto.
- Memory-device support gates: `VIRTIO_MD_SUPPORTED`, `VIRTIO_MD`, `VIRTIO_PMEM_SUPPORTED`, `VIRTIO_PMEM`, `VIRTIO_MEM_SUPPORTED`, `VIRTIO_MEM`.
- vhost/vhost-user devices: vsock, i2c, rng, fs, gpio, vdpa dev, sound, SCMI, SPI, test, RTC.

Dependency model:
- Transports select `VIRTIO`; PCI and CCW also select `VIRTIO_MD_SUPPORTED`.
- Virtio memory devices require a supported transport/board path and select `MEM_DEVICE` through `VIRTIO_MD`.
- `VIRTIO_NSM` requires `LIBCBOR && VIRTIO`.
- `VIRTIO_IOMMU` requires `PCI && VIRTIO`.
- vhost-user devices generally require `VIRTIO && VHOST_USER`; vhost-vdpa requires `VIRTIO && VHOST_VDPA && LINUX`.

Notable role:
- This file is build-configuration glue rather than runtime code. It controls which virtio device implementations are available for a target based on platform, transport, and dependency symbols.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/cbor-helpers.c -->
# File Research: sources/virtualization/qemu/hw/virtio/cbor-helpers.c

Helper layer around libcbor for QEMU virtio code, used to construct CBOR maps and arrays with consistent ownership cleanup. It is gated by virtio Kconfig users such as `VIRTIO_NSM`.

Key responsibilities:
- Add key/value pairs to CBOR maps using `cbor_move()` while restoring references on failure.
- Push values to CBOR arrays with equivalent ownership handling.
- Provide typed convenience helpers for adding booleans, uint8 values, uint64 values, strings, nulls, byte strings, nested maps, uint8 arrays, and uint8-keyed byte strings to maps.
- Clean up partially constructed CBOR items on allocation or insertion failure.

Important functions:
- `qemu_cbor_map_add()`: moves key/value into a `struct cbor_pair` and calls `cbor_map_add()`.
- `qemu_cbor_array_push()`: moves an item into an array.
- `qemu_cbor_add_bool_to_map()`, `qemu_cbor_add_uint8_to_map()`, `qemu_cbor_add_uint64_to_map()`: scalar helpers.
- `qemu_cbor_add_map_to_map()`: creates a definite nested map and returns it to the caller through `nested_map`.
- `qemu_cbor_add_bytestring_to_map()` and `qemu_cbor_add_uint8_key_bytestring_to_map()`: byte-string helpers.
- `qemu_cbor_add_string_to_map()` and `qemu_cbor_add_null_to_map()`: string/null helpers.
- `qemu_cbor_add_uint8_array_to_map()`: builds a definite array and pushes per-byte CBOR uint8 items.

Notable constraints:
- All helpers return `bool` success/failure and avoid propagating `Error **`.
- On successful map/array insertion, ownership is transferred to the CBOR container.
- On failure, locally held CBOR items are decref’d to avoid leaks.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/cbor-helpers.c -->
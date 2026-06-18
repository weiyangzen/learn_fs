# Group Research: group_301_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_subr_bus_c_sources_d92608754055

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_bus.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_bus.c

DragonFly BSD kernel bus/device framework core. It manages devclasses, devices, driver module registration, generic bus methods, resource hints, root bus bootstrapping, and user-visible device-tree reporting.

Key responsibilities:
- Creates `hw.bus` and `dev.*` sysctl surfaces for bus generation, device metadata, devclass parents, device descriptions, drivers, PNP info, locations, and parents.
- Implements `/dev/devctl` as a single-reader event queue with blocking/nonblocking reads, kqueue read readiness, optional `SIGIO`, and formatted add/remove/no-match notifications.
- Maintains global devclass and device lists, unit allocation, device naming, parent/child links, device state transitions, softc allocation, descriptions, sysctl lifecycle, and bus data generation changes.
- Probes drivers by devclass and parent devclass inheritance, supports global driver priority filtering, handles attach/detach/shutdown/suspend/resume, and optionally launches asynchronous attach threads.
- Implements root bus creation/configuration and dynamic driver module load/unload handling.
- Provides runtime/config-time resource hint lookup and mutation plus `resource_list_*` helpers.
- Provides generic bus method implementations that propagate interrupts, resources, ivars, DMA tags, and child operations up the bus hierarchy.

Important behavior:
- `root_bus_configure()` identifies/probes root children and waits for async attaches before marking the root bus attached.
- Driver load calls `BUS_DRIVER_ADDED()` on already attached busses so newly loaded modules can bind existing devices.
- Failed probes emit no-match notifications once per device through `DF_DONENOMATCH`.
- Device detach refuses busy devices, tears down sysctls, clears non-fixed devclasses, and resets the driver/kobj binding.
- `hw.bus.devices` is generation-checked; userland must retry if the bus generation changes.

Dependencies:
- Depends on DragonFly `kobj`, module, sysctl, devfs/dev_ops, rman/resource, bus method macros, lwkt threads, locks, caps, signal, and interrupt APIs.
- Interacts with config-generated `config_devtab` and kernel environment hints in both DragonFly and FreeBSD naming forms.

Notable risks:
- Much of the device/devclass global state is manipulated without a single visible global lock in this file; callers rely on bus configuration ordering and subsystem conventions.
- `/dev/devctl` intentionally supports only one reader and can drop events on allocation failure.
- `devaddq()` has suspicious cleanup logic: if `loc` allocation fails after `data` allocation, the `bad:` path does not free `data` because it checks `loc` before freeing `data`.
- Resource hint generic matching has an in-code XXX noting that the generic pass still compares `devtab[i].unit == unit`, which makes generic unit entries questionable.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_bus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_busdma.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_busdma.c

Small bus-DMA convenience layer for coherent memory allocation and mbuf DMA loading with defragmentation fallback.

Key responsibilities:
- `bus_dmamem_coherent()` creates a DMA tag, allocates coherent memory, loads the DMA map, and returns virtual address, tag, map, and bus address through `bus_dmamem_t`.
- `_bus_dmamem_coherent_cb()` records the single DMA segment bus address and asserts that exactly one segment is returned.
- `bus_dmamem_coherent_any()` wraps coherent allocation for unrestricted address ranges and returns the virtual address plus raw tag/map/busaddr outputs.
- `bus_dmamap_load_mbuf_defrag()` retries mbuf segment loading after `m_defrag()` when the first load fails with `EFBIG`.

Important behavior:
- Coherent allocation constrains the tag to one segment of `maxsize`.
- If `bus_dmamap_load()` reports `EINPROGRESS` for coherent memory, the helper panics instead of supporting asynchronous completion.
- On allocation or map-load failure, the helper unwinds the tag/map/allocation and clears the caller's `bus_dmamem_t`.

Dependencies:
- Depends on bus_dma tag/map APIs, mbufs, `m_defrag()`, and `BUS_DMA_COHERENT`.

Notable risks:
- Callers receiving pointers from `bus_dmamem_coherent_any()` must retain and free the returned tag/map using the expected bus-DMA APIs.
- The mbuf defrag helper uses `M_NOWAIT`, so high pressure can surface as `ENOBUFS`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_busdma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_cpu_topology.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_cpu_topology.c

CPU topology discovery, tree construction, sibling mask query, and sysctl export for DragonFly BSD.

Key responsibilities:
- Builds a uniform topology tree from architecture-provided APIC/chip/core/thread ID helpers.
- Stores topology nodes in a static `MAXCPU` node array and exports `cpu_root_node`/`root_cpu_node`.
- Computes threads per core, cores per chip, physical package count, per-CPU physical/core/HT IDs, and sibling masks.
- Handles x86_64 AMD compute-unit reshaping when `fix_amd_topology()` reports applicable topology.
- Provides query helpers such as `get_cpu_node_by_cpuid()`, `get_cpumask_from_level()`, `get_cpu_node_by_chipid()`, `get_cpu_ht_id()`, `get_cpu_core_id()`, `get_cpu_phys_id()`, and `get_highest_node_memory()`.
- Builds `hw.cpu_topology` sysctls, including a printable topology tree, level descriptions, root members, and per-CPU physical/core sibling data.

Important behavior:
- Initialization runs at `SI_BOOT2_CPU_TOPOLOGY` using `naps + 1` as the assumed CPU count.
- Topology shape is inferred from BSP sibling relationships, then APIC IDs are walked in order to populate leaf CPU masks.
- Physical IDs are normalized into a compact range before being exposed for VM/scheduler use.

Dependencies:
- Depends on machine SMP helpers: `detect_cpu_topology()`, APIC ID lookup, chip/core/logical CPU ID accessors, and AMD topology fixups.
- Uses DragonFly cpumask macros and `sbuf` for sysctl string generation.

Notable risks:
- The builder assumes a mostly uniform topology; unusual heterogeneous CPU layouts may be represented poorly.
- `get_next_valid_apicid()` can return `-1` when no valid APIC ID is found, so correctness depends on architecture data and `assumed_ncpus` being consistent.
- Several output buffers are fixed-size strings sized from `MAXCPU`; very large CPU counts depend on those sizing assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_cpu_topology.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_cpuhelper.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_cpuhelper.c

Per-CPU helper thread framework for executing callbacks on a selected CPU through lwkt message ports.

Key responsibilities:
- Creates one fixed-CPU helper thread per CPU during `SI_SUB_PRE_DRIVERS`.
- Exposes `cpuhelper_initmsg()`, `cpuhelper_replymsg()`, and `cpuhelper_domsg()` for callback-message setup, reply, and synchronous dispatch.
- Replaces each helper port's `mp_putport` with `cpuhelper_putport()` to detect synchronous self-messages and execute them directly.
- Provides `cpuhelper_assert()` invariant checks for code that must run inside or outside a specific helper context.

Important behavior:
- A synchronous message sent to the current helper port is converted into a direct callback invocation and returns `EASYNC`, preventing self-deadlock.
- Helper threads loop forever on their message port and require every message to contain a non-NULL callback.

Dependencies:
- Depends on DragonFly lwkt threads, ports, messages, fixed-CPU thread creation, and `sys/cpuhelper.h`.

Notable risks:
- Self-referential callbacks execute in the caller's current stack/context, not through the normal queued helper loop.
- Initialization assumes all helper ports start with the same original `mp_putport` function.
- There is no teardown path; the helper array is lifetime-kernel state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_cpuhelper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_csprng.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_csprng.c

Fortuna-like CSPRNG state machine built from SHA-256 entropy pools and embedded ChaCha20 keystream generation.

Key responsibilities:
- Initializes 32 SHA-256 entropy pools, the ChaCha key/context, source-to-pool round-robin indexes, reseed counters, and timestamps.
- Adds entropy by hashing source ID, byte count, and entropy bytes into a rotating pool selected per 8-bit source ID.
- Reseeds from pool 0 only after a minimum pool byte threshold, and folds higher-numbered pools in on reseed counts divisible by powers of two.
- Updates the ChaCha key from SHA-256(old key || selected pool digests), resets the 128-bit counter, and generates output in bounded chunks.
- Rekeys after each output chunk by encrypting new key material from the existing stream.

Important behavior:
- Callers are expected to hold `state->spin` for both entropy addition and random generation.
- Non-`CSPRNG_UNLIMITED` consumers sleep until at least one reseed has succeeded.
- Output is limited to `2^20` bytes between rekeys.
- Callout-based reseeding code is present but disabled with `#if 0`.

Dependencies:
- Embeds `crypto/chacha20/chacha.c` with keystream-only settings and uses SHA-256 from `crypto/sha2`.
- Uses DragonFly spin locks, `ratecheck()`, `ssleep()`, and `wakeup()` conventions.

Notable risks:
- `CSPRNG_UNLIMITED` callers can receive output even before the first successful reseed, relying on that mode's weaker semantics.
- Entropy accounting is byte-count based; it does not estimate entropy quality.
- Pool byte counters grow monotonically after pool reinitialization with a digest seed, so they are not a strict measure of fresh entropy.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_csprng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_devstat.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_devstat.c

Kernel device I/O statistics registry and transaction accounting implementation.

Key responsibilities:
- Maintains a priority-sorted global `devstat` singly-linked tail queue.
- Adds/removes `devstat` entries, assigning stable device numbers, creation time, block size, support flags, type flags, and priority.
- Tracks transaction start and completion, including busy periods, read/write/free/other operation counts, byte counters, completion time, and ordered tag counters.
- Provides `devstat_end_transaction_buf()` to classify completed `struct buf` commands.
- Exports all device statistics, generation, number of devices, and devstat ABI version through `kern.devstat.*` sysctls.

Important behavior:
- `busy_count` is atomically incremented/decremented; busy time is accumulated only when the device transitions back to idle.
- The `kern.devstat.all` sysctl emits the generation number followed by the current array of `struct devstat` entries to keep the snapshot self-consistent for userland.

Dependencies:
- Depends on DragonFly buffer command values, sysctl, timekeeping, and `sys/devicestat.h`.

Notable risks:
- The global devstat queue and generation counters have no explicit lock in this file; callers rely on higher-level registration discipline.
- Per-device byte and operation counters are plain fields, so concurrent updates may be approximate rather than strictly serialized.
- If `devstat_end_transaction()` is called more times than start, it logs a negative `busy_count` warning but does not otherwise repair accounting.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_devstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_disk.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_disk.c

DragonFly BSD managed disk layer. It wraps raw disk driver devices with cooked disk/slice/partition devices, probes partition metadata, routes I/O through slices, and coordinates disk lifecycle through a serialized message thread.

Key responsibilities:
- Creates raw and managed disk `cdev_t` devices, devfs aliases, udev metadata, dsched integration, and iocom state.
- Updates disk media info and triggers asynchronous or synchronous probing through `disk_msg_core`.
- Probes MBR/GPT slices, creates slice devices, probes BSD disklabel32/64 partitions, creates partition devices, and maintains `serno`, label, UUID, slice, and partition aliases.
- Serializes probe, reprobe, unprobe, and destroy operations through lwkt disk messages and `ds_token`.
- Implements disk open/close, ioctl routing, strategy I/O, psize, crash dump configuration, disk enumeration, and disk locate helpers.
- Provides `bioqdisksort()` read-before-write ordering with write trickle/burst controls and media-size bounds checking.

Important behavior:
- `disk_setdiskinfo()` copies media geometry/serial data, derives missing media size/block count, updates scheduler state, then probes the disk.
- `disk_probe()` replaces the slice table, calls `mbrinit()`, creates slice devices, and probes BSD labels only for compatibility/BSD-like slices.
- `diskstrategy()` uses `dscheck()` to translate slice-relative offsets to raw-device offsets before dispatching to the raw strategy routine.
- Opens are serialized with `DISKFLAG_LOCK`; the raw device is opened on the first slice/partition open and closed after the last close.
- Reprobe preserves existing devfs nodes by marking valid devices with `SI_REPROBE_TEST` and destroying stale related nodes afterward.

Dependencies:
- Depends on disk slice and disklabel ops, MBR/GPT probing, devfs, raw driver `dev_ops`, buffer/BIO APIs, lwkt ports/tokens, kernel dump, dsched, udev, and UUID helpers.

Notable risks:
- Disk probing is asynchronous by default, so consumers must tolerate device-node appearance after `disk_setdiskinfo()`.
- Correctness depends on `dscheck()`, disklabel ops, and devfs reprobe flags staying in sync across slice/partition changes.
- Raw/cooked device layering has special cases for device-mapper and `D_NOEMERGPGR`.
- `bounds_check_with_mediasize()` mixes `DEV_BSIZE` offset conversion with caller-provided sector size/media units, matching legacy assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskgpt.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskgpt.c

GPT partition-table reader used when the MBR parser detects a protective GPT MBR entry.

Key responsibilities:
- Reads the primary GPT header at LBA 1 and validates header size and header CRC.
- Validates partition entry count, entry size, entry table location, and table size against media bounds.
- Reads the GPT entry table and replaces the caller's minimal slice structure with one sized for up to 128 GPT entries plus special slices.
- Converts little-endian GPT UUIDs, LBAs, attributes, and UTF-16 name fields into host-order temporary entries.
- Maps non-empty GPT entries into DragonFly disk slices, including storage/type UUIDs and offsets/sizes.
- Maps known DragonFly and FreeBSD GPT type UUIDs to legacy DOS partition type values for downstream BSD-label probing.

Important behavior:
- GPT parsing is not recursive; once GPT is detected the rest of the MBR is ignored.
- GPT entry 0 is exposed through `COMPATIBILITY_SLICE` (`s0`), and later GPT entries are mapped starting at `BASE_SLICE`.
- Entries overlapping the GPT table, beyond media bounds, or with inverted LBA ranges are rejected with diagnostics.

Dependencies:
- Depends on `sys/gpt.h`, UUID helpers, disk slice structures, buffer/BIO synchronous reads, and `crc32()`.

Notable risks:
- Only the primary GPT path is handled here; backup GPT recovery is not implemented in this routine.
- The GPT entry-array CRC from the header is not checked, so validation is weaker than full GPT verification.
- The implementation caps GPT entries at 128 and expects the whole entry table read to fit in one pbuf-sized request.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskgpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskiocom.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskiocom.c

Disk DMSG/kdmsg bridge exposing a local raw disk as a remote block peer and executing remote block operations against the raw device.

Key responsibilities:
- Initializes and tears down per-disk `kdmsg_iocom` state with autoconnect, autorxspan, and autotxspan enabled.
- Handles `DIOCRECLUSTER` by reconnecting the disk iocom over a provided file descriptor.
- Publishes block media size, block size, peer labels, and PFS labels derived from hostname, device name, and serial number.
- Dispatches received DMSG transactions for block open, read, write, flush, and free-block commands.
- Converts remote block commands into kernel pbuf/BIO operations against `dp->d_rawdev`.
- Replies asynchronously from `diskiodone()` with DMSG error codes and read data in auxiliary payloads.

Important behavior:
- Non-transaction root-state messages are rejected except for limited debug message handling.
- `DMSG_BLK_OPEN` tracks per-transaction read/write open counts and closes raw-device references when the transaction is deleted.
- Writes with short auxiliary data zero-fill the remainder of the requested block range.
- Reads copy pbuf data into a newly allocated DMSG auxiliary reply buffer.
- `blk_active` tracks active iocom BIOs and is exposed under `debug.blk_active`.

Dependencies:
- Depends on DragonFly DMSG/kdmsg, raw dev_ops, pbuf/BIO, proc0 credentials, file descriptor hold logic, and disk media info.

Notable risks:
- Explicit block close handling is disabled with `#if 0`; cleanup relies on transaction delete handling.
- Bounds and permission enforcement are delegated to the raw device strategy/open paths.
- Comments show `kdmsg_state_hold/drop` are disabled, so state lifetime safety depends on kdmsg transaction serialization.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskiocom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel32.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel32.c

Legacy BSD 32-bit disklabel operations implementation for DragonFly disk slices.

Key responsibilities:
- Reads disklabel32 metadata from `LABELSECTOR32`, scanning the sector at long-word increments for a valid magic/checksum pair.
- Converts legacy absolute on-disk partition offsets to slice-relative in-core offsets via `l32_fixlabel()`.
- Exposes partition bounds, filesystem type, partition count, pack name, clone/virgin label creation, label writing, and label freeing through `disklabel32_ops`.
- Validates new labels, including magic/checksum, open partition compatibility, raw partition offset, slice bounds, and partition sizes.
- Writes labels by reading the existing label sector, finding an existing valid label location, replacing it, fixing offsets for disk format, and writing the sector back.
- Creates compatibility labels for unlabeled media, including raw partition and optional `a` partition.

Important behavior:
- In-core labels are always slice-relative, while on-disk 32-bit labels are adjusted back to absolute offsets when written.
- Open partitions cannot move or shrink; omitted filesystem metadata can inherit from the old open partition.
- The raw partition must start at offset 0 after in-core normalization.

Dependencies:
- Depends on disk slice state, UFS constants for boot/superblock sizes, `dkcksum32()`, pbuf synchronous I/O, and legacy disklabel structures.

Notable risks:
- No UUID information is available from disklabel32, so UUID aliases cannot come from this label format.
- The write path requires finding an existing valid label in the sector, making first-write or corrupted-label replacement awkward through this API.
- Size and offset fields are 32-bit-sector based and carry legacy 2TB-era limitations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel64.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel64.c

DragonFly 64-bit disklabel operations implementation with byte-granular offsets, UUIDs, CRC validation, and modern alignment defaults.

Key responsibilities:
- Reads disklabel64 metadata from offset 0 of the slice/device, using a sector-rounded I/O size.
- Validates magic, partition count, and CRC over the active disklabel64 region.
- Exposes partition bounds by converting byte offsets/sizes to media blocks.
- Loads per-partition filesystem type UUIDs, storage UUIDs, and legacy filesystem type values.
- Validates and applies new labels while preventing open partitions from moving, shrinking, or changing UUIDs.
- Writes labels with read-modify-write so reserved leading bytes not covered by the label payload are preserved.
- Creates compatibility labels and virgin labels, including storage UUID generation, boot area reservation, backup-label reservation, and 1 MiB physical alignment.

Important behavior:
- Partition offsets and sizes must be aligned to `dss_secsize`.
- Virgin labels reserve room for the label, stage2 boot area, and backup label area, and align usable partition space relative to the physical disk start.
- `l64_adjust_label_reserved()` write-protects the label area of a slice based on `d_bbase`.

Dependencies:
- Depends on `disklabel64`, disk slice state, kernel UUID generation, CRC32, pbuf synchronous I/O, and buffer helpers.

Notable risks:
- The label is sector-agnostic but still assumes the rounded label I/O fits in a pbuf.
- The read path derives the CRC span from the on-disk partition count before rejecting too-large counts, so corrupted counts rely on the surrounding validation and buffer sizing assumptions.
- Open partitions can grow but cannot move, shrink, or change type/storage UUIDs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskmbr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskmbr.c

MBR and extended-partition parser for DragonFly disk slice discovery, with GPT handoff support.

Key responsibilities:
- Reads the primary MBR, verifies the `0x55aa` signature, and falls back to a compatibility slice if the signature is missing.
- Detects protective GPT in the first DOS partition and delegates to `gptinit()`.
- Detects Ontrack Disk Manager and rereads the MBR from sector 63.
- Rejects historical DragonFly dangerously dedicated partition-table templates.
- Guesses CHS geometry from primary partition entries and updates disk info geometry fields without changing media size/block count.
- Allocates a full `MAX_SLICES` slice structure and populates primary and logical slices.
- Recursively walks extended partitions up to depth 16 and truncates slice count to `MAX_SLICES`.

Important behavior:
- `check_part()` compares CHS-derived sectors with LBA values but permits common pure-LBA and modulo-1024 CHS encodings.
- `mbr_setslice()` clamps/truncates slices extending past media end and special-cases `0xffffffff` size as likely >2TB media.
- Extended partition links use base extended offset for nested links and current extended offset for logical data partitions.

Dependencies:
- Depends on disk slice structures, DOS partition constants/macros, pbuf synchronous I/O, disk error printing, and GPT initialization.

Notable risks:
- MBR verification is intentionally weak and does not perform full overlap validation.
- Geometry inference is legacy CHS heuristic code and may only be diagnostic for modern LBA media.
- Extended partition parsing is bounded by recursion depth and `MAX_SLICES`; extra logical partitions are reported/dropped.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_diskmbr.c -->
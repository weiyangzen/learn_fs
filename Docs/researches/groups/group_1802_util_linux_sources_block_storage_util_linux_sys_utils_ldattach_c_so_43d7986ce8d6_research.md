# Group Research: group_1802_util_linux_sources_block_storage_util_linux_sys_utils_ldattach_c_so_43d7986ce8d6

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ldattach.c -->
# File Research: sources/block-storage/util-linux/sys-utils/ldattach.c

`ldattach.c` implements the `ldattach(8)` utility, which opens a serial tty, configures termios settings, attaches a Linux tty line discipline with `TIOCSETD`, and stays resident so the line discipline remains active.

Key behavior:
- Maintains lookup tables for supported line disciplines (`TTY`, `SLIP`, `PPP`, `GSM0710`, `PPS`, etc.) and termios input flags.
- Parses serial configuration options for speed, character size, parity, stop bits, input flags, intro command, intro pause, debug mode, and GSM0710 MTU.
- Uses `cfmakeraw()` and `tcsetattr()` to put the tty into raw mode before attaching the line discipline.
- Supports non-standard baud rates via `struct termios` `c_ispeed`/`c_ospeed` and `BOTHER` where available.
- Sends an optional intro command before attaching, then sleeps for a bounded pause.
- Applies GSM0710-specific configuration through `GSMIOC_GETCONF`/`GSMIOC_SETCONF`.
- Daemonizes unless `--debug` is used, then calls `pause()` to keep the process alive.

Important dependencies:
- Linux tty constants and ioctls from `<linux/tty.h>`, `<linux/gsmmux.h>` or the local fallback `struct gsm_config`.
- util-linux helpers for parsing, I/O, localization, diagnostics, and stdout cleanup.

Risk notes:
- `signal(SIGKILL, handler)` has no practical effect because `SIGKILL` cannot be caught.
- `gsm0710_set_conf()` ignores ioctl return values, so GSM configuration failures are silent.
- `parse_iflag()` mutates `optarg` with `strtok()`, which is acceptable for command-line storage but means the original string is destroyed.
- The process must remain alive for the discipline to remain attached; daemonization failure aborts setup after the ioctl has already succeeded.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/ldattach.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/losetup.c -->
# File Research: sources/block-storage/util-linux/sys-utils/losetup.c

`losetup.c` implements `losetup(8)`, the CLI for creating, listing, modifying, detaching, and removing Linux loop devices.

Key behavior:
- Defines action modes for create, detach, detach-all, list, show-one, find-free, set-capacity, set-direct-io, set-blocksize, and remove.
- Uses `struct loopdev_cxt` from util-linux loopdev helpers for all kernel loop interactions.
- Provides legacy text output through `printf_loopdev()` and structured table/JSON/raw output through `libsmartcols`.
- Supports listing all loop devices or only those associated with a backing file and offset.
- Implements `--nooverlap` checks to prevent conflicting loop mappings and to reuse exact matching non-encrypted mappings where safe.
- Handles setup flags for read-only, partition scan, direct I/O, offset, size limit, logical sector size, and reference string.
- Retries loop setup on transient `EBUSY`/`EAGAIN` for automatically selected loop devices.
- Warns for backing files smaller than 512 bytes or not aligned to 512-byte sector boundaries.

Important dependencies:
- `loopdev.h` owns loop ioctl details, backing-file metadata, iteration, overlap detection, and status queries.
- `libsmartcols` owns column definitions, JSON typing, raw output, and no-heading output.
- util-linux parsing helpers enforce numeric sizes and exclusive option groups.

Risk notes:
- The command has many mutually exclusive modes; correctness depends on the `ul_excl_t` tables and later contextual validation.
- `--direct-io` and `--sector-size` can modify existing loop devices when no create action is selected.
- Non-root listing can lack backing inode/device data, so output falls back to partial information.
- Reuse under `--nooverlap` deliberately rejects read-only-to-read-write transitions and encrypted overlaps.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/losetup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-arm.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-arm.c

`lscpu-arm.c` provides ARM/aarch64 CPU implementer and part-number decoding for `lscpu`.

Key behavior:
- Contains static implementer tables mapping ARM implementer IDs to vendor names and part-number tables.
- Covers ARM, Broadcom, Cavium, Qualcomm, Samsung, NVIDIA, Marvell, Apple, Fujitsu, HiSilicon, Ampere, Microsoft, Phytium, and others.
- Detects ARM for live systems by architecture name `aarch64`; for dumps it infers ARM from known implementer IDs.
- Converts raw `/proc/cpuinfo` implementer and part fields into human-readable vendor/model strings.
- Converts ARM revision/variant into `rXpY` stepping format for ARM implementer `0x41`.
- On live aarch64 systems, supplements model/vendor/family data from DMI when available.
- Detects a special “cluster” mode for aarch64 systems without ACPI PPTT and with a single CPU type.
- Implements `--arm-id`, `--arm-id=<id>`, and `--arm-id=<id> --arm-model=<id>` output backends.

Important dependencies:
- Shared `lscpu_cxt` and `lscpu_cputype` structures from `lscpu.h`.
- `libsmartcols` for ARM implementer/model table output.
- DMI helpers from `lscpu-dmi.c`.

Risk notes:
- Tables are manually maintained and must track new ARM implementers/parts.
- `HW_IMPL_NOOVERWRITE` for Phytium intentionally avoids replacing existing `/proc/cpuinfo` vendor/model strings.
- Cluster socket counts rely on DMI when ACPI PPTT is absent, which may be missing or inaccurate.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-arm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-cpu.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-cpu.c

`lscpu-cpu.c` owns allocation, reference counting, and lookup for per-logical-CPU objects.

Key behavior:
- `lscpu_new_cpu()` allocates a `struct lscpu_cpu`, initializes reference count and logical ID, and sets topology fields to `-1`.
- `lscpu_ref_cpu()` and `lscpu_unref_cpu()` manage CPU object lifetime.
- `lscpu_unref_cpu()` releases the associated CPU type and per-CPU frequency/BogoMIPS strings before freeing.
- `lscpu_create_cpus()` creates the context CPU array from a possible-CPU cpuset.
- `lscpu_cpu_set_type()` swaps a CPU’s referenced `struct lscpu_cputype` safely.
- `lscpu_get_cpu()` performs a linear lookup by logical CPU ID.

Important dependencies:
- CPU set macros and allocation sizing from util-linux cpuset support.
- CPU type reference management from `lscpu-cputype.c`.

Risk notes:
- Lookup is linear over possible CPUs; acceptable for this utility but not optimized for very large CPU counts.
- Callers must follow the comment on `lscpu_get_cpu()` and take a reference when retaining the returned pointer.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-cputype.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-cputype.c

`lscpu-cputype.c` parses CPU type data, architecture data, CPU lists, NUMA maps, vulnerabilities, and architecture-specific extras for `lscpu`.

Key behavior:
- Defines field pattern tables for `/proc/cpuinfo` CPU-type, per-CPU, and cache lines across many architectures.
- Parses `/proc/cpuinfo` into `struct lscpu_cputype` and `struct lscpu_cpu` objects.
- Deduplicates CPU types by vendor, model, model name, and stepping, then reassigns CPUs to canonical type objects.
- Parses extra cache descriptors from `/proc/cpuinfo`, especially for s390 shared caches not represented in sysfs topology.
- Reads architecture name from `uname()` and derives 32-bit/64-bit operation modes from platform macros, CPU flags, ISA strings, and live architecture names.
- Reads CPU possible/present/online masks from sysfs and creates the per-CPU array.
- Reads dispatching, frequency boost, s390 machine type, and PowerPC RTAS physical topology data when available.
- Reads CPU vulnerability files from sysfs, normalizes names, and sorts them.
- Reads NUMA node directories and cpumaps from sysfs.

Important dependencies:
- `lscpu.h` structures and path constants.
- util-linux `path_cxt`, cpuset, string, allocation, and numeric parsing helpers.
- Optional `librtas` for PowerPC processor module information.

Risk notes:
- The parser assumes field pattern arrays stay sorted because it uses `bsearch()`.
- `lookup()` implements “first one wins” semantics for matched fields.
- `/proc/cpuinfo` varies heavily by architecture, so new kernel fields require carefully adding sorted patterns.
- Some data, especially vulnerabilities and NUMA maps, may be absent and is treated as optional.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-cputype.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-dmi.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-dmi.c

`lscpu-dmi.c` decodes selected SMBIOS/DMI table data for aarch64 CPU reporting and socket counting.

Key behavior:
- Converts raw SMBIOS bytes into `struct lscpu_dmi_header`.
- Resolves SMBIOS string indices with `dmi_string()`.
- `parse_dmi_table()` walks DMI structures and extracts BIOS vendor, system manufacturer/product, and processor information.
- For processor records, it captures manufacturer, version, current/max speed, part number, processor family, and increments socket count.
- `dmi_decode_cputype()` reads `/sys/firmware/dmi/tables/DMI`, parses it, and populates BIOS CPU vendor/model/family fields.
- `get_number_of_physical_sockets_from_dmi()` returns the number of processor records found.

Important dependencies:
- `get_mem_chunk()` from `lscpu-virt.c`.
- DMI path `_PATH_SYS_DMI` from `lscpu.h`.

Risk notes:
- `parse_dmi_table()` uses `st.st_size / 4` as a synthetic structure count when callers do not know the true DMI count.
- Some field reads use raw casts to `uint16_t *`, so behavior assumes the platform tolerates unaligned little-endian SMBIOS reads.
- If DMI data is malformed, parsing stops and callers usually fall back silently.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-dmi.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-riscv.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-riscv.c

`lscpu-riscv.c` provides RISC-V ISA identification and formatting for `lscpu`.

Key behavior:
- `is_riscv()` checks whether the CPU type ISA begins with `rv32`, `rv64`, or `rv128`, case-insensitively.
- `lscpu_format_isa_riscv()` splits the ISA string on underscores, sorts multi-letter extensions alphabetically, and rewrites underscores as spaces.
- Keeps the base ISA and single-letter extension segment first.

Important dependencies:
- util-linux string-vector helpers `ul_strv_split()`, `ul_strv_length()`, and `ul_strv_free()`.
- Shared `struct lscpu_cputype`.

Risk notes:
- `lscpu_format_isa_riscv()` assumes `ct->isa` is writable and large enough for the reformatted string; the comment notes the length stays the same.
- It does not guard against `ct->isa == NULL`; callers check `ct->isa` before invoking.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-riscv.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-topology.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-topology.c

`lscpu-topology.c` reads CPU topology, frequency, cache, and selected per-CPU status attributes from sysfs and `/proc/sysinfo`.

Key behavior:
- Builds unique core, socket, book, and drawer CPU-set maps per CPU type.
- Skips CPUs that are not fully online when hotplug state information is available.
- Reads s390 software topology from `/proc/sysinfo` and falls back to sysfs-derived ratios otherwise.
- Reads per-CPU physical topology IDs: core, socket/package, book, and drawer.
- Reads s390 polarization, physical address, and configured status attributes.
- Reads max/min/current CPU frequency from cpufreq sysfs.
- Reads standard cache topology from `cpuN/cache/indexM`, including type, level, ID, size, sharing map, allocation/write policy, line size, set count, and associativity.
- Provides a SPARC fallback for cache files such as `l1_icache_size`.
- Sorts caches by name and exposes helpers for total cache size and per-CPU cache lookup.

Important dependencies:
- `path_cxt` sysfs access helpers.
- CPU-set allocation and operations.
- Shared CPU and CPU-type structures.

Risk notes:
- Cache identity is based on type, level, and kernel cache ID; if ID is unavailable, it synthesizes one from sharing maps.
- SPARC fallback assumes caches are private when no sharing map exists.
- Topology ratios such as cores per socket are derived from counts and can be zero or misleading on unusual virtualized systems.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-topology.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-virt.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu-virt.c

`lscpu-virt.c` detects virtualization features, hypervisor vendor, and virtualization type for `lscpu`.

Key behavior:
- Reads arbitrary memory chunks from files through `get_mem_chunk()`, shared with DMI parsing.
- Detects hypervisors from SMBIOS/DMI data in sysfs or `/dev/mem`.
- Detects common virtual PCI devices for Xen, VMware, and VirtualBox.
- On x86, reads CPUID hypervisor leaf `0x40000000`.
- On x86, optionally probes VMware’s backdoor I/O port under a temporary SIGSEGV handler, only as root.
- Detects WSL first via `/proc/sys/kernel/osrelease`.
- Handles Xen features to distinguish full virtualization from paravirtual/PVH cases.
- Handles PowerPC virtualization through device-tree compatibility and partition metadata.
- Handles s390 PR/SM and KVM from `/proc/sysinfo`.
- Detects OpenVZ/Virtuozzo, User-mode Linux, and Linux-VServer container/paravirtual cases.
- Exposes `lscpu_read_virtualization()` and `lscpu_free_virtualization()`.

Important dependencies:
- DMI parser from `lscpu-dmi.c`.
- `/proc`, `/sys`, `/dev/mem`, CPUID, device-tree, and optional low-level I/O support.
- Shared virtualization enums in `lscpu.h`.

Risk notes:
- `/dev/mem` DMI probing may fail for permission or kernel lockdown reasons and is treated as optional.
- VMware backdoor probing is fragile and intentionally guarded by root and SIGSEGV handling.
- Detection order matters; WSL is checked before VMware probing due to known crash risk.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu-virt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu.c

`lscpu.c` is the main program and output layer for the `lscpu(1)` CPU architecture reporting utility.

Key behavior:
- Owns `struct lscpu_cxt` creation, path initialization, full data-gathering sequence, output mode dispatch, and cleanup.
- Defines CPU table columns, cache table columns, virtualization labels, hypervisor labels, dispatch modes, and polarization strings.
- Supports summary, extended table, parsable table, cache table, ARM implementer/model lookup, raw, JSON, byte sizes, physical IDs, sysroot snapshots, and hierarchical summaries.
- Formats per-CPU table cells for CPU ID, topology IDs, NUMA node, cache-sharing IDs, polarization, address, configured/online state, microcode, MHz values, and model name.
- Formats cache table rows for one-cache size, total system cache size, type, level, ways, policies, line partitions, sets, and coherency size.
- Builds the default summary from architecture, CPU masks, CPU type details, virtualization, caches, NUMA, and vulnerabilities.
- Coordinates data collection in order: CPU lists, cpuinfo, architecture, arch extras, vulnerabilities, NUMA, topology, ARM decode, virtualization.
- Uses environment variables `LSCPU_COLUMNS` and `LSCPU_CACHES_COLUMNS` for default custom columns.

Important dependencies:
- All companion `lscpu-*` modules and shared `lscpu.h`.
- `libsmartcols` for summary/table/JSON/raw output.
- util-linux sysfs/path, cpuset, parsing, annotation, and localization helpers.

Risk notes:
- Output defaults depend on gathered data, so missing sysfs/procfs attributes change column sets.
- Parsable output has a compatibility mode that treats cache columns specially with historical comma formatting.
- JSON type handling is adjusted when values are missing and rendered as `-`.
- Hierarchical summary defaults to TTY detection unless explicitly set.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu.h -->
# File Research: sources/block-storage/util-linux/sys-utils/lscpu.h

`lscpu.h` is the shared interface and data model for all `lscpu` implementation files.

Key contents:
- Debug mask declarations for init, misc, gather, type, CPU, and virtualization domains.
- Sysfs/procfs path constants for CPU, node, DMI, ACPI PPTT, and Xen hypervisor features.
- `struct lscpu_cache` describing cache identity, type/name, policies, size, geometry, and shared CPU map.
- `struct lscpu_cputype` describing vendor/model/family strings, BIOS strings, topology counts, sibling maps, flags, frequency fields, s390/PowerPC-specific fields, and ISA.
- `struct lscpu_cpu` describing one logical CPU, including type reference, frequency fields, topology IDs, polarization, address, and configured state.
- `struct lscpu_arch`, `struct lscpu_virt`, `struct lscpu_vulnerability`, DMI structs, virtualization enums, output mode enums, and helper macros.
- Function declarations for CPU/type lifetime, parsing, topology, caches, architecture, virtualization, ARM/RISC-V formatting, DMI, memory chunks, and NUMA/vulnerability reads.

Important dependencies:
- util-linux core headers for allocation, cpuset, path handling, string parsing, I/O, bit operations, debug, and localization.

Risk notes:
- This header couples all `lscpu` modules around mutable shared structs.
- Reference-counted CPU and CPU-type ownership must be respected across modules.
- Field additions require coordinated updates in parsing, output, freeing, and architecture-specific decode paths.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lscpu.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsipc.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lsipc.c

`lsipc.c` implements `lsipc(1)`, a flexible System V and POSIX IPC reporting utility.

Key behavior:
- Supports System V shared memory, message queues, semaphores, and global IPC limits.
- Supports POSIX shared memory, POSIX message queues, and POSIX semaphores.
- Defines one shared column table with generic, POSIX, message, shared-memory, semaphore, summary, and POSIX-semaphore-specific columns.
- Enforces resource-specific column applicability via global `LOWER`/`UPPER` bounds.
- Supports output modes: list, pretty, export, newline, raw, and JSON.
- Supports owner/creator columns, time columns, numeric permissions, byte sizes, shell-safe names, no headings, and no truncation.
- Pretty mode prints a single resource as key/value rows and can include a subtable of semaphore elements.
- Uses `ipcutils` helpers to collect IPC data and limits.
- Uses `pid_get_cmdline()` for creator/last-user command display.
- Uses `make_time()` for short, full, and ISO timestamps.

Important dependencies:
- `ipcutils.h` and related IPC helper implementations for System V/POSIX enumeration.
- `libsmartcols` for all tabular and JSON output.
- passwd/group lookup APIs for user/group name resolution.
- util-linux time, string, parsing, and option-exclusion helpers.

Risk notes:
- Option exclusivity is complex because resource selection, global mode, ID/name lookup, and output modes interact.
- `LOWER`/`UPPER` are mutable globals set by selected resource mode; custom columns rely on them being set correctly.
- Some POSIX global reporting is compiled out when message queue headers are unavailable.
- There appears to be a likely typo in the System V shared-memory `COL_CGID` case: it prints `p->shm_perm.cuid` instead of `p->shm_perm.cgid`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsipc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsirq.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lsirq.c

`lsirq.c` implements `lsirq(1)`, a command-line frontend for displaying interrupt or softirq counters.

Key behavior:
- Delegates data parsing and table construction to shared IRQ helpers through `get_scols_table()`.
- Supports JSON, key-value pairs, no headings, custom columns, sorting, input-file override, softirq mode, counter threshold, and CPU-list filtering.
- Defaults to `/proc/interrupts` or `/proc/softirqs` depending on `--softirq`.
- Defaults output columns to IRQ, total, and name.
- Parses CPU lists into a dynamically allocated cpuset sized from the system maximum CPU count.
- Prints column help via `irq_print_columns()`.

Important dependencies:
- `irq-common.h`/`irq-common.c` for column definitions, parsing, sorting, and smartcols table creation.
- util-linux cpuset and option-exclusion helpers.
- `libsmartcols` through the IRQ common layer.

Risk notes:
- JSON and pairs output are mutually exclusive.
- Invalid CPU count discovery aborts `--cpu-list`.
- The file itself is intentionally thin; most correctness lives in `irq-common`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsirq.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsmem.c -->
# File Research: sources/block-storage/util-linux/sys-utils/lsmem.c

`lsmem.c` implements `lsmem(1)`, which reports Linux memory block ranges, online/offline state, removability, NUMA node, zones, firmware memory configuration, and summary totals.

Key behavior:
- Reads memory block data from `/sys/devices/system/memory`.
- Optionally reads configured and memmap-on-memory state from `/sys/firmware/memory`.
- Supports table, summary, summary-only, JSON, raw, pairs/export, bytes, sysroot, all-blocks, custom columns, split policy, and annotated headers.
- Groups adjacent memory blocks into ranges unless `--all` is used or selected split fields differ.
- Default columns are range, size, state, removable, and block.
- Can split ranges by state, node, removable flag, zones, firmware configuration, and memmap-on-memory.
- Reads memory block size from `block_size_bytes`.
- Detects NUMA node membership by scanning `memoryN/nodeX` entries.
- Detects zone support through `valid_zones` and parses zone names.
- Computes online/offline memory totals while reading blocks.
- Prints memory hotplug `memmap_on_memory` module parameter when available.

Important dependencies:
- `path_cxt` for sysfs and sysroot-safe path access.
- `libsmartcols` for table/JSON/raw/export output.
- util-linux size formatting, option exclusivity, annotation, and allocation helpers.

Risk notes:
- The firmware memory configuration tree is optional and columns are skipped when unavailable.
- Summary-only mode returns early without freeing path contexts, relying on process exit cleanup.
- Block merging depends on sorted `versionsort()` directory results and contiguous block indices.
- `read_info()` counts each memory config directory as one block-size unit for totals, even when firmware config is used as the iteration source.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/lsmem.c -->
# subset-b-006575 research

Grouped research for the requested Hyper-V tools, IIO tools, and tools/include compatibility headers. Each section is bounded by the required source-path markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_kvp_daemon.c -->
# sources/distributed-fs/ceph-client/tools/hv/hv_kvp_daemon.c

## Purpose

`hv_kvp_daemon.c` is the Linux user-space Hyper-V Key Value Pair daemon. It registers with the kernel driver through `/dev/vmbus/hv_kvp`, services host requests, persists guest/host KVP pools, reports auto-generated guest facts such as OS version and IP addresses, and applies host-provided network configuration through a distribution-specific helper script.

## Important APIs, Types, and Functions

The file uses Hyper-V ABI structures and constants from `<linux/hyperv.h>`, especially `struct hv_kvp_msg`, `struct hv_kvp_ipaddr_value`, `KVP_OP_*`, `KVP_POOL_*`, and `HV_*` status codes. Local storage is modeled with `struct kvp_record` and `struct kvp_file_state`; `kvp_file_info[KVP_POOL_COUNT]` tracks file descriptors, backing filenames, allocated blocks, and in-memory records. Core pool functions are `kvp_file_init`, `kvp_update_mem_state`, `kvp_update_file`, `kvp_key_add_or_modify`, `kvp_get_value`, `kvp_key_delete`, and `kvp_pool_enumerate`. Host-facing network operations use `kvp_mac_to_ip`, `kvp_get_if_name`, `kvp_get_ip_info`, and `kvp_set_ip_info`. OS identity helpers include `kvp_get_os_info` and `kvp_get_domain_name`.

## Control Flow and State

Startup parses `--no-daemon`, `--debug`, and `--help`, optionally daemonizes, initializes syslog, reads OS/domain data, and creates or loads `/var/lib/hyperv/.kvp_pool_<n>` files. The daemon opens `/dev/vmbus/hv_kvp`, writes a `KVP_OP_REGISTER1` message, then blocks in `poll`. Each request is read, decoded by operation, answered in the same message buffer, and written back to the kernel. Short reads or writes reopen the device, which handles hibernation and kernel-side reset cases. Persistent state lives in fixed-size record files under `/var/lib/hyperv`; `fcntl` write locks protect file reads and rewrites. Network SET operations also persist generated `ifcfg-<ifname>` and `<ifname>.nmconnection` files under `/var/lib/hyperv` before invoking `hv_set_ifconfig`.

## Dependencies and Integration Points

The daemon depends on the Hyper-V kernel vmbus KVP device, `/sys/class/net`, `/etc/os-release` or legacy release files, libc networking APIs, `ip`, and helper scripts under `KVP_SCRIPTS_PATH` such as `hv_get_dns_info`, `hv_get_dhcp_info`, and `hv_set_ifconfig`. It integrates with host Hyper-V Data Exchange and network injection flows. The generated NetworkManager and ifcfg files are intended as an intermediate distro-neutral contract between the C daemon and the external distro-specific script.

## Risks

The daemon runs as a privileged service and executes shell commands assembled from configured script paths and interface names, so argument construction and deployment paths are security-sensitive. Pool file rewrites rewrite the whole record array and exit on many I/O failures, which can terminate the service if `/var/lib/hyperv` is unavailable. Network parsing has many fixed-size buffers and semicolon-delimited formats; malformed or oversized host-provided address, gateway, DNS, or subnet strings can lead to failed configuration. IPv6 and NetworkManager method decisions are subtle, especially when DHCP is true but only IPv6 data is supplied. External helper failures are reported as Hyper-V failures but may leave intermediate config files behind.

## Test Signals

Useful tests include building the tool against the current kernel UAPI, running KVP set/get/delete/enumerate operations through `/dev/vmbus/hv_kvp`, checking file locking and reload behavior with concurrent pool modifications, validating auto enumeration values, and testing GET/SET IP flows on IPv4, IPv6, DHCP, static, no-address, and multi-address interfaces. Integration tests should confirm helper script invocation, generated `ifcfg` and `.nmconnection` contents, device reopen after simulated hibernation, and error propagation to the host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_kvp_daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_set_ifconfig.sh -->
# sources/distributed-fs/ceph-client/tools/hv/hv_set_ifconfig.sh

## Purpose

This shell script is the distro-specific network configuration hook invoked by `hv_kvp_daemon.c` after a host sends Hyper-V KVP IP configuration. The daemon writes an ifcfg-style file and a NetworkManager keyfile; this script installs them and cycles the target interface.

## Important APIs and Flow

The script appends `IPV6INIT=yes`, `NM_CONTROLLED=no`, `PEERDNS=yes`, and `ONBOOT=yes` to the first argument, copies that ifcfg file into `/etc/sysconfig/network-scripts/`, sets `umask 0177`, derives an interface name from the second argument with `awk -F - '{ print $2 }'`, inserts `autoconnect=true` after `[connection]`, writes the result to `/etc/NetworkManager/system-connections/<filename>`, then runs `/sbin/ifdown` and `/sbin/ifup` on the inferred interface.

## State, Dependencies, and Integration

The script mutates host guest network configuration in `/etc/sysconfig/network-scripts` and `/etc/NetworkManager/system-connections`. It assumes a RHEL-like system with legacy network scripts, NetworkManager keyfile support, `/sbin/ifdown`, `/sbin/ifup`, `sed`, `awk`, and root privileges. It is tightly coupled to `hv_kvp_daemon.c`, which supplies the two path arguments and expects persistent interface configuration after the script exits.

## Risks and Test Signals

Arguments are unquoted in several command positions, making spaces or shell metacharacters in generated paths unsafe. Interface derivation from `$2` with `-` as delimiter is fragile for arbitrary filenames and appears inconsistent with the daemon's `<ifname>.nmconnection` naming. The script appends to the ifcfg file each run, so repeated calls can duplicate keys. Tests should run it in a disposable rootfs or namespace with generated files, verify copied content and file permissions, and cover interface names with expected and unexpected formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_set_ifconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_vss_daemon.c -->
# sources/distributed-fs/ceph-client/tools/hv/hv_vss_daemon.c

## Purpose

`hv_vss_daemon.c` implements the Hyper-V host-initiated guest snapshot service. It registers with `/dev/vmbus/hv_vss`, receives freeze/thaw/check messages from the kernel, and freezes or thaws mounted guest filesystems so the host can take a consistent backup checkpoint.

## Important APIs, Types, and Functions

The daemon uses `struct hv_vss_msg`, `VSS_OP_REGISTER1`, `VSS_OP_FREEZE`, `VSS_OP_THAW`, `VSS_OP_HOT_BACKUP`, and Hyper-V error codes from `<linux/hyperv.h>`. `vss_do_freeze` opens a mount point and issues `FIFREEZE` or `FITHAW`; it treats `EBUSY` on freeze and `EINVAL` on thaw as success for duplicate mounts of the same backing device. `is_dev_loop` walks `/sys/dev/block/<major>:<minor>` and its `slaves` recursively to skip loop-backed devices. `vss_operate` scans `/proc/mounts`, filters unsuitable mounts, freezes non-root mounts first, freezes root last, and rolls back on failure.

## Control Flow and State

Startup parses foreground/help options, optionally daemonizes, opens syslog, opens `/dev/vmbus/hv_vss`, and registers. The first read during handshake is a kernel module version, then the main loop blocks in `poll`, reads a full `hv_vss_msg`, performs the requested operation, stores `error`, and writes the response. `fs_frozen` is the only process state. On device reopen, the daemon thaws if `fs_frozen` is true before re-registering, preventing a stale frozen guest after hibernation or channel reset.

## Dependencies and Integration Points

It depends on the Hyper-V VSS kernel device, Linux freeze/thaw ioctls, `/proc/mounts`, `/sys/dev/block`, device major/minor mapping, syslog, and root privileges. It integrates with host backup/checkpoint orchestration and with filesystem drivers that support `FIFREEZE`/`FITHAW`.

## Risks and Test Signals

Freezing filesystems is high impact. The code intentionally avoids syslog inside `vss_do_freeze` because logging may write to frozen storage. The root-last ordering and rollback path are critical; bugs can leave filesystems frozen. Filtering skips read-only, `vfat`, loop-backed, and non-`/dev/` mounts, so coverage depends on mount topology. Tests should simulate `/proc/mounts` patterns where possible, run freeze/thaw on disposable filesystems, validate duplicate-mount handling, check loop-device skipping, and verify that failed freeze attempts thaw previous mounts and report `HV_E_FAIL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_vss_daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/lsvmbus -->
# sources/distributed-fs/ceph-client/tools/hv/lsvmbus

## Purpose

`lsvmbus` is a Python 3 diagnostic utility that lists Hyper-V VMBus devices visible in sysfs. It maps well-known Hyper-V class GUIDs to readable device descriptions and prints channel-to-CPU mappings at higher verbosity.

## Important APIs and Flow

The script uses `optparse` for `-v/--verbose`, reads `/sys/bus/vmbus/devices`, and uses `get_vmbus_dev_attr` to read attributes such as `id`, `class_id`, `device_id`, and `channel_vp_mapping`. It builds lightweight `VMBus_Dev` objects, sorts them by numeric VMBus ID, and prints three output formats: terse description, class ID with mapping, or class ID, device ID, sysfs path, and mapping.

## State, Dependencies, and Integration

There is no persistent state. Runtime state is derived entirely from sysfs. It depends on the Hyper-V bus being present and exposing expected attributes. It integrates with `vmbus_testing` and administrator workflows by giving users the device identity and sysfs paths needed for further inspection.

## Risks and Test Signals

The script assumes each device has readable `id`, `class_id`, and `device_id`; missing attributes can raise indexing errors. It sorts mapping lines by the left side of `relid:cpu`, so malformed entries also fail. Tests should run on a Hyper-V guest, on a fake sysfs tree via refactoring or monkeypatching, and with verbosity levels 0, 1, and 2. Compatibility tests should include unknown class IDs and devices without channel mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/lsvmbus -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.c -->
# sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.c

## Purpose

`vmbus_bufring.c` implements user-space helpers for Hyper-V VMBus ring buffers and channel packets. It maps shared ring memory, initializes ring descriptors, sends in-band packets, and receives raw packets from a VMBus channel ring.

## Important APIs and Functions

Exported functions are `vmbus_uio_map`, `vmbus_br_setup`, `rte_vmbus_chan_send`, and `rte_vmbus_chan_recv_raw`. Internal helpers include `vmbus_br_idxinc`, `rte_smp_mb`, `rte_atomic32_cmpset`, `vmbus_txbr_copyto`, `vmbus_txbr_write`, `vmbus_rxbr_copyfrom`, `vmbus_rxbr_peek`, and `vmbus_rxbr_read`. The code uses `struct vmbus_br`, `struct vmbus_bufring`, `struct vmbus_chanpkt`, and `struct vmbus_chanpkt_hdr` from `vmbus_bufring.h`.

## Control Flow and State

`vmbus_uio_map` maps two ring pages from a file descriptor with `mmap`. `vmbus_br_setup` stores the ring pointer, snapshots the write index, and computes usable data size. Sending computes packet length and 8-byte padding, reserves a contiguous logical region by CAS-ing the private write index, copies scatter/gather data with wraparound handling, appends the saved packet offset, then waits until it can publish the host-visible write index. Receiving peeks the packet header, validates header and total lengths, checks caller buffer size, reads packet data with wraparound, skips the trailing offset, and advances the ring read index after a compiler barrier.

## Dependencies and Integration

The file depends on x86 atomic and pause instructions, SSE2 `_mm_pause`, `mmap`, `struct iovec`, and the VMBus ABI layout in the companion header. It appears intended for tools that interact with Hyper-V UIO mappings and must match kernel/host ring semantics exactly.

## Risks and Test Signals

Ring index arithmetic, padding, and memory ordering are correctness-critical. `ALIGN` is a down-align macro here, so callers rely on packet lengths already being compatible with expected alignment behavior. Multi-writer send support depends on the private `tbr->windex` CAS and the publish-order spin loop. Tests should cover wraparound copies, full-ring `-EAGAIN`, invalid packet headers, too-small receive buffers, 32-bit index rollover, and host interoperability on real VMBus mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.h -->
# sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.h

## Purpose

`vmbus_bufring.h` defines the user-space ABI structures and constants used by `vmbus_bufring.c` for Hyper-V VMBus ring buffers, channel packets, and integration-component message negotiation.

## Important APIs and Types

The header defines packet types and flags such as `VMBUS_CHANPKT_TYPE_INBAND`, `VMBUS_CHANPKT_FLAG_RC`, and `VMBUS_CHANPKT_HLEN_MIN`. `struct vmbus_bufring` mirrors the shared ring header, including volatile write/read indexes, interrupt mask, pending-send feature state, page-sized padding, and flexible `data[]`. `struct vmbus_br` is the local ring handle. Packet and integration-service structures include `vmbus_chanpkt_hdr`, `vmbus_chanpkt`, `vmbuspipe_hdr`, `ic_version`, `icmsg_negotiate`, and `icmsg_hdr`. Inline helpers expose available write and read space.

## State, Dependencies, and Integration

The persistent state is shared memory owned by the VMBus channel, not this header. Consumers must map a buffer whose layout matches `struct vmbus_bufring`. The prototypes connect to `vmbus_bufring.c`; the negotiation structures are used by Hyper-V integration-service tools that need to form or parse IC messages.

## Risks and Test Signals

This header encodes wire and shared-memory layout. Packing, volatile fields, padding size, and flexible-array placement must remain compatible with the kernel and host. `vmbus_br_availwrite` deliberately leaves one byte/slot distinction to identify full versus empty rings; off-by-one changes can deadlock or corrupt data. Tests should compile users on supported architectures, assert structure offsets and sizes, and run send/receive interoperability against a real or simulated VMBus ring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/vmbus_testing -->
# sources/distributed-fs/ceph-client/tools/hv/vmbus_testing

## Purpose

`vmbus_testing` is a Python 3 command-line tool for enabling, disabling, and viewing Hyper-V VMBus fuzz-test controls exposed through debugfs. Its current test method controls buffer interrupt delay and message delay attributes.

## Important APIs and Flow

The script uses `argparse` subcommands: `delay`, `disable_all`/`D`, `disable_single`/`d`, `view_all`/`V`, and `view_single`/`v`. It expects `/sys/kernel/debug/hyperv` and recursively builds a `file_map` from device directories to debugfs files. Enums `dev_state` and `f_names` define on/off values and known file names: `fuzz_test_state`, `fuzz_test_buffer_interrupt_delay`, and `fuzz_test_message_delay`. Helper functions validate paths and delay ranges, read and write debugfs attributes, locate per-device state files, set delays for one or all devices, and disable tests.

## State, Dependencies, and Integration

The script does not persist its own state; it writes kernel debugfs attributes that affect Hyper-V driver behavior. It depends on debugfs being mounted, Hyper-V debugfs support, file permissions, and the exact file names from `drivers/hv/debugfs.c`. `lsvmbus` is referenced as the way to identify device types before using paths.

## Risks and Test Signals

It exits on invalid inputs and I/O failures, which is appropriate for a test tool but means partial writes can occur during all-device operations. Recursive discovery assumes a stable debugfs directory shape and uses string splitting to print device names. Delay values allow `-1` as keep-previous but reject zero and values above 1000 microseconds. Tests should use a fake debugfs tree for parser and file-map behavior, plus real Hyper-V debugfs tests for delay effects and cleanup through `disable_all`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/vmbus_testing -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/Makefile -->
# sources/distributed-fs/ceph-client/tools/iio/Makefile

## Purpose

This Makefile builds and installs the user-space Industrial I/O example tools: `iio_event_monitor`, `lsiio`, and `iio_generic_buffer`.

## Important Targets and Variables

It imports `../scripts/Makefile.include`, derives `srctree` when unset, disables built-in rules with `MAKEFLAGS += -r`, and augments `CFLAGS` with optimization, warnings, debug info, `_GNU_SOURCE`, and `-I$(OUTPUT)include`. `prepare` creates `$(OUTPUT)include/linux/iio` and symlinks UAPI headers `buffer.h`, `events.h`, and `types.h`. Each program has an intermediate `*-in.o` target built through `tools/build`, then a final link step with `$(CC)`. `clean` removes binaries, generated include symlinks, objects, dependency files, and command files. `install` copies programs into `$(DESTDIR)$(bindir)`.

## State, Dependencies, and Integration

Build outputs live under `$(OUTPUT)`, enabling out-of-tree builds. The Makefile depends on the kernel tools build system and UAPI IIO headers. It integrates the shared `iio_utils` object into all three tools.

## Risks and Test Signals

The symlink preparation assumes kernel source-relative paths and may fail outside the expected tree. `clean` uses `find $(or $(OUTPUT),.)`, so an unexpected empty or broad `OUTPUT` value deserves caution. Tests are `make -C tools/iio`, out-of-tree `O=` or `OUTPUT=` builds, `make clean`, and staged `make install DESTDIR=...`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_event_monitor.c -->
# sources/distributed-fs/ceph-client/tools/iio/iio_event_monitor.c

## Purpose

`iio_event_monitor.c` is an example and diagnostic program that opens an IIO character device, retrieves its event file descriptor, reads `struct iio_event_data` events, decodes event IDs, and prints readable event descriptions.

## Important APIs and Functions

It uses IIO UAPI headers `<linux/iio/events.h>` and `<linux/iio/types.h>`, plus helpers from `iio_utils.h`. Large lookup tables map channel types, event types, event directions, and modifiers to text. `event_is_known` validates decoded enum values before indexing those tables. `print_event` extracts channel type, modifier, event type, direction, channel numbers, and differential flag with `IIO_EVENT_CODE_EXTRACT_*` macros. `enable_events` scans `<device>/events` for `*_en` attributes and writes enable or disable values. `main` handles `-a`, resolves a device name to `/dev/iio:deviceN`, opens the character device, issues `IIO_GET_EVENT_FD_IOCTL`, closes the main fd, then reads events in a loop.

## State, Dependencies, and Integration

The program's only persistent side effect is optional enabling/disabling of event sysfs knobs when `-a` is used. It depends on IIO sysfs under `/sys/bus/iio/devices`, IIO character devices under `/dev`, and device support for event fds. It integrates with `iio_utils.c` for name lookup and sysfs writes.

## Risks and Test Signals

The event loop is unbounded and exits only on read failure. If the process is killed before normal cleanup after `-a`, enabled event knobs may remain enabled. Event enum coverage must track the UAPI or new event codes print as unknown. Tests should compile against current UAPI, run on devices with and without event support, verify `-a` enables and later disables sysfs attributes, and feed known synthetic event IDs to `event_is_known` and `print_event`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_event_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_generic_buffer.c -->
# sources/distributed-fs/ceph-client/tools/iio/iio_generic_buffer.c

## Purpose

`iio_generic_buffer.c` captures buffered samples from an IIO device, converts raw scan data using channel metadata, and prints values in scaled units. It is both an example program and a diagnostic tool for triggers, buffers, and channel layout.

## Important APIs and Functions

The program uses IIO buffer UAPI `IIO_BUFFER_GET_FD_IOCTL` and shared helpers from `iio_utils`. `size_from_channelarray` computes aligned scan size and per-channel byte locations. `print1byte`, `print2byte`, `print4byte`, and `print8byte` handle endian conversion, shifts, masks, signed extension, offset, and scale. `process_scan` dispatches per-channel printing. `enable_disable_all_channels` writes `*_en` scan-element attributes. `cleanup` disconnects triggers, disables buffers, and disables auto-enabled channels. Signal handlers call cleanup on interrupt, termination, and abort. `main` parses device, trigger, buffer, loop count, length, eventless, triggerless, and auto-channel options.

## Control Flow and State

After option parsing, the tool resolves a device by name or number, resolves or constructs a trigger unless triggerless mode is selected, builds the enabled channel array, optionally auto-enables channels and rebuilds metadata, constructs a buffer directory, sets `trigger/current_trigger`, opens `/dev/iio:deviceN`, obtains the indexed buffer fd through ioctl, writes buffer length, enables the buffer, computes scan size, allocates a read buffer, and loops polling or sleeping before reading and printing scans. Global variables track configured resources so `cleanup` can undo state at normal exit and on signals.

## Dependencies and Integration

It depends on IIO sysfs, IIO character devices, scan element metadata, optional triggers, and `iio_utils.c`. It integrates with drivers that expose buffer directories and scan elements, and it demonstrates the newer buffer-fd ioctl flow.

## Risks and Test Signals

Sysfs writes mutate live device state, so cleanup correctness matters. The code guards against `scan_size * buf_len` overflow, but many allocations and sysfs reads can fail after partial configuration. Channel formats outside 1, 2, 4, or 8 bytes are silently skipped. Tests should cover named and numeric device/trigger selection, triggerless and eventless modes, auto-channel modes, cleanup after errors and signals, endian/sign extension conversion, multiple buffer indexes, and devices without enabled channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_generic_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_utils.c -->
# sources/distributed-fs/ceph-client/tools/iio/iio_utils.c

## Purpose

`iio_utils.c` provides shared sysfs utilities for the IIO example tools. It discovers IIO devices and triggers, reads channel metadata, builds sorted channel arrays, and reads/writes typed sysfs attributes.

## Important APIs and Functions

The exported `iio_dir` points to `/sys/bus/iio/devices/`. `iioutils_break_up_name` strips direction prefixes and digits to derive a generic channel name. `iioutils_get_type` parses scan element type strings like endian/sign/bits/storage/shift into channel layout fields. `iioutils_get_param_float` reads per-channel scale and offset, trying specific and generic names. `build_channel_array` scans `bufferN/*_en`, counts enabled channels, allocates `struct iio_channel_info` entries, reads indexes, scale, offset, and type data, then sorts by index. `find_type_by_name` searches IIO top-level entries for a matching `name` file. The read/write helpers handle integer, float, and string sysfs access with optional verification.

## Control Flow and State

The file has no durable state beyond sysfs mutations done by write helpers. Most functions allocate temporary path strings with `asprintf` or `malloc`, open directories and files, return negative errno-style errors, and clean up on failure. `build_channel_array` is the central state-construction path used by buffered readers: it produces an owned array whose strings must be freed by the caller.

## Dependencies and Integration

The utilities depend on stable IIO sysfs layout, scan-element naming conventions, and libc directory/file APIs. They are integrated by `iio_generic_buffer`, `iio_event_monitor`, and `lsiio`, and the header exposes their contracts.

## Risks and Test Signals

Several functions assume filenames have expected suffix lengths before subtracting suffix lengths; unusual sysfs entries could stress those assumptions. String reads use `%s`, so names with whitespace are truncated. `find_type_by_name` skips entries with colon after the numeric suffix to avoid char devices. Tests should use fake sysfs trees for channel parsing, scale/offset fallback, enabled-channel counting, sorting, verified write mismatch, and error cleanup, plus live tests against real IIO devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_utils.h -->
# sources/distributed-fs/ceph-client/tools/iio/iio_utils.h

## Purpose

`iio_utils.h` declares the shared helper interface and channel metadata structure used by the IIO example tools.

## Important APIs and Types

The header defines `IIO_MAX_NAME_LENGTH`, format strings for buffer and event sysfs directories, `ARRAY_SIZE`, and external `iio_dir`. `struct iio_channel_info` captures channel name, generic name, scale, offset, index, storage bytes, used bits, shift, mask, endian flag, signed flag, and computed scan location. Inline `iioutils_check_suffix` tests suffixes safely. Function prototypes cover channel-name parsing, float parameter lookup, channel array building and sorting, device/trigger lookup, and integer/string/float sysfs access.

## State, Dependencies, and Integration

The header itself has no state; it defines ownership expectations for allocated channel arrays and strings returned by `iio_utils.c`. It depends on `<stdint.h>` and on consumers including standard string declarations before using the inline function, as the header calls `strlen` and `strncmp`.

## Risks and Test Signals

Changes to `struct iio_channel_info` affect every IIO tool's scan parsing and cleanup loops. Format constants must match actual sysfs layout. Tests should compile all IIO tools with warnings enabled and run channel-array construction on devices with multiple channels, mixed endianness, and scale/offset attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/iio_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/lsiio.c -->
# sources/distributed-fs/ceph-client/tools/iio/lsiio.c

## Purpose

`lsiio.c` lists Industrial I/O devices and triggers available under IIO sysfs, optionally showing sensor channel attributes.

## Important APIs and Flow

The tool uses `iio_dir` and `read_sysfs_string` from `iio_utils`. Local helpers check prefixes and postfixes, dump input channels ending in `_raw` or `_input`, print one device by parsing its numeric suffix and reading its `name`, and print one trigger similarly. `dump_devices` scans the IIO sysfs directory twice: first for `iio:device*`, then for `trigger*`. `main` accepts repeated `-v`; default output resembles `lspci`, while verbosity level 1 lists sensor raw/input attributes below each device.

## State, Dependencies, and Integration

There is no persistent state. The tool depends on `/sys/bus/iio/devices/`, readable `name` files, and the shared sysfs helper implementation. It integrates with the other IIO examples as a discovery command for device and trigger names.

## Risks and Test Signals

The prefix check requires names to be longer than the prefix, so exact-prefix entries are ignored. Errors while dumping one entry abort the whole listing. Tests should run against fake and real IIO sysfs trees, covering no-device behavior, devices with missing names, trigger listings, and `-v` channel display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/iio/lsiio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/atomic-gcc.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/atomic-gcc.h

## Purpose

This tools header supplies generic GCC-based atomic operations for architectures without a tools-specific atomic implementation.

## APIs, State, and Dependencies

It defines `ATOMIC_INIT`, `atomic_read`, `atomic_set`, `atomic_inc`, `atomic_dec_and_test`, `cmpxchg`, `atomic_cmpxchg`, `test_and_set_bit`, and `test_and_clear_bit`. The implementation uses `READ_ONCE`, GCC `__sync_*` builtins, and bit helpers `BIT_MASK` and `BIT_WORD`. It assumes `atomic_t` has a `counter` field supplied by included Linux types. No runtime state is stored in the header; operations mutate caller-provided atomic variables and bitmaps.

## Risks and Test Signals

Correctness depends on GCC builtin semantics and on matching the kernel-style `atomic_t` layout. `atomic_set` is a plain store rather than `WRITE_ONCE`, unlike `atomic_read`, so users needing strict compiler access semantics should check call sites. Tests are compile coverage on non-x86 tool builds and concurrency smoke tests for atomic counters and bit operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/atomic-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/barrier.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/barrier.h

## Purpose

This header provides generic fallback memory barrier definitions for tools builds when an architecture-specific barrier header is unavailable.

## APIs, State, and Dependencies

It includes `<linux/compiler.h>` and defines `mb()` as `barrier()` if missing, then maps `rmb()` and `wmb()` to `mb()` if they are not already defined. There is no runtime state and no executable control flow beyond macro expansion. It integrates through `<asm/barrier.h>`, which selects architecture-specific versions first.

## Risks and Test Signals

The fallback is only a compiler barrier, not necessarily a hardware barrier, so it is suitable for simple tools but may be insufficient for device or shared-memory protocols on weakly ordered architectures. Tests should compile affected tools on fallback architectures and audit any MMIO or shared-memory users for stronger ordering needs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops.h

## Purpose

This umbrella header collects generic bit-operation helpers for the tools include environment.

## APIs, State, and Dependencies

It includes generic `__ffs`, `ffz`, `fls`, `__fls`, `fls64`, `hweight`, atomic bitops, and non-atomic bitops. It deliberately errors if included directly without `<linux/bitops.h>`, preserving the intended include layering. It has no state or runtime behavior.

## Risks and Test Signals

The risk is include-order drift: direct inclusion breaks by design, and consumers must get types, masks, and compiler attributes from `<linux/bitops.h>`. Tests are compile-only coverage of tools using bit iteration, hweight, set/clear/test helpers, and architecture overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffs.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffs.h

## Purpose

This header defines the generic `__ffs` helper, which returns the zero-based index of the least significant set bit in an unsigned long.

## APIs, State, and Dependencies

`__ffs(unsigned long word)` uses staged tests and shifts, with an extra 32-bit step on 64-bit long builds. It depends on `__BITS_PER_LONG` and basic asm types. The function is undefined for zero input, matching kernel semantics. There is no persistent state.

## Risks and Test Signals

Callers must test for nonzero before calling. Word-size macros must match the compiler ABI or bit positions will be wrong. Tests should cover representative 32-bit and 64-bit inputs, single-bit positions, and compile-time integration through `find_*_bit` helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffz.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffz.h

## Purpose

This header defines `ffz(x)` as the first zero-bit counterpart to `__ffs`.

## APIs, State, and Dependencies

`ffz(x)` expands to `__ffs(~(x))`. It has no state and relies on `__ffs` already being available through the generic bitops include order. Like `__ffs`, it is undefined when no matching bit exists, so all-ones inputs must be checked by callers.

## Risks and Test Signals

Incorrect include order or all-ones inputs are the main hazards. Tests should exercise `find_first_zero_bit` and `find_next_zero_bit`, which are typical higher-level consumers that bound the search size before using `ffz`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__ffz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__fls.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__fls.h

## Purpose

This header provides `generic___fls`, the zero-based index of the most significant set bit in an unsigned long, and maps `__fls` to it unless an architecture override exists.

## APIs, State, and Dependencies

`generic___fls` starts from `BITS_PER_LONG - 1` and shifts left while testing high chunks. It depends on `BITS_PER_LONG`, asm types, `__always_inline`, and `__attribute_const__`. The function is undefined for zero input.

## Risks and Test Signals

The helper is sensitive to word size and undefined zero semantics. Tests should cover lowest, highest, and mixed set bits on 32-bit and 64-bit builds and ensure `fls64` uses the right path for `BITS_PER_LONG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/__fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/arch_hweight.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/arch_hweight.h

## Purpose

This header defines architecture hweight hooks for tools builds that do not provide optimized population-count operations.

## APIs, State, and Dependencies

`__arch_hweight8`, `__arch_hweight16`, `__arch_hweight32`, and `__arch_hweight64` forward to software implementations `__sw_hweight*`. It depends on asm integer types and on the software hweight functions being linked elsewhere. There is no state.

## Risks and Test Signals

Missing `__sw_hweight*` definitions cause link failures. Performance may be lower than architecture popcount, but correctness should match. Tests should compile and link bitmap users and compare hweight results against known bit counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/atomic.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/atomic.h

## Purpose

This header maps generic atomic bit set/clear names onto test-and-modify operations for tools builds.

## APIs, State, and Dependencies

It defines `set_bit` as `test_and_set_bit` and `clear_bit` as `test_and_clear_bit`. The actual atomic behavior comes from the included atomic implementation such as `atomic-gcc.h`. No state is stored in the header.

## Risks and Test Signals

The aliases discard the old-bit return value when used through `set_bit` or `clear_bit`, but the underlying functions still perform fetch-style atomics. Tests should compile users expecting kernel names and run simple concurrent bit set/clear operations where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/const_hweight.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/const_hweight.h

## Purpose

This header implements compile-time and runtime population-count macros for 8-, 16-, 32-, and 64-bit values.

## APIs, State, and Dependencies

`__const_hweight*` count set bits in constant expressions. `hweight*` choose constant versions with `__builtin_constant_p` or runtime `__arch_hweight*`. `HWEIGHT*` force constant arguments with `BUILD_BUG_ON_ZERO`. It depends on build-bug macros, `u64`, and arch hweight hooks. There is no runtime state.

## Risks and Test Signals

Macro arguments can be evaluated in compile-time contexts, so type width and constant-ness matter. Tests should compile constant and non-constant hweight users, intentionally reject nonconstant `HWEIGHT*` inputs, and compare runtime counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/const_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls.h

## Purpose

This header defines `generic_fls`, returning the one-based position of the most significant set bit in a 32-bit integer, with `fls(0) == 0`.

## APIs, State, and Dependencies

`generic_fls(unsigned int x)` uses a binary-search-like shift sequence over high bit ranges and maps `fls` to it unless an architecture override exists. It has no state and only relies on compiler inline attributes.

## Risks and Test Signals

The public zero behavior differs from `__fls`, which is undefined for zero; callers must pick the right helper. Tests should cover zero, one, high bit, and mixed values, plus code paths using `fls_long`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls64.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls64.h

## Purpose

This header defines `fls64`, the one-based most-significant-set-bit helper for 64-bit values.

## APIs, State, and Dependencies

On 32-bit long builds, `fls64` checks the high 32 bits first and falls back to `fls` on the low half. On 64-bit long builds, it returns `0` for zero or `__fls(x) + 1`. It errors for unsupported word sizes. There is no state.

## Risks and Test Signals

Correctness depends on `BITS_PER_LONG` matching target ABI and on `fls`/`__fls` semantics. Tests should cover zero, 32-bit boundary values, bit 63, and both 32-bit and 64-bit toolchain builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/fls64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/hweight.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/hweight.h

## Purpose

This header is a small umbrella that brings together architecture and constant hweight implementations.

## APIs, State, and Dependencies

It includes `arch_hweight.h` and `const_hweight.h`, thereby exposing `hweight8`, `hweight16`, `hweight32`, `hweight64`, and constant-only variants through the generic bitops stack. It has no state or direct logic.

## Risks and Test Signals

The header relies on include order and linked software hweight functions. Tests are compile/link coverage for bitmap and bitops consumers that call hweight helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/non-atomic.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/non-atomic.h

## Purpose

This header implements non-atomic bitmap mutation and test helpers for tools code.

## APIs, State, and Dependencies

Functions include `___set_bit`, `___clear_bit`, `___change_bit`, `___test_and_set_bit`, `___test_and_clear_bit`, `___test_and_change_bit`, and `_test_bit`. They compute `BIT_MASK` and `BIT_WORD`, cast the address to an unsigned long pointer, and update caller-owned memory directly. The header depends on `<linux/bits.h>` and has no own state.

## Risks and Test Signals

The functions are explicitly non-atomic and may be reordered, so racing callers need external locking. Volatile in the signature does not make compound operations atomic. Tests should cover bit positions across word boundaries, return values from test-and-modify helpers, and use through `<linux/bitops.h>` wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/non-atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitsperlong.h

## Purpose

This header reconciles userspace/compiler word-size information with UAPI `__BITS_PER_LONG` for tools builds.

## APIs, State, and Dependencies

It includes `<uapi/asm-generic/bitsperlong.h>`, defines `BITS_PER_LONG` from `__SIZEOF_LONG__` or `__WORDSIZE`, errors if it differs from `__BITS_PER_LONG`, defines `BITS_PER_LONG_LONG` as 64 if missing, and provides `small_const_nbits(nbits)` for optimized bitmap paths. There is no runtime state.

## Risks and Test Signals

Incorrect word-size macros break every bitmap and bitops helper. Tests should compile tools on 32-bit and 64-bit targets and verify `small_const_nbits` optimizations do not change results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/hugetlb_encode.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/hugetlb_encode.h

## Purpose

This header defines the generic huge-page size encoding used in syscall flag fields that request hugetlb pages.

## APIs, State, and Dependencies

It defines `HUGETLB_FLAG_ENCODE_SHIFT`, `HUGETLB_FLAG_ENCODE_MASK`, and constants for sizes from 16 KiB through 16 GiB, each encoding `log2(size)` into bits 26 through 31. It has no includes, state, or control flow.

## Risks and Test Signals

The constants are ABI-facing. Incorrect shifts or log2 values would make mmap or other hugetlb flag users request the wrong size. Tests are compile checks and comparisons against UAPI/kernel definitions for `MAP_HUGE_*` style flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/hugetlb_encode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/io.h -->
# sources/distributed-fs/ceph-client/tools/include/asm-generic/io.h

## Purpose

This header provides generic userspace tools implementations of kernel-style MMIO and repeated I/O accessors.

## APIs, State, and Dependencies

It defines ordering hooks such as `__io_br`, `__io_ar`, `__io_bw`, and `__io_aw`, no-op MMIO logging hooks, raw native-endian read/write helpers `__raw_read{b,w,l,q}` and `__raw_write{b,w,l,q}`, little-endian ordered accessors `read{b,w,l,q}` and `write{b,w,l,q}`, relaxed variants, and repeated accessors `reads{b,w,l,q}` and `writes{b,w,l,q}`. It depends on barrier, byteorder, compiler, kernel, and type headers. It mutates only the caller-provided MMIO addresses.

## Risks and Test Signals

The generic implementation dereferences volatile pointers directly and uses fallback barriers, so it may not be suitable for all architectures or devices. Endianness conversions are embedded in non-raw accessors. Tests should compile MMIO consumers on little- and big-endian targets where possible, audit for required ordering, and validate repeated accessors with fake mapped memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm-generic/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/alternative.h

## Purpose

This tools header stubs architecture alternative-instruction support enough for userspace tools assembly to build.

## APIs, State, and Dependencies

For s390x assembly it defines an `ALTERNATIVE` macro that emits the old instruction. For other architectures it defines `ALTERNATIVE` as `#`, effectively disabling alternative patching for tools builds. There is no runtime state.

## Risks and Test Signals

This intentionally does not implement kernel runtime patching semantics. It is only safe for tools code that needs assembly to assemble, such as perf benchmarks. Tests should assemble relevant architecture files and ensure no runtime path expects alternative replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/atomic.h

## Purpose

This header selects an architecture-specific atomic implementation for x86 tools builds or falls back to the generic GCC implementation.

## APIs, State, and Dependencies

On `__i386__` or `__x86_64__`, it includes `../../arch/x86/include/asm/atomic.h`; otherwise it includes `<asm-generic/atomic-gcc.h>`. It defines no APIs directly and has no state.

## Risks and Test Signals

The relative include path must remain valid in the tools source tree. Atomic semantics can differ between architecture and generic paths, so tests should compile atomic users on x86 and at least one fallback architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/barrier.h

## Purpose

This header selects the proper architecture barrier implementation for tools builds and supplies generic SMP acquire/release fallbacks.

## APIs, State, and Dependencies

It includes architecture-specific barrier headers for x86, arm, arm64, powerpc, riscv, s390, sh, sparc, tile, alpha, mips, ia64, and xtensa, otherwise generic barriers. It defines fallback `smp_rmb`, `smp_wmb`, `smp_mb`, `smp_store_release`, and `smp_load_acquire` using `READ_ONCE` and `WRITE_ONCE`. There is no runtime state.

## Risks and Test Signals

Wrong architecture detection or stale relative paths can change memory ordering for all tools users. The fallback acquire/release definitions are conservative but depend on `smp_mb`. Tests should compile on supported architectures and run lock-free helper tests that rely on acquire/release semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/bug.h

## Purpose

This header provides tools-friendly warning macros modeled after kernel `WARN*` helpers.

## APIs, State, and Dependencies

It defines `__WARN_printf` to print to `stderr`, plus `WARN`, `WARN_ON`, `WARN_ON_ONCE`, and `WARN_ONCE`. The once variants use a function-local static `__warned` flag for persistence. It depends on compiler `unlikely` and `<stdio.h>`.

## Risks and Test Signals

Warnings are side effects to standard error, not kernel logs, and once-state is per macro expansion. Tests should compile warning users and verify return values reflect whether the condition was true, including once behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/export.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/export.h

## Purpose

This header stubs kernel export macros for tools builds.

## APIs, State, and Dependencies

It defines `EXPORT_SYMBOL(x)` and `EXPORT_SYMBOL_GPL(x)` as empty macros. There is no state, dependency, or control flow.

## Risks and Test Signals

The header is intentionally a build-compatibility shim; it does not create symbol metadata. Tests are compile-only coverage of copied kernel code that contains export annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/io.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/io.h

## Purpose

This header selects the architecture MMIO accessor implementation for tools builds.

## APIs, State, and Dependencies

It includes the x86 tools `asm/io.h` on i386/x86_64 and generic MMIO accessors otherwise. It defines no direct functions and has no state.

## Risks and Test Signals

Relative architecture include paths and generic fallback semantics are the key risks. Tests should compile users on x86 and non-x86 configurations and verify any MMIO-dependent tool has the required ordering semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/rwonce.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/rwonce.h

## Purpose

This file is intentionally empty in this source snapshot. It reserves the tools include path for architecture-specific `rwonce` content while the active `READ_ONCE` and `WRITE_ONCE` definitions come from `linux/compiler.h`.

## APIs, State, and Dependencies

There are no macros, functions, includes, or state in the file.

## Risks and Test Signals

Consumers must not rely on this header to provide APIs directly. Tests are compile checks for code that includes `<asm/rwonce.h>` indirectly and gets actual access macros from the proper compiler headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/rwonce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/sections.h

## Purpose

This is a minimal placeholder for kernel-style section declarations in tools builds.

## APIs, State, and Dependencies

The header only defines an include guard. It declares no section symbols and has no state or dependencies.

## Risks and Test Signals

Copied kernel code that expects actual linker section symbols will need more than this stub. Tests are compile-only coverage of tools users that merely require the header to exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/tools/include/asm/timex.h

## Purpose

This header provides a minimal tools implementation of kernel timing cycle access.

## APIs, State, and Dependencies

It includes `<time.h>`, defines `cycles_t` as `clock_t`, and implements `get_cycles()` as `clock()`. It has no persistent state beyond libc clock state.

## Risks and Test Signals

`clock()` measures process CPU time, not hardware cycles, so this is a compatibility substitute rather than a precise cycle counter. Tests should compile timing users and avoid interpreting `get_cycles` values as real hardware cycle counts in tools that use this fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/generated/asm-offsets.h -->
# sources/distributed-fs/ceph-client/tools/include/generated/asm-offsets.h

## Purpose

This generated include placeholder is empty in the snapshot.

## APIs, State, and Dependencies

It defines no macros, offsets, types, or functions. There is no state and no dependencies.

## Risks and Test Signals

Any copied kernel code requiring real generated asm offsets will not be satisfied by this file. Compile tests should reveal such consumers; absence of failures means current tools code only needs the path to exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/generated/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/generated/asm/cpucap-defs.h -->
# sources/distributed-fs/ceph-client/tools/include/generated/asm/cpucap-defs.h

## Purpose

This generated architecture CPU capability definition header is empty in the snapshot.

## APIs, State, and Dependencies

It provides no macros or declarations. There is no runtime state.

## Risks and Test Signals

Architecture code that expects generated CPU capability constants would fail to compile or silently miss feature logic if it included this placeholder. Tests should build all tools paths that include generated asm headers and confirm no real constants are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/generated/asm/cpucap-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/generated/asm/sysreg-defs.h -->
# sources/distributed-fs/ceph-client/tools/include/generated/asm/sysreg-defs.h

## Purpose

This generated system-register definition header is empty in this tools snapshot.

## APIs, State, and Dependencies

It declares no system-register encodings, macros, or functions and has no state.

## Risks and Test Signals

Code that needs real generated sysreg constants cannot rely on this placeholder. Compile coverage of architecture tools consumers is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/generated/asm/sysreg-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/io_uring/mini_liburing.h -->
# sources/distributed-fs/ceph-client/tools/include/io_uring/mini_liburing.h

## Purpose

`mini_liburing.h` is a small header-only subset of liburing used by kernel tools and tests that need direct `io_uring` setup, submission, completion, and a few operation prep helpers without linking full liburing.

## Important APIs and Flow

The header defines `struct io_sq_ring`, `io_cq_ring`, `io_uring_sq`, `io_uring_cq`, and `io_uring`. `io_uring_setup` and `io_uring_enter` wrap syscalls. `io_uring_queue_init_params` sets up the ring fd and calls `io_uring_mmap`, which maps SQ ring, SQEs, and CQ ring. `io_uring_get_sqe` reserves an SQE in userspace. `io_uring_submit` publishes SQEs to the kernel SQ ring and enters the ring. `io_uring_wait_cqe` waits until a CQE is available, `io_uring_cqe_seen` advances the CQ head, and `io_uring_queue_exit` unmaps and closes. Prep helpers cover `IORING_OP_URING_CMD`, buffer registration, send, and zero-copy send.

## State, Dependencies, and Integration

Ring state is shared with the kernel through mmaped pages and tracked in the `io_uring` struct. The header depends on `<linux/io_uring.h>`, syscalls, mmap, barriers, and UAPI structs. It integrates with tools that need basic io_uring operations in a single include.

## Risks and Test Signals

The implementation is intentionally minimal. `io_uring_queue_exit` unmaps SQ state but does not unmap CQ in the visible code, which callers should audit. Barrier behavior differs by architecture. `IORING_SETUP_NO_SQARRAY` changes SQ size and submit behavior. Tests should create rings with and without `NO_SQARRAY`, submit simple operations, wait and mark CQEs seen, register buffers, and run under leak detection for mmap cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/io_uring/mini_liburing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/align.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/align.h

## Purpose

This header exposes kernel-style alignment macros to tools code.

## APIs, State, and Dependencies

It includes `<uapi/linux/const.h>` and defines `ALIGN`, `ALIGN_DOWN`, and `IS_ALIGNED`. These macros operate on caller-provided values and have no state.

## Risks and Test Signals

Alignment arguments are expected to be powers of two. Misuse with side-effect expressions can evaluate arguments more than once depending on nested macros. Tests should compile users and validate representative align-up, align-down, and aligned checks for integer and pointer-sized values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/align.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/args.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/args.h

## Purpose

This header provides small variadic macro utilities for counting arguments and concatenating tokens in tools builds.

## APIs, State, and Dependencies

`COUNT_ARGS` counts up to 15 variadic arguments, returning the 16th slot for larger lists. `__CONCAT` and `CONCATENATE` paste tokens while allowing macro expansion. There is no state or runtime behavior.

## Risks and Test Signals

Argument counting is macro-sensitive and bounded. Empty argument behavior depends on the `, ##X` extension. Tests should compile macro users with zero, one, many, and over-limit arguments under GCC and Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/arm-smccc.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/arm-smccc.h

## Purpose

This header provides ARM SMC Calling Convention constants and helpers for tools code that needs to encode or decode SMCCC function IDs.

## APIs, State, and Dependencies

It defines call type, 32/64-bit convention, owner, and function masks and shifts, plus helpers `ARM_SMCCC_IS_FAST_CALL`, `ARM_SMCCC_IS_64`, `ARM_SMCCC_FUNC_NUM`, `ARM_SMCCC_OWNER_NUM`, and `ARM_SMCCC_CALL_VAL`. It enumerates owner IDs, version IDs, architecture feature/workaround function IDs, KVM vendor hypervisor UID and function IDs, paravirtual time calls, TRNG calls, and return codes. It depends on `<linux/const.h>` and has no runtime state.

## Risks and Test Signals

These constants are ABI definitions. Wrong owner or function encodings can make hypercalls fail or call the wrong service. Tests should compare generated call values against ARM SMCCC specifications and kernel UAPI expectations, especially KVM PTP and workaround IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/arm-smccc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/atomic.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/atomic.h

## Purpose

This header adapts kernel-style atomic helper names for tools code.

## APIs, State, and Dependencies

It includes `<asm/atomic.h>`, declares `atomic_long_set`, maps relaxed/release cmpxchg names to `atomic_cmpxchg` when missing, and implements `atomic_try_cmpxchg` and `atomic_inc_unless_negative`. The latter loops reading the atomic value and compare-exchanging `c + 1` unless the current value is negative. State is caller-owned atomic variables.

## Risks and Test Signals

The header depends on the selected architecture atomic implementation and on a linked `atomic_long_set`. `atomic_inc_unless_negative` can spin under contention. Tests should compile and link atomic users and exercise cmpxchg success/failure and negative guard behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bitfield.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/bitfield.h

## Purpose

This header supplies kernel-style bitfield extraction, preparation, validation, and typed endian-aware field helpers for tools code.

## APIs, State, and Dependencies

Core macros include `FIELD_MAX`, `FIELD_FIT`, `FIELD_PREP`, and `FIELD_GET`, backed by `__bf_shf` and `__BF_FIELD_CHECK`. The checks enforce constant nonzero masks, field fit for constant values, register type width, and contiguous power-of-two mask layout. The header also declares compile-time error helpers and builds typed operations for little-endian, big-endian, and native u8/u16/u32/u64 fields. It depends on build-bug, kernel, and byteorder headers. It has no runtime state.

## Risks and Test Signals

The macros deliberately fail compilation for bad masks or oversized constant values; nonconstant misuse may become runtime truncation. Tests should include compile-fail coverage for invalid masks, runtime extraction/prep for several field positions, and endian typed helper checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bitmap.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/bitmap.h

## Purpose

This header provides kernel-style bitmap declarations, allocation helpers, and inline operations for tools code.

## APIs, State, and Dependencies

It defines `DECLARE_BITMAP`, first/last word masks, `bitmap_size`, `bitmap_zero`, `bitmap_fill`, `bitmap_copy`, `bitmap_empty`, `bitmap_full`, `bitmap_weight`, logical operations, allocation/free helpers, `bitmap_scnprintf`, `bitmap_set`, `bitmap_clear`, and `bitmap_xor`. Larger operations delegate to external `__bitmap_*` functions. Small constant bit counts use optimized single-word operations. It depends on bitsperlong, align, bitops, find, stdlib, string, and kernel helpers.

## Risks and Test Signals

The header mixes inline optimized paths and external implementations, so behavior must match for small and large bitmaps. Endianness controls memory comparison alignment. Tests should cover zero/fill/copy, set/clear ranges, logical ops, subset/intersection/equality, allocation sizes, and boundary bit counts around `BITS_PER_LONG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bitops.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/bitops.h

## Purpose

This is the main tools bit-operations header. It defines bit sizing macros, exposes hweight software hooks, wraps generic atomic and non-atomic bitops, and provides bit iteration helpers.

## APIs, State, and Dependencies

Macros include `BITS_PER_TYPE`, `BITS_TO_LONGS`, `BITS_TO_U64`, `BITS_TO_U32`, `BITS_TO_BYTES`, and `BYTES_TO_BITS`. It declares `__sw_hweight*`, maps public `__set_bit`, `__clear_bit`, `test_bit`, and related names to generic implementations, includes `asm-generic/bitops.h`, and defines `for_each_set_bit`, `for_each_clear_bit`, and `for_each_set_bit_from`. Inline helpers include `hweight_long`, `fls_long`, `rol32`, and `sign_extend64`.

## Risks and Test Signals

This header is a central include-order point for bitmap code. Missing external hweight/find implementations cause link failures. Tests should compile all tools bit users, exercise iteration over empty/full/sparse bitmaps, and validate sign extension and rotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bits.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/bits.h

## Purpose

This header exposes kernel-style bit and bitmask construction macros to tools code.

## APIs, State, and Dependencies

It includes vdso and UAPI bit definitions, defines `BIT_MASK`, `BIT_WORD`, `BIT_ULL_MASK`, `BIT_ULL_WORD`, `BITS_PER_BYTE`, and `BITS_PER_TYPE`, then provides typed `GENMASK_*` and `BIT_U*` macros with compile-time input checks in C contexts. It depends on build-bug, compiler, and overflow helpers. There is no state.

## Risks and Test Signals

The macros are ABI- and type-width-sensitive. Bad high/low ordering or out-of-range bit indexes intentionally trigger build errors where possible. Tests should cover typed masks for u8/u16/u32/u64/u128 and assembly inclusion paths where checks are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/btf_ids.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/btf_ids.h

## Purpose

This header defines structures and macros for representing BTF ID sets in kernel-derived tools code.

## APIs, State, and Dependencies

It defines `struct btf_id_set` and `struct btf_id_set8`. When `CONFIG_DEBUG_INFO_BTF` is enabled, macros such as `BTF_ID`, `BTF_ID_LIST`, `BTF_SET_START`, and `BTF_SET_END` emit zero-filled records into the `.BTF_ids` section for later resolution by `resolve_btfids`. When disabled, the macros become static placeholder objects or no-ops. It also enumerates socket and tracing BTF type categories and declares related ID arrays.

## Risks and Test Signals

The assembly layout must match `resolve_btfids` expectations. Disabled-BTF fallbacks must still satisfy references without section data. Tests should build with and without `CONFIG_DEBUG_INFO_BTF`, inspect `.BTF_ids` layout, and run the resolver on users that define BTF sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/btf_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bug.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/bug.h

## Purpose

This minimal header provides a `BUILD_BUG_ON_ZERO` expression helper for tools/perf-style code.

## APIs, State, and Dependencies

`BUILD_BUG_ON_ZERO(e)` uses a negative-width bitfield in `sizeof` to force a compilation error when `e` is true while evaluating to zero otherwise. It has no state or dependencies.

## Risks and Test Signals

The macro is compile-time only and may conflict semantically with the richer `linux/build_bug.h` variant. Tests should compile users that place it in constant-expression contexts and verify true conditions fail compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/build_bug.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/build_bug.h

## Purpose

This header implements kernel-style compile-time assertion and build-bug helpers for tools builds.

## APIs, State, and Dependencies

It defines `BUILD_BUG_ON_ZERO`, `BUILD_BUG_ON_NOT_POWER_OF_2`, `BUILD_BUG_ON_INVALID`, `BUILD_BUG_ON_MSG`, `BUILD_BUG_ON`, `BUILD_BUG`, optional-message `static_assert`, and `ASSERT_STRUCT_OFFSET`. It depends on compiler assertion support from `<linux/compiler.h>` and uses `offsetof` where the offset assertion macro is used. There is no runtime state.

## Risks and Test Signals

These macros are intentionally compile-breaking; portability depends on compiler support for `_Static_assert` and attributes. Tests should include compile-pass and compile-fail cases for power-of-two, struct offsets, and constant-expression assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/build_bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/cache.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/cache.h

## Purpose

This header supplies minimal cache-line size constants for tools builds.

## APIs, State, and Dependencies

It defines `L1_CACHE_SHIFT` as 5, `L1_CACHE_BYTES` as 32, and `SMP_CACHE_BYTES` as `L1_CACHE_BYTES`. There is no state or dependency.

## Risks and Test Signals

The fixed 32-byte value is a portability approximation and may not match host hardware. Tests are compile-only unless a tool uses these constants for layout or padding, in which case architecture expectations should be reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/cfi_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/cfi_types.h

## Purpose

This header provides Clang CFI/KCFI type annotation macros for kernel-derived assembly and C code in tools builds.

## APIs, State, and Dependencies

For assembly with `CONFIG_CFI`, it defines `__CFI_TYPE`, `SYM_TYPED_ENTRY`, `SYM_TYPED_START`, and `SYM_TYPED_FUNC_START` to emit type identifiers before symbols. Without CFI, typed starts map to normal symbol starts. For C with `CONFIG_CFI`, `DEFINE_CFI_TYPE` emits a read-only type-id object referencing `__kcfi_typeid_<func>`. There is no normal runtime state, but emitted objects and assembly labels affect binary metadata.

## Risks and Test Signals

The macros rely on compiler-emitted KCFI symbols and correct assembly syntax. Incorrect use can break indirect-call checking or symbol layout. Tests should build assembly and C users with and without `CONFIG_CFI` and inspect object symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/cfi_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler-context-analysis.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/compiler-context-analysis.h

## Purpose

This header stubs kernel compiler context-analysis annotations for tools builds.

## APIs, State, and Dependencies

It defines guard, lock-context, acquire/release, must-hold, and unsafe-context annotations as no-ops or simple expression wrappers. There is no runtime state, dependency, or checking in tools.

## Risks and Test Signals

The annotations do not enforce locking or context rules in userspace tools. Copied code that relies on sparse or compiler analysis for safety will compile without those checks. Tests are compile-only; code review must cover actual locking rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler-context-analysis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler-gcc.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/compiler-gcc.h

## Purpose

This header supplies GCC-specific compiler attributes and helpers for the tools compiler abstraction layer.

## APIs, State, and Dependencies

It is guarded so it must be included through `<linux/compiler.h>`. It defines `GCC_VERSION`, `fallthrough`, `__compiletime_error`, `__must_be_array`, `__pure`, `noinline`, `__packed`, `__noreturn`, `__aligned`, `__printf`, and `__scanf` as supported by the compiler. There is no state.

## Risks and Test Signals

Compiler feature detection must work for GCC and Clang-compatible frontends. Direct inclusion intentionally errors. Tests should compile attribute users with GCC and Clang and verify direct include failure is preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/compiler.h

## Purpose

This is the main tools compiler abstraction header. It provides compile-time assertions, barriers, attributes, access annotations, branch prediction, type helpers, and `READ_ONCE`/`WRITE_ONCE`.

## APIs, State, and Dependencies

It includes `compiler_types.h`, defines `compiletime_assert`, `barrier`, inline and attribute fallbacks, `__same_type`, constexpr helpers, annotation stubs such as `__user`, `__rcu`, `__iomem`, `likely`, `unlikely`, may-alias integer typedefs, and size-specialized `__read_once_size`/`__write_once_size`. Public `READ_ONCE` and `WRITE_ONCE` use alias-safe volatile loads/stores for 1, 2, 4, and 8 bytes and memcpy with barriers for larger objects. It also defines token-paste helpers and build-bug machinery.

## Risks and Test Signals

This header affects almost every copied kernel helper. Incorrect `READ_ONCE`/`WRITE_ONCE` semantics can break lock-free code, while attribute fallbacks can hide missing compiler support. Tests should compile a broad tools set under GCC and Clang, exercise once-access macros for scalar and aggregate types, and validate compile-time assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/compiler_types.h

## Purpose

This header centralizes compiler type support used by the tools compiler abstraction.

## APIs, State, and Dependencies

It defines fallback `__has_builtin`, includes context-analysis stubs, includes GCC-specific definitions when `__GNUC__` is set, defines `asm_goto_output`, and provides `__unqual_scalar_typeof` using C11 `_Generic` to strip scalar qualifiers while leaving nonscalars unchanged. There is no runtime state.

## Risks and Test Signals

The `_Generic` type logic depends on compiler C dialect support. Tests should compile with GCC and Clang, including users of `__unqual_scalar_typeof` on signed, unsigned, char, and nonscalar expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/compiler_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/const.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/const.h

## Purpose

This header forwards kernel-style constant construction macros to the vdso constant header.

## APIs, State, and Dependencies

It includes `<vdso/const.h>` and defines no additional macros. There is no state or control flow.

## Risks and Test Signals

The include path must provide vdso constants such as `_AC`. Tests are compile-only coverage for headers like `arm-smccc.h` that depend on those macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/container_of.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/container_of.h

## Purpose

This header provides the kernel-style `container_of` macro for tools code.

## APIs, State, and Dependencies

If not already defined, `container_of(ptr, type, member)` captures the member pointer type and subtracts `offsetof(type, member)` from it to recover the containing structure pointer. There is no state.

## Risks and Test Signals

The macro requires a valid pointer to the named member and an included declaration of `offsetof`. Misuse with wrong types can produce invalid pointers despite the type check. Tests should compile representative intrusive-list or embedded-struct users and run pointer round-trip checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/container_of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/coresight-pmu.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/coresight-pmu.h

## Purpose

This header defines CoreSight ETM PMU names and AUX hardware ID encoding helpers used by perf and related tools.

## APIs, State, and Dependencies

It defines `CORESIGHT_ETM_PMU_NAME`, the legacy CPU-to-trace-ID formula, masks for `PERF_RECORD_AUX_OUTPUT_HW_ID` fields, and helpers to extract trace ID, sink ID, minor version, and major version from packed hardware IDs. It depends on `<linux/bits.h>` and has no state.

## Risks and Test Signals

The field layout is part of the perf/CoreSight userspace contract. Incorrect masks break trace decoding and CPU/sink association. Tests should decode known AUX hardware IDs, including legacy and versioned values, and compare against perf output on CoreSight systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/coresight-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/ctype.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/ctype.h

## Purpose

This header provides kernel-style character classification and case conversion helpers for tools code.

## APIs, State, and Dependencies

It defines classification bit masks, declares external `_ctype[]`, and maps `isalnum`, `isalpha`, `iscntrl`, `isgraph`, `islower`, `isprint`, `ispunct`, `isspace`, `isupper`, `isxdigit`, `isascii`, `toascii`, `isdigit`, `tolower`, `toupper`, `_tolower`, and `isodigit`. `isdigit` uses a compiler builtin when available. State is limited to the external classification table.

## Risks and Test Signals

The macros index `_ctype` by unsigned char cast, which avoids negative-char indexing. Locale is not considered; behavior is kernel ASCII-style. Tests should link `_ctype`, cover all ASCII classes, and check case conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/ctype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/debugfs.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/debugfs.h

## Purpose

This is an empty compatibility header for copied kernel code that includes `<linux/debugfs.h>` in tools builds.

## APIs, State, and Dependencies

It defines only an include guard. There are no functions, macros, or state.

## Risks and Test Signals

Code requiring actual debugfs APIs cannot use this stub. Compile tests should identify any consumer that needs more than header presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/delay.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/delay.h

## Purpose

This is a placeholder for kernel delay helpers in tools builds.

## APIs, State, and Dependencies

The file only contains an include guard and provides no delay functions or macros.

## Risks and Test Signals

Copied code that calls `udelay`, `mdelay`, or related helpers will not be satisfied by this header. Compile coverage is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/err.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/err.h

## Purpose

This header implements kernel-style encoded error-pointer helpers for userspace tools.

## APIs, State, and Dependencies

It defines `MAX_ERRNO`, `IS_ERR_VALUE`, `ERR_PTR`, `PTR_ERR`, `IS_ERR`, `IS_ERR_OR_NULL`, `PTR_ERR_OR_ZERO`, and `ERR_CAST`. It depends on compiler and type annotations plus asm errno values. It stores no state; it interprets pointer values in the high unused address range as negative errno values.

## Risks and Test Signals

The scheme assumes architectures have an unused pointer range analogous to the kernel/user address hole. Misusing real pointers near the error range would be misclassified. Tests should cover all helper conversions for common negative errno values and null/non-null pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/export.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/export.h

## Purpose

This header stubs Linux symbol export annotations for tools code.

## APIs, State, and Dependencies

It defines `EXPORT_SYMBOL(sym)` and `EXPORT_SYMBOL_GPL(sym)` as empty macros. There is no state or dependency.

## Risks and Test Signals

The macros do not emit module export metadata. They only allow copied kernel code to compile in userspace tools. Tests are compile-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/filter.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/filter.h

## Purpose

This header provides Linux socket filter and eBPF instruction construction macros for tools code.

## APIs, State, and Dependencies

It includes `<linux/bpf.h>`, maps argument/context/frame-pointer registers, defines `MAX_BPF_STACK`, and provides initializer macros for ALU, move, endian, load, store, atomic, jump, call, immediate, map-fd, map-value, relative-call, and exit BPF instructions. Each macro expands to one or more `struct bpf_insn` initializers. There is no runtime state.

## Risks and Test Signals

Instruction encoding macros are ABI-sensitive; wrong opcodes, register fields, offsets, or immediate splitting can produce verifier rejection or wrong BPF behavior. Tests should assemble known instruction sequences, compare encodings to expected bytes/fields, and load simple programs through the BPF verifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/find.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/find.h

## Purpose

This header exposes bitmap bit-search helpers for tools code, with small-constant inline fast paths and external generic implementations for larger bitmaps.

## APIs, State, and Dependencies

It can only be included through `<linux/bitmap.h>`. It declares `_find_next_bit`, `_find_next_and_bit`, `_find_next_zero_bit`, `_find_first_bit`, `_find_first_and_bit`, and `_find_first_zero_bit`. Inline public helpers check `small_const_nbits` and use `GENMASK`, `__ffs`, and `ffz` for one-word cases, otherwise delegate to external functions. There is no state.

## Risks and Test Signals

The header relies on proper bounds handling before calling undefined helpers like `__ffs` or `ffz`. Include layering is enforced with an error. Tests should cover empty, full, sparse, offset-at-size, and one-word versus multiword bitmap searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/find.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/ftrace.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/ftrace.h

## Purpose

This is an empty compatibility header for kernel code that includes ftrace interfaces while being built in the tools environment.

## APIs, State, and Dependencies

Only an include guard is present. There are no tracing APIs or state.

## Risks and Test Signals

Code that actually needs ftrace instrumentation declarations will need a fuller shim. Compile tests validate that current tools users only require the header path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/gfp.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/gfp.h

## Purpose

This header provides minimal GFP flag helpers for tools code that shares kernel allocation-style APIs.

## APIs, State, and Dependencies

It includes Linux types and `gfp_types.h`, defines `default_gfp` helper macros to supply `GFP_KERNEL` when no flag is passed, and implements `gfpflags_allow_blocking(gfp_t)` by testing `__GFP_DIRECT_RECLAIM`. It has no state.

## Risks and Test Signals

The helper reflects kernel GFP semantics only at a shallow flag level; userspace allocation behavior is not controlled by GFP flags. Tests should compile allocation wrappers and verify blocking classification for `GFP_KERNEL`, atomic/no-reclaim-style flags, and explicit default macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/gfp.h -->

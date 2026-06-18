# Group Research: group_380_freebsd_src_sources_os_bsd_freebsd_src_sbin_nvmecontrol_modules_wdc__c399603218da

Scope verified against `Docs/research_subset_a.md`: all listed files are under `sources/os/bsd/freebsd-src`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/wdc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/wdc.c

Purpose: Implements the dynamically registered `nvmecontrol wdc` vendor command group and WDC/HGST-specific log page decoders.

Key behavior:
- Registers top-level `wdc` and subcommand `cap-diag`.
- Supports WDC vendor IDs `0x1c58`, `0x1b96`, and `0x15b7`.
- Retrieves older WDC cap-diag data via vendor opcode `0xe6`.
- Retrieves SanDisk/WDC DUI/cap-diag data via opcode `0xfa`.
- Appends the controller serial number and a suffix to the user-provided output path template before writing binary dumps.
- Uses `NVME_PASSTHROUGH_CMD` and `NVME_GET_MAX_XFER_SIZE` to chunk vendor log reads.
- Registers both `hgst` and `wdc` handlers for `HGST_INFO_LOG`.

Important internals:
- `wdc_get_data()` and `wdc_get_data_dui()` differ in opcode layout and offset dword placement.
- `wdc_get_dui_log_size()` decodes DUI header versions 0 through 3 and can limit collection by data area.
- `wdc_do_dump_e6()` detects the `E6LG` header and adjusts offset handling.
- HGST log decoding dispatches subpages for read/write/verify errors, self-test, background scan, erase errors/counts, temperature history, SSD performance, and firmware load data.

Dependencies:
- `nvmecontrol.h` helpers: `read_controller_data()`, `kv_lookup()`, `NVME_LOGPAGE`.
- FreeBSD NVMe ioctl ABI: `struct nvme_pt_command`, `NVME_PASSTHROUGH_CMD`, `NVME_GET_MAX_XFER_SIZE`.
- Endian helpers from `<sys/endian.h>`.

Research notes:
- This file is both a command module and a log-page plugin.
- Error handling is fail-fast via `err()`/`errx()`.
- Dump output overwrite protection is explicitly marked as missing by an `XXX` comment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/wdc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nc_util.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nc_util.c

Purpose: Provides small utility routines shared by `nvmecontrol`.

Key behavior:
- `uint128_to_str()` converts an unsigned 128-bit value to decimal text in a caller-supplied buffer.
- `le48dec()` decodes a 48-bit little-endian integer from a byte buffer.

Dependencies:
- `nvmecontrol.h` for `uint128_t`.
- `<sys/endian.h>` for `le16dec()` and `le32dec()`.

Research notes:
- `uint128_to_str()` returns `NULL` if the buffer is too small.
- `le48dec()` fills a helper gap not directly covered by the standard endian helpers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nc_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/ns.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/ns.c

Purpose: Implements `nvmecontrol ns` namespace-management commands.

Key behavior:
- Registers `ns` with subcommands: `active`, `allocated`, `controllers`, `create`, `delete`, `attach`, `detach`, `attached`, and `identify`.
- Converts namespace device paths back to controller paths when controller-level admin commands are needed.
- Checks `NVME_CTRLR_DATA_OACS_NSMGMT` before namespace-management operations.
- Uses `NVME_OPC_IDENTIFY` CNS selectors to list active namespaces, allocated namespaces, subsystem controllers, attached controllers, and allocated namespace identify data.
- Uses `NVME_OPC_NAMESPACE_MANAGEMENT` for create/delete.
- Uses `NVME_OPC_NAMESPACE_ATTACHMENT` for attach/detach.
- Maps namespace-management completion status codes to human-readable messages.

Important internals:
- `nscreate()` builds `struct nvme_namespace_data`, defaults capacity to namespace size, defaults namespace sharing from controller multipath capability, and swaps the structure to little endian before submission.
- `nsdelete()` accepts either an explicit namespace ID or a namespace device context.
- `nsattach()` can attach a namespace to all subsystem controllers or a specific/default controller.
- `nsdetach()` can detach from all currently attached controllers or a specific/default controller.
- `nsidentify()` can print parsed namespace data or hex output, trimming trailing zeroes unless verbose.

Dependencies:
- `nvmecontrol.h` command registration and device helpers.
- FreeBSD NVMe passthrough ioctl and NVMe identify/namespace structures.

Research notes:
- Mutating operations open the controller for write.
- Commands invoked on controller devices often require explicit `--namespace-id`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/ns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nsid.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nsid.c

Purpose: Implements `nvmecontrol nsid`, a small helper command for resolving a namespace device to its controller and namespace ID.

Key behavior:
- Opens the provided namespace/controller device.
- Calls `get_nsid()` to fetch the backing controller device name and NSID.
- Prints controller path and namespace ID separated by a tab.

Dependencies:
- `open_dev()` and `get_nsid()` from the shared nvmecontrol helper layer.
- Command parser definitions from `comnd.h`.

Research notes:
- The command expects one positional device argument named `namespace-id`.
- It frees the controller path allocated by `get_nsid()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nsid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.c

Purpose: Provides the `nvmecontrol` program entry point and core shared helpers.

Key behavior:
- Formats hex output as dwords or bytes.
- Implements identify helpers for controller data, namespace data, and active namespace lists.
- Opens device paths, accepting either absolute paths or names under `/dev`.
- Resolves namespace devices with `NVME_GET_NSID`.
- Loads command modules from `/lib/nvmecontrol` and `${LOCALBASE}/lib/nvmecontrol`.
- Initializes and dispatches the command framework in `main()`.

Important internals:
- Identify helpers submit `NVME_OPC_IDENTIFY` through `NVME_PASSTHROUGH_CMD`.
- Returned identify structures are byte-swapped to host endian before use.
- `get_nsid()` optionally returns both controller path and namespace ID.

Dependencies:
- FreeBSD NVMe ioctl ABI.
- `libutil` for `getlocalbase()`.
- The local command framework from `nvmecontrol.h`/`comnd.h`.

Research notes:
- Dynamic module loading is part of normal startup.
- `open_dev()` can either return an error code or terminate, depending on `exit_on_error`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.h

Purpose: Central header for `nvmecontrol` command and log-page integration.

Key behavior:
- Defines `print_fn_t` and `struct logpage_function`.
- Provides the `NVME_LOGPAGE()` constructor macro for registering log page decoders.
- Declares shared device, identify, print, log-page, and utility functions.
- Defines `NVME_CTRLR_PREFIX`, `NVME_NS_PREFIX`, and `DEFAULT_SIZE`.
- Defines `struct kv_name` and `kv_lookup()` interface for key/value display tables.
- Provides a generic `letoh()` macro for little-endian scalar conversion.

Important internals:
- Defines portable `uint128_t` support using C23 `_BitInt(128)`, compiler `__uint128_t`, or fallback `uint64_t`.
- `to128()` decodes a 128-bit little-endian value from memory when the compiler supports it.

Dependencies:
- Kernel/user NVMe definitions from `<dev/nvme/nvme.h>`.
- Local command parser header `comnd.h`.

Research notes:
- This header is the coupling point between built-in commands and dynamically registered log-page handlers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol_ext.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol_ext.h

Purpose: Minimal external interface header for controller data printing.

Key behavior:
- Declares `nvme_print_controller(struct nvme_controller_data *cdata)`.

Dependencies:
- Consumers must already have the NVMe controller data type visible.

Research notes:
- The file contains only license text and this one function prototype.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol_ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/passthru.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/passthru.c

Purpose: Implements generic NVMe passthrough commands: `admin-passthru` and `io-passthru`.

Key behavior:
- Accepts opcode, flags, dwords 2/3/10-15, data length, metadata length, timeout, prefill value, input file, read/write mode, binary output, dry-run, and show-command flags.
- Opens the selected controller or namespace device for read/write.
- Allocates page-aligned data buffers for command payloads.
- Reads write payload data from an input file or stdin.
- Submits `NVME_PASSTHROUGH_CMD`.
- Prints completion DWORD0 and hex output for reads, or writes raw binary data when requested.

Important internals:
- Option names intentionally mirror `nvme-cli` for easier command translation.
- Requires exactly one of read/write when data transfer is requested.
- Metadata is rejected because FreeBSD kernel support is marked unavailable.

Dependencies:
- `nvmecontrol.h` for `open_dev()` and `print_hex()`.
- FreeBSD NVMe passthrough ioctl.

Research notes:
- `timeout` is parsed and displayed but not passed into the current passthrough structure.
- The namespace ID option is accepted, but the comment notes FreeBSD kernel behavior overrides it.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/passthru.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/perftest.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/perftest.c

Purpose: Implements `nvmecontrol perftest`, a low-level NVMe I/O performance test wrapper.

Key behavior:
- Accepts thread count, request size, duration, operation type, interrupt/test mode, per-thread reporting, and optional flags.
- Supports read and write test opcodes.
- Selects `NVME_IO_TEST` or `NVME_BIO_TEST` based on interrupt mode.
- Supports `refthread` test flag.
- Prints aggregate IOPS and MB/s, optionally with per-thread IOPS.

Dependencies:
- FreeBSD NVMe test ioctls: `NVME_IO_TEST`, `NVME_BIO_TEST`.
- `struct nvme_io_test` from NVMe headers.
- Shared `open_dev()` helper.

Research notes:
- Thread count is constrained to 1 through 128.
- This is a driver-test interface rather than a filesystem-level benchmark.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/perftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/power.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/power.c

Purpose: Implements `nvmecontrol power` for listing, querying, and setting NVMe power states.

Key behavior:
- Lists supported power states from controller identify data.
- Queries current power state and workload hint via `NVME_OPC_GET_FEATURES`.
- Sets power state and workload hint via `NVME_OPC_SET_FEATURES`.
- Converts namespace devices back to controller devices before controller-level operations.

Important internals:
- Uses a static assertion to verify `struct nvme_power_state` size.
- `power_list_one()` decodes max, idle, and active power scaling fields and latency fields for display.
- Rejects simultaneous list and set operations.

Dependencies:
- `read_controller_data()`, `open_dev()`, and `get_nsid()`.
- NVMe feature opcodes and power-management feature constants.

Research notes:
- `power_set()` has a `perm` parameter for persistent setting but the command path passes `0`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/power.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reconnect.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reconnect.c

Purpose: Implements `nvmecontrol reconnect` for reconnecting to NVMe-oF controllers.

Key behavior:
- Fetches reconnect parameters from the kernel using `nvmf_reconnect_params()`.
- Validates required nvlist fields including discovery log entry, host NQN, queue counts, queue size, and flow-control settings.
- Reconnects using either stored parameters or an explicit replacement address.
- Supports TCP transport options including header digests, data digests, SQ flow control, keep-alive timeout, reconnect delay, controller loss timeout, queue count, and queue size.
- Creates admin and I/O queues in userspace, then hands them back to the kernel with `nvmf_reconnect_host()`.

Important internals:
- `reconnect_nvm_controller()` centralizes queue connection and kernel handoff.
- `reconnect_by_address()` parses an explicit address and requires an explicit port.
- `reconnect_by_params()` reconstructs transport/address details from persisted discovery log entry data.
- `fetch_and_validate_rparams()` rejects missing or malformed reconnect metadata before attempting reconnection.

Dependencies:
- `libnvmf`, `<sys/nv.h>`, `<sys/dnv.h>`.
- Fabric helper declarations from `fabrics.h`.
- NVMe discovery log entry structures.

Research notes:
- Only TCP is accepted in current command-line handling.
- In `reconnect_by_params()`, the call to `tcp_association_params()` appears after an earlier `break` in the TCP case, making that block unreachable as written.
- The function allocates a terminated `subnqn` copy but passes `dle->subnqn` into `reconnect_nvm_controller()` in one path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reconnect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reset.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reset.c

Purpose: Implements `nvmecontrol reset` for controller-level reset.

Key behavior:
- Opens a controller or namespace device for write.
- Resolves namespace devices back to their controller device.
- Issues `NVME_RESET_CONTROLLER`.

Dependencies:
- Shared `open_dev()` and `get_nsid()` helpers.
- FreeBSD NVMe reset ioctl.

Research notes:
- This is intentionally controller-scoped even when invoked with a namespace device.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/resv.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/resv.c

Purpose: Implements `nvmecontrol resv` reservation-management commands.

Key behavior:
- Registers `resv` with subcommands `acquire`, `register`, `release`, and `report`.
- Requires namespace devices for all reservation commands.
- Uses `NVME_OPC_RESERVATION_ACQUIRE`, `NVME_OPC_RESERVATION_REGISTER`, `NVME_OPC_RESERVATION_RELEASE`, and `NVME_OPC_RESERVATION_REPORT`.
- Builds little-endian reservation payloads for current key, preempt key, new key, reservation type, action fields, ignore-existing-key, and persist-through-power-loss settings.
- Reports normal or extended reservation status.
- Supports hex output and verbose hex trimming control.

Important internals:
- `resvreport()` uses a 4096-byte aligned buffer and swaps either normal or extended reservation status structures before printing.
- Registered controller count is decoded from the two-byte `regctl` field.
- Printed report includes generation, reservation type, registered controller count, PTPL state, controller IDs, reservation status, host IDs, and reservation keys.

Dependencies:
- FreeBSD NVMe reservation opcodes and status structures.
- Shared `open_dev()`, `get_nsid()`, and `print_hex()` helpers.

Research notes:
- The command exits through `arg_help()` if invoked against a controller rather than a namespace.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/resv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/sanitize.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/sanitize.c

Purpose: Implements `nvmecontrol sanitize` for NVMe sanitize operations and status reporting.

Key behavior:
- Supports sanitize actions: `exitfailure`, `block`, `overwrite`, `crypto`, and numeric action compatibility.
- Supports options for unrestricted sanitize exit, no deallocate after sanitize, overwrite invert pattern, overwrite pass count, overwrite pattern, and report-only mode.
- Resolves namespace devices back to controllers for subsystem-level sanitize.
- Checks controller sanitize capabilities before issuing block erase, overwrite, or crypto erase.
- Polls the sanitize status log page until completion or failure.

Important internals:
- Builds sanitize command bits in CDW10 and overwrite pattern in CDW11.
- Disallows sanitizing a single namespace when the controller reports multiple namespaces.
- Progress display uses `sprog` scaled against 65536 with increasing sleep delay up to 16 seconds.

Dependencies:
- `read_controller_data()`, `read_logpage()`, `open_dev()`, and `get_nsid()`.
- NVMe sanitize opcode, sanitize capability fields, and sanitize status log page definitions.

Research notes:
- `--reportonly` skips issuing a new sanitize command and only reads status.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/sanitize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/selftest.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/selftest.c

Purpose: Implements `nvmecontrol selftest` for starting NVMe device self-tests.

Key behavior:
- Requires a self-test code via `--test-code`.
- Accepts controller or namespace device input.
- Resolves namespace devices to controller paths while preserving NSID.
- Checks controller self-test support via `NVME_CTRLR_DATA_OACS_SELFTEST`.
- Issues `NVME_OPC_DEVICE_SELF_TEST`.
- Reports the command-specific “self-test in progress” status distinctly.

Dependencies:
- Shared `open_dev()`, `get_nsid()`, and `read_controller_data()` helpers.
- NVMe self-test opcode and status helpers.

Research notes:
- Self-test code is limited to values up to `0x0f`; missing code is a usage error.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/selftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/telemetry.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/telemetry.c

Purpose: Implements `nvmecontrol telemetry-log` for extracting host-initiated NVMe telemetry logs.

Key behavior:
- Requires an output file.
- Allows selecting data area 1 through 3, defaulting to 3.
- Rejects namespace-scoped operation; telemetry is treated as controller/global only.
- Checks telemetry support in controller identify LPA.
- Reads the telemetry header, derives the requested data-area end block, then streams the log to the output file in 4096-byte chunks.
- Supports verbose progress output.

Important internals:
- Uses `NVME_LOG_TELEMETRY_HOST_INITIATED` with retain asynchronous event behavior set in `read_logpage()` calls.
- Converts `da1_last`, `da2_last`, or `da3_last` using `letoh()`.
- Computes total byte count as `(last_block + 1) * 512`.

Dependencies:
- `read_controller_data()`, `read_logpage()`, `open_dev()`, and `get_nsid()`.
- NVMe telemetry log page structures and controller LPA telemetry bit.

Research notes:
- Output file is opened with create/write flags but without truncation, so shorter later captures may leave prior trailing data.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/telemetry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/Makefile

Purpose: FreeBSD test makefile for nvmecontrol ATF tests.

Key behavior:
- Sets `PACKAGE=tests`.
- Registers `basic` as a shell ATF test.
- Includes `<bsd.test.mk>`.

Dependencies:
- FreeBSD bsd.test.mk infrastructure.
- `basic.sh` in the same test directory.

Research notes:
- The file is only four lines and contains no custom test logic.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/basic.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/basic.sh

Purpose: Provides ATF shell sanity tests for `nvmecontrol`.

Key behavior:
- Selects the first `/dev/nvme[0-9]*` controller or falls back to `nvme0`.
- Defines an invalid option probe `-z` and expected parser error text.
- Tests dynamic library load failure handling from `/lib/nvmecontrol` and `/usr/local/lib/nvmecontrol` by creating fake `.so` files.
- Exercises `admin-passthru`, `devlist`, `identify`, `io-passthru`, `logpage`, `nsid`, `power`, and `reset`.
- Adapts expectations based on whether the selected NVMe character device exists.
- Skips actual reset of an active device unless `DANGEROUS=true`.

Dependencies:
- FreeBSD ATF shell framework.
- Root privileges for all test cases.
- Installed `nvmecontrol` binary and optional NVMe device node.

Research notes:
- The suite is explicitly a basic sanity check, not full functional coverage.
- Cleanup hooks remove fake dynamic libraries created during load-failure tests.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/basic.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/Makefile

Purpose: FreeBSD build makefile for the `pfctl` packet filter control utility.

Key behavior:
- Builds program `pfctl` in package `pf`.
- Installs configuration `pf.os` and manual page `pfctl.8`.
- Lists source files including parser, state printing, ALTQ, OS fingerprinting, radix, table, queue stats, optimizer, and ruleset code.
- Sets warning level and CFLAGS for prototypes, ALTQ, and include paths.
- Adds `WITH_INET6` and `WITH_INET` defines based on source build options.
- Links libraries `m`, `md`, and `pfctl`.
- Enables tests through `HAS_TESTS` and `SUBDIR.${MK_TESTS}+= tests`.

Dependencies:
- FreeBSD build system: `<src.opts.mk>` and `<bsd.prog.mk>`.
- `libpfctl` headers and object directory.
- Build options `MK_INET6_SUPPORT`, `MK_INET_SUPPORT`, and `MK_TESTS`.

Research notes:
- This file is outside nvmecontrol but still under the same FreeBSD source tree and subset A scope.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/Makefile -->
# subset-b-006898 research

This grouped report covers the USB test/usbip utilities and runtime-verification tooling listed for subset-b-006898. Each source file has its own marker-bounded section and title preserving the source path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-test.c -->
# sources/distributed-fs/ceph-client/tools/usb/ffs-test.c

Purpose: `ffs-test.c` is a userspace FunctionFS source/sink gadget exerciser. It writes FunctionFS descriptors and strings to `ep0`, then runs endpoint threads that generate IN traffic on `ep1`, consume OUT traffic on `ep2`, and print control-plane events from `ep0`. The file exists to validate user-mode FunctionFS setup and endpoint data paths for a two-endpoint vendor-specific interface.

Important APIs, types, and functions: the packed `descriptors` object builds v2 FS/HS/SS descriptors and `strings` supplies the English interface string. `descs_to_legacy()` converts v2 descriptor blocks to the legacy FunctionFS descriptor header when a kernel rejects v2 with `EINVAL`. `struct thread` describes each endpoint loop. `init_thread()`, `start_thread_helper()`, `cleanup_thread()`, `start_thread()`, and `join_thread()` own endpoint lifecycle. `fill_in_buf()` and `empty_out_buf()` implement zero, sequence, or pipe patterns, while `ep0_init()` writes descriptors and strings and `ep0_consume()` decodes FunctionFS events.

Control flow: `main()` opens ep0, initializes descriptors, opens data endpoints, starts ep1 and ep2 worker threads, and runs the ep0 event loop in the main thread. Each endpoint thread repeatedly calls its `in` callback, then its `out` callback, until EOF or a non-retryable error. Cleanup checks FunctionFS FIFO status/flush ioctls for data endpoints before closing.

State and dependencies: state is process-local except for FunctionFS endpoint files in the current mount directory and stdout/stdin when `PAT_PIPE` is selected. The descriptor definitions depend on Linux USB UAPI and `tools/le_byteshift.h`; runtime depends on pthreads and a mounted/configured FunctionFS instance. Risks include indefinite loops, global `pattern` defaulting to zero with no CLI parser despite comments, descriptor address/name assumptions matching the gadget configuration, and partial event reads being interpreted only by whole-event count. Test signals are successful descriptor/string writes, printed bind/enable/setup events, endpoint transfer progress without `EILSEQ`, and FIFO flush warnings during cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/ffs-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/hcd-tests.sh -->
# sources/distributed-fs/ceph-client/tools/usb/hcd-tests.sh

Purpose: this shell script is a long-running stress harness around `./testusb` for host-controller-driver and usbtest firmware coverage. It groups usbtest ioctl cases into named workloads such as `control`, `out`, `in`, `iso-out`, `iso-in`, `halt`, `unlink`, and `loop`.

Important APIs and commands: `do_test()` invokes `./testusb` with the selected device mode, buffer size, iteration count, and usbtest case arguments. `check_config()` enforces that mutually incompatible workload families are not mixed after a configuration assumption is established. `DEVICE` controls whether testing targets one device or all recognized devices via `-a`.

Control flow: defaults are `TYPES='control out in'`, `COUNT=50000`, and `BUFLEN=2048`, but the main infinite loop resets count and length for each type, dispatches a `case`, and exits on the first failing `testusb` command. Each branch tunes iterations, transfer size, scatter/gather length, and variation to exercise normal, short, unaligned, isochronous, halt, and unlink paths.

State and dependencies: persistent state is minimal; the script loops forever and prints timestamps and progress to stdout. It depends on Bash-style `declare -i` despite `#!/bin/sh`, on a locally built `testusb`, on the kernel `usbtest` driver and matching gadget firmware/configuration, and optionally on `DEVICE`. Risks are non-portability under strict POSIX `/bin/sh`, infinite execution by design, hidden `testusb` stderr, and manual configuration assumptions. Test signals are pass/fail exit status, case progress lines, and sustained operation under mixed system load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/hcd-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/p9_fwd.py -->
# sources/distributed-fs/ceph-client/tools/usb/p9_fwd.py

Purpose: `p9_fwd.py` forwards 9P filesystem messages between a USB gadget interface and a TCP 9P server. It is aimed at `usb9pfs` inside a composite gadget, discovering the vendor-specific 9P interface and shuttling length-prefixed 9P packets between PyUSB endpoints and a socket.

Important APIs and functions: `path_from_usb_dev()` derives a stable bus-port path for selecting devices behind hubs. `Forwarder.__init__()` locates the USB device by VID/PID/path, detaches storage interfaces when needed, claims the 9P interface, finds IN/OUT endpoints, and connects to the TCP server. `c2s()` reads a packet from USB IN and sends it to TCP; `s2c()` reads a packet from TCP and writes it to USB OUT, adding a zero-length packet for max-packet-aligned USB transfers. `list_usb()` prints matching devices, and `connect()` runs the forwarding loop.

Control flow: `main()` builds an argparse CLI with `list` and `connect` subcommands and log verbosity. The connect loop alternates one client-to-server request with one server-to-client response, assuming request/response lockstep. USB transient read timeout and `EIO` are retried; other USB errors abort and final statistics are printed in `finally`.

State and dependencies: state includes socket connection, claimed USB interface, endpoint descriptors, counters, and periodic stats timing. Dependencies are PyUSB/libusb, `/sys/bus/usb/devices` metadata for names, TCP reachability to the 9P server, and a gadget interface class/subclass/protocol of `0xff/0xff/0x09`. Risks include blocking or short TCP reads returning empty buffers, `socket.send()` not guaranteeing full sends, assumptions about 4-byte little-endian 9P size fields, and no concurrent full-duplex pumping. Test signals are successful `list`, interface claim logs, packet counters, trace hexdumps, and a mounted 9P client behaving through the forwarder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/p9_fwd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/testusb.c -->
# sources/distributed-fs/ceph-client/tools/usb/testusb.c

Purpose: `testusb.c` is the userspace frontend for the kernel `usbtest` driver. It discovers recognized USB test devices under usbfs, then issues `USBDEVFS_IOCTL` requests wrapping `USBTEST_REQUEST` to run kernel-side transfer test cases.

Important APIs, types, and functions: `struct usbtest_param` mirrors the ioctl payload with test number, iterations, length, variation, scatter/gather count, and duration. `struct testdev` tracks discovered devices, speed, interface number, thread, and parameters. `testdev_ifnum()` recognizes known test VID/PID pairs and FunctionFS descriptors, using `testdev_ffs_ifnum()` to scan interface descriptors. `find_testdev()` is the `ftw()` callback. `usbdev_ioctl()` wraps interface ioctls. `handle_testdev()` opens the device, queries `USBDEVFS_GET_SPEED`, runs selected test cases, and prints duration or errors.

Control flow: `main()` parses `-D`, `-a`, `-A`, `-c`, `-g`, `-l`, `-n`, `-s`, `-t`, and `-v`, discovers `/dev/bus/usb` unless an alternate tree is supplied, builds a linked list of recognized devices, then either runs a single device inline or starts one pthread per device. `-l` restarts test enumeration forever.

State and dependencies: state is in process memory plus opened usbfs device files. It depends on usbfs, kernel `usbtest` support, usbdevfs ioctls, pthreads, and known device descriptors. Risks include intentionally permissive fallback when a specific `DEVICE` is not recognized, test result errors being ignored for threaded all-device mode, descriptor parsing trusting length bytes, and requiring privileges for device ioctls. Test signals are recognized device listings, per-test timing lines, ioctl errno lines, and stress behavior when run through `hcd-tests.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/testusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/Makefile.am -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/Makefile.am

Purpose: this top-level Automake file defines the usbip userspace package layout. It builds the library and command subdirectories, installs selected public headers, and distributes man pages for `usbip` and `usbipd`.

Important build declarations: `SUBDIRS := libsrc src` orders the shared library before the CLI/daemon. `includedir = @includedir@/usbip` places installed headers under an `usbip` include subdirectory. `include_HEADERS` exports common library headers such as `usbip_common.h`, `vhci_driver.h`, `usbip_host_driver.h`, `list.h`, `sysfs_utils.h`, and `usbip_host_common.h`. `dist_man_MANS` packages `doc/usbip.8` and `doc/usbipd.8`.

Control flow and integration: generated by Autotools from `configure.ac`, this file ties `libsrc/Makefile.am` and `src/Makefile.am` into the recursive build. It is the bridge between configuration-time substitutions and installed development/runtime artifacts.

State, dependencies, risks, and tests: there is no runtime state. It depends on Automake variables supplied by `configure`. Risks are header install drift when new library APIs are added but `include_HEADERS` is not updated, and recursive build failures if subdir order changes. Test signals are successful `autoreconf`, `configure`, `make`, `make install`, and man/header installation into the expected paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/autogen.sh -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/autogen.sh

Purpose: `autogen.sh` regenerates the usbip Autotools build system from checked-in `configure.ac` and `Makefile.am` files.

Important commands: the only active command is `autoreconf -i -f -v`, which installs missing helper files, forces regeneration, and emits verbose progress. Older explicit tool invocations (`aclocal`, `autoheader`, `libtoolize`, `automake`, `autoconf`) remain commented as historical context.

Control flow and state: the shell runs with `-x`, so each command is echoed. Generated state includes `configure`, `Makefile.in`, `aclocal.m4`, libtool helper files, and other Autotools artifacts later removable by `cleanup.sh`.

Dependencies, risks, and tests: it depends on Autoconf, Automake, Libtool support, and m4 macros for libudev/libwrap checks. Risks include host-tool version differences changing generated files and `-f` overwriting local generated artifacts. Test signals are a successful `autoreconf` exit, generated `configure`, and a following `./configure && make` succeeding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/cleanup.sh -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/cleanup.sh

Purpose: `cleanup.sh` removes generated Autotools and build files from the usbip userspace directory.

Important commands and data: if a readable `Makefile` exists, it first runs `make distclean`. It then removes a fixed `FILES` list containing `aclocal.m4`, `autom4te.cache`, `compile`, `config.*`, `configure`, `depcomp`, `install-sh`, `libtool`, `ltmain.sh`, top-level and subdir `Makefile`/`Makefile.in`, `missing`, and `cscope.out`.

Control flow and persistence: the script is linear and destructive for generated files only. It uses `rm -vRf`, so deletion is recursive for directories such as `autom4te.cache` and verbose for auditability.

Dependencies, risks, and tests: it assumes the current directory is `tools/usb/usbip`. Risks include deleting a user-maintained file if it has the same generated filename, and `make distclean` executing arbitrary generated make rules. Test signals are a clean source tree where `autogen.sh` can regenerate the removed files and `git status` shows only expected generated-file changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/cleanup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/configure.ac -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/configure.ac

Purpose: `configure.ac` defines the usbip-utils Autoconf configuration. It prepares package metadata, libtool versioning, compiler flags, feature checks, library checks, and generated Makefiles for the usbip userspace tools.

Important macros and settings: `AC_INIT` declares `usbip-utils` version `2.0`; `AC_DEFINE([USBIP_VERSION], [0x00000111])` defines protocol/tool version; `LIBUSBIP_VERSION` is `0:1:0`; `LT_INIT` enables libtool. `EXTRA_CFLAGS` enforces `-Wall -Werror -Wextra -std=gnu99`. Header/type/function checks validate common POSIX networking support. The libudev check is mandatory. Optional TCP wrappers are enabled if requested or auto-detected. `--with-usbids-dir` sets `USBIDS_DIR`, and `--with-fortify` can add `_FORTIFY_SOURCE=2`.

Control flow and integration: after checks, `AC_CONFIG_FILES` emits `Makefile`, `libsrc/Makefile`, and `src/Makefile`. The substitutions are consumed by Automake files for include paths, `USBIDS_FILE`, compiler flags, and library versioning.

State, dependencies, risks, and tests: generated state includes `config.h`, Makefiles, and configure cache/logs. Dependencies are Autoconf 2.59+, Automake, Libtool, a C compiler, libudev headers/library, and optionally libwrap. Risks include `-Werror` breaking builds on newer compilers, default usb.ids path mismatch across distributions, and deprecated `AC_TRY_LINK`. Test signals are successful `./configure`, correct `config.h` defines, and compile/link of `libusbip`, `usbip`, and `usbipd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/Makefile.am -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/Makefile.am

Purpose: this Automake file builds `libusbip.la`, the shared support library used by `usbip` and `usbipd`.

Important declarations: `libusbip_la_CPPFLAGS` defines `USBIDS_FILE` from `@USBIDS_DIR@/usb.ids`; `libusbip_la_CFLAGS` inherits `@EXTRA_CFLAGS@`; `libusbip_la_LDFLAGS` sets libtool version info. `lib_LTLIBRARIES := libusbip.la` declares the installed library. Source membership includes USB name parsing, host/vUDC driver backends, common USB/sysfs helpers, VHCI driver access, and headers.

Control flow and integration: this file is generated into `libsrc/Makefile` by configure and is built before `src` through the parent `SUBDIRS`. `src/Makefile.am` links commands against `$(top_builddir)/libsrc/libusbip.la`.

State, dependencies, risks, and tests: no runtime state is owned here. Build dependencies include libudev and Linux USB headers through the source files. Risks include stale source lists causing missing symbols, and `USBIDS_FILE` being compiled in at build time. Test signals are successful library compile/link and downstream command link without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/list.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/list.h

Purpose: `list.h` provides a small userspace copy of Linux kernel-style intrusive doubly linked lists for usbip internals.

Important APIs: `struct list_head` stores `next` and `prev`. `LIST_HEAD_INIT`, `LIST_HEAD`, and `INIT_LIST_HEAD()` initialize lists. `list_add()` inserts after a head, `list_del()` removes and poisons pointers, `list_entry()` maps a node pointer back to its containing struct, and `list_for_each()`/`list_for_each_safe()` iterate. Local `offsetof` and `container_of` macros support embedding.

Control flow and state: the list primitives mutate only embedded pointers inside caller-owned objects. usbip uses them for exported-device lists in the host and device driver backends.

Dependencies, risks, and tests: it depends on GNU C `typeof` in `container_of`, so strict non-GNU compilers are not supported. It lacks many kernel-list helpers and no runtime validation is performed; misuse can corrupt process memory. `LIST_POISON*` helps expose use-after-delete under debugging. Test signals are successful enumeration/destruction of exported device lists, especially safe deletion through `list_for_each_safe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.c

Purpose: `names.c` parses the `usb.ids` database and provides lookup tables for vendor, product, class, subclass, and protocol names used in usbip list/port output.

Important APIs, types, and functions: hash buckets store linked `vendor`, `product`, `class`, `subclass`, and `protocol` records. Public lookups are `names_vendor()`, `names_product()`, `names_class()`, `names_subclass()`, and `names_protocol()`. `names_init()` opens a database and calls `parse()`. `names_free()` releases all allocations tracked through the custom `pool` list. Internal `new_*()` helpers deduplicate and insert records.

Control flow: `parse()` reads lines, strips CR/LF, skips comments and unsupported sections, tracks current vendor/class context, and interprets tab indentation as product/subclass/protocol entries. It ignores many usb.ids sections such as HID, HUT, languages, reports, physical descriptors, and audio terminal metadata.

State and dependencies: parsed data is held in static global hash tables and a static allocation pool. It depends on a valid usb.ids format and `usbip_common` logging. Risks include no hash-table reset after `names_free()` leaving stale static bucket pointers, duplicate entries logged but ignored, parser fragility around unusual whitespace, and fixed 512-byte line buffers truncating long names. Test signals are successful `usbip list` output with names instead of unknown strings and no parser errors for common distribution `usb.ids` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.h

Purpose: `names.h` declares the USB name database interface implemented by `names.c`.

Important APIs: it exports lookup functions for vendor, product, class, subclass, and protocol names, plus `names_init(char *n)` to load a database and `names_free()` to release memory. The API uses fixed-width USB ID types from `<sys/types.h>`.

Control flow and integration: callers normally use the wrappers in `usbip_common.c` (`usbip_names_init()`, `usbip_names_get_product()`, and `usbip_names_get_class()`) rather than formatting directly. `usbip_list` and `usbip_port` initialize names around user-visible listing commands.

State, dependencies, risks, and tests: the header itself has no state, but the implementation behind it is global and process-wide. It has no const-correctness on the input path. Risks are limited API documentation and no explicit reinitialization contract. Test signals are compile-time consistency with `names.c` and correct name lookups after `names_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.c

Purpose: `sysfs_utils.c` centralizes writing strings to sysfs attributes for usbip commands and library helpers.

Important API: `write_sysfs_attribute(const char *attr_path, const char *new_value, size_t len)` opens an attribute path write-only, writes `len` bytes, logs debug messages on open/write failure, closes the descriptor, and returns `0` or `-1`.

Control flow and integration: callers build sysfs paths for driver `bind`, `unbind`, `rebind`, `match_busid`, `usbip_sockfd`, `attach`, and `detach` attributes, then pass the intended command string. This keeps path-specific logic out of the write primitive.

State, dependencies, risks, and tests: the function mutates kernel sysfs state and requires suitable privileges. It depends on `open`, `write`, and usbip logging. Risks include not verifying short positive writes against `len`, not preserving `errno` across `close`, and no retry on transient interruption. Test signals are driver state transitions after command writes and debug logs on permission or missing-attribute failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.h

Purpose: `sysfs_utils.h` declares the shared sysfs attribute write helper used by usbip library and command code.

Important API: `write_sysfs_attribute()` takes an attribute path, buffer pointer, and byte length, returning `0` on accepted write and `-1` on open/write failure.

Control flow and integration: the header is included by host common code, VHCI code, `usbip_bind`, `usbip_unbind`, and `utils.c` to modify kernel driver state through sysfs.

State, dependencies, risks, and tests: the header has no state. It relies on including files to provide `size_t` through other headers, which can be fragile if included standalone. Test signals are clean compilation in all current include contexts and successful sysfs operations through callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.c

Purpose: `usbip_common.c` provides shared logging controls, USB speed/status formatting, libudev sysfs readers, and usb.ids name formatting for usbip tools.

Important APIs and functions: global `usbip_use_syslog`, `usbip_use_stderr`, and `usbip_use_debug` drive logging macros from the header. `usbip_status_string()`, `usbip_speed_string()`, and `usbip_op_common_status_string()` format kernel/protocol statuses. `read_attr_value()` and `read_attr_speed()` read sysfs attributes through libudev. `read_usb_device()` fills `struct usbip_usb_device`; `read_usb_interface()` fills `struct usbip_usb_interface`. `usbip_names_*()` wrap `names.c` and format product/class strings.

Control flow and integration: host and vHCI driver discovery calls `read_usb_device()` on udev devices; listing and daemon replies use the packed device/interface structs over the network. Debug dump helpers format the same structs for trace output.

State and dependencies: it depends on the global `udev_context` defined in `vhci_driver.c` and reused by host common code, libudev sysattrs, Linux USB speed constants, and usb.ids parser globals. Risks include a global udev context shared across independent subsystems, benign missing attributes being folded into zero values, unchecked `sscanf(name, "%u-%u")` assumptions, and names parser lifecycle issues. Test signals are accurate list/port output, successful remote devlist serialization, and stable behavior when devices are unconfigured after binding to `usbip-host`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.h

Purpose: `usbip_common.h` defines usbip-wide constants, logging macros, wire-visible USB metadata structs, and shared helper prototypes.

Important types and constants: it defines default `USBIDS_FILE`, `VHCI_STATE_PATH`, module names (`usbip-core`, `usbip-host`, `usbip-vudc`, `vhci_hcd`), sysfs constants, protocol status codes, and `struct usbip_usb_device`/`struct usbip_usb_interface` with packed layout. Logging macros `err`, `info`, and `dbg` route to syslog and/or stderr.

Control flow and integration: the packed structs are used both for sysfs discovery and network PDUs, so layout compatibility matters. The macros are included by library, CLI, and daemon code, making global logging flags the process-wide output control.

State, dependencies, risks, and tests: it depends on libudev and Linux USB/UAPI headers. Risks include packed structs crossing ABI/protocol boundaries, fixed path/busid sizes, variadic GNU-style macros, and `PROGNAME` redefinition by individual C files. Test signals are compile compatibility, correct byte packing in network code, and readable diagnostics under `--debug` and `--log`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.c

Purpose: `usbip_device_driver.c` implements the usbip generic-driver backend for virtual UDC (`usbip-vudc`) device-mode exports.

Important functions and data: `read_usb_vudc_device()` reads a vUDC parent platform device's binary `dev_desc`, copies descriptor fields into `struct usbip_usb_device`, maps `current_speed` strings to USB speed enums, and uses the platform device name as the busid. `is_my_device()` checks the `USB_UDC_NAME` property for `usbip-vudc`. `usbip_device_driver_open()` initializes the generic list and reports missing modules. The exported `device_driver` struct sets subsystem `udc` and provides generic open/close/refresh/get hooks plus vUDC-specific read/filter functions.

Control flow and integration: `usbipd --device` selects `device_driver` instead of `host_driver`, so daemon devlist/import requests enumerate vUDC gadgets instead of physical USB devices. Interface reading is intentionally omitted because vUDC does not support it here.

State and dependencies: state is in the generic exported-device list and libudev context. It depends on sysfs `dev_desc`, `current_speed`, UDC properties, and little-endian USB descriptors. Risks include failing if the descriptor file is absent or short, no interface data in devlist replies, assuming the parent relation and sysname are stable, and using string speed names that must match kernel output. Test signals are `usbipd --device`, `usbip list -r`, and successful attach of a ConfigFS gadget bound to `usbip-vudc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.h

Purpose: this header exports the vUDC/device-mode usbip driver backend.

Important API: `extern struct usbip_host_driver device_driver;` exposes a backend compatible with the generic `usbip_host_driver` interface even though it enumerates UDC devices rather than host USB devices.

Control flow and integration: `usbipd.c` switches its global `driver` pointer to `&device_driver` when invoked with `--device`, reusing the same daemon protocol handlers for virtual device export.

State, dependencies, risks, and tests: the header pulls in common USB metadata, host common backend types, and list support. Risks are semantic confusion from using `usbip_host_driver` names for device-mode operation. Test signals are compile-time visibility to `usbipd.c` and successful runtime selection with `usbipd --device`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.c

Purpose: `usbip_host_common.c` implements generic exported-device enumeration and export operations shared by physical host and vUDC backends.

Important functions: `read_attr_usbip_status()` reads a device's `usbip_status` sysfs attribute. `usbip_exported_device_new()` builds a `struct usbip_exported_device`, invokes backend-specific device/interface readers, reallocates for interface records, and reads status. `refresh_exported_devices()` enumerates a backend subsystem through libudev and filters with `is_my_device()`. `usbip_generic_driver_open()`, `usbip_generic_driver_close()`, and `usbip_generic_refresh_device_list()` manage udev context and the exported list. `usbip_export_device()` writes a connected socket descriptor to `usbip_sockfd`. `usbip_generic_get_device()` indexes the list.

Control flow and integration: `host_driver` and `device_driver` use these functions through `struct usbip_host_driver_ops`. `usbipd` refreshes the list before each PDU and calls `usbip_export_device()` on import requests.

State and dependencies: state is a linked list of heap-allocated exported devices and a global libudev context. Persistent kernel state changes when `usbip_sockfd` receives the daemon's accepted connection fd. Risks include missing NULL checks after `calloc`, potential udev refs not being unreffed for enumeration temp devices, short status reads, and race windows between status enumeration and export. Test signals are accurate devlist contents, correct busy/error status handling, and kernel takeover of the socket after import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.h

Purpose: `usbip_host_common.h` defines the generic exported-device backend abstraction for usbip daemon-side device providers.

Important types and APIs: `struct usbip_host_driver_ops` contains open/close/refresh/get and backend-specific read/filter callbacks. `struct usbip_host_driver` stores device count, exported list, subsystem name, and ops. `struct usbip_exported_device` combines a udev handle, status, USB metadata, list node, and flexible interface array. Inline wrappers call optional ops and return `-EOPNOTSUPP` or NULL when missing. Generic helper prototypes expose open/close/refresh/export/get behavior.

Control flow and integration: both `host_driver` and `device_driver` instantiate this abstraction. `usbipd` treats the selected backend uniformly for devlist and import handling.

State, dependencies, risks, and tests: it depends on libudev, list primitives, common USB structs, and sysfs helper declarations. Risks include flexible-array allocation mistakes, backend callbacks being optional in ways command code must tolerate, and the host-oriented naming obscuring device-mode behavior. Test signals are successful compilation of both backend implementations and daemon operation in default and `--device` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.c

Purpose: `usbip_host_driver.c` implements the daemon backend for physical USB devices bound to the `usbip-host` kernel driver.

Important functions and data: `is_my_device()` accepts libudev USB devices whose current driver is `usbip-host`. `usbip_host_driver_open()` initializes list state, calls the generic open/enumeration path, and logs module-loading guidance when no devices are found. The exported `host_driver` struct sets subsystem `usb` and callbacks for common open/close/refresh/get, `read_usb_device()`, `read_usb_interface()`, and the filter.

Control flow and integration: this is the default backend selected by `usbipd`. It only exports devices already rebound by `usbip bind`, so binding and daemon export are separate steps.

State and dependencies: runtime state is the generic exported-device list. It depends on libudev driver names, `usbip-core.ko`, `usbip-host.ko`, and sysfs attributes created by the kernel driver. Risks include driver-name matching failures, stale enumeration under hotplug races, and no direct binding fallback inside the daemon. Test signals are `usbip bind -b BUSID`, `usbipd`, and `usbip list -r HOST` showing the bound device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.h

Purpose: this header exports the physical-host usbip backend.

Important API: `extern struct usbip_host_driver host_driver;` exposes the backend instance consumed by `usbipd`.

Control flow and integration: `usbipd.c` initializes its global `driver` to `&host_driver` unless `--device` is selected. The backend plugs into generic devlist/import logic through `usbip_host_common.h`.

State, dependencies, risks, and tests: the header has no state. It depends on common USB metadata, list support, and the backend abstraction. Risks are minimal, mostly coupling all users to the concrete global backend instance. Test signals are successful daemon build/link and default daemon enumeration of `usbip-host` devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.c

Purpose: `vhci_driver.c` is the client-side library for controlling the local `vhci_hcd` virtual host controller. It discovers ports, parses imported-device status, attaches sockets to ports, detaches ports, and prints imported-device records.

Important functions: `usbip_vhci_driver_open()` creates a udev context, finds platform device `vhci_hcd.0`, reads `nports`, counts controllers, allocates `vhci_driver`, and refreshes imported devices. `parse_status()` parses `status` and `status.N` sysfs text into `struct usbip_imported_device` entries. `usbip_vhci_get_free_port()` selects a high/super-speed-compatible free port. `usbip_vhci_attach_device2()` writes `port sockfd devid speed` to `attach`; `usbip_vhci_detach_device()` writes a port to `detach`. `read_record()` reads `/var/run/vhci_hcd/portN`, and `usbip_vhci_imported_device_dump()` formats port ownership.

Control flow and integration: `usbip attach` opens this driver after receiving a remote import reply, attaches the connected TCP socket to a free VHCI port, then records host/port/busid in `/var/run/vhci_hcd`. `usbip detach` and `usbip port` use the same parsed status.

State and dependencies: state includes global `vhci_driver`, global `udev_context`, kernel sysfs attributes, and persistent `/var/run/vhci_hcd/portN` files. Risks include global context conflicts, strict parsing of kernel status format, status arrays indexed by parsed port, no locking around state files, and attach/detach requiring root and loaded modules. Test signals are `usbip attach`, `usbip port`, valid `/var/run/vhci_hcd/portN`, and correct detach cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.h

Purpose: `vhci_driver.h` declares the client-side VHCI control API and data structures.

Important types and APIs: `enum hub_speed` distinguishes high-speed and super-speed hubs. `struct usbip_imported_device` stores hub type, port, status, remote devid/bus/dev numbers, and local USB metadata. `struct usbip_vhci_driver` owns the udev handle, controller count, port count, and flexible imported-device array. APIs open/close/refresh the driver, find a free port, attach by devid or bus/dev, detach, and dump imported devices.

Control flow and integration: `usbip_attach.c`, `usbip_detach.c`, and `usbip_port.c` include this header to manipulate the local virtual host controller.

State, dependencies, risks, and tests: the header exposes the global `vhci_driver`, coupling callers to open-before-use ordering. It depends on libudev and common USB metadata. Risks include callers dereferencing the global after failed open and deprecated `usbip_vhci_attach_device()` still present. Test signals are successful compile/link of attach/detach/port and runtime behavior across high-speed and super-speed devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/vhci_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/Makefile.am -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/Makefile.am

Purpose: this Automake file builds the installed `usbip` CLI and `usbipd` daemon.

Important declarations: `AM_CPPFLAGS` includes `libsrc` and defines `USBIDS_FILE`; `AM_CFLAGS` inherits configure flags; `LDADD` links against `libusbip.la`. `sbin_PROGRAMS := usbip usbipd` declares both binaries. `usbip_SOURCES` includes command dispatch, utilities, network helpers, and attach/detach/list/bind/unbind/port subcommands. `usbipd_SOURCES` includes daemon code and network helpers.

Control flow and integration: generated Makefiles compile commands after the library. The daemon and CLI share `usbip_network.c`, while only the CLI includes command submodules.

State, dependencies, risks, and tests: no runtime state is owned here. Build depends on libusbip and configured libudev/libwrap linkage. Risks include source-list drift, compiled-in usb.ids path, and daemon linking network code separately from the CLI. Test signals are successful build of both sbin programs and command help/version execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.c

Purpose: `usbip.c` is the top-level command dispatcher for the `usbip` CLI.

Important APIs and functions: `struct command` maps command names to implementation functions, help text, and usage callbacks. The command table includes `help`, `version`, `attach`, `detach`, `list`, `bind`, `unbind`, and `port`. `usbip_help()` prints global or command-specific help. `usbip_version()` prints `PACKAGE_STRING`. `main()` handles global `--debug`, `--log`, and `--tcp-port`.

Control flow: after global option parsing, `main()` identifies the subcommand, rewrites `argc/argv` to start at that command, resets `optind`, and calls `run_command()`. Invalid options or unknown commands print usage/help and return failure.

State and dependencies: global logging flags from `usbip_common` and global port state from `usbip_network` are modified. It depends on command implementations declared in `usbip.h`. Risks include global `optind` reuse across subcommands, default command failure when no command is provided, and syslog opened with an empty ident. Test signals are `usbip help`, per-command help, `usbip version`, custom port selection, and debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.h

Purpose: `usbip.h` is the internal CLI header for `usbip` subcommands.

Important APIs: it conditionally includes generated `config.h` and declares command entry points `usbip_attach()`, `usbip_detach()`, `usbip_list()`, `usbip_bind()`, `usbip_unbind()`, and `usbip_port_show()`, plus usage functions for commands that have argument help.

Control flow and integration: `usbip.c` dispatches through these prototypes; each subcommand implements its own getopt parsing and returns `0` or negative failure.

State, dependencies, risks, and tests: the header has no state. It depends on the source files matching function signatures. Risks are minimal but adding a command requires coordinated updates to this header and the command table. Test signals are successful CLI build and all command symbols resolving at link time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_attach.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_attach.c

Purpose: `usbip_attach.c` implements `usbip attach`, connecting to a remote `usbipd`, requesting a device import, and attaching the returned connection to a local VHCI port.

Important functions: `record_connection()` creates `/var/run/vhci_hcd` and writes `host port busid` into `portN`. `import_device()` opens the local VHCI driver, finds a compatible free port, and writes the socket/devid/speed to VHCI attach, retrying on `EBUSY`. `query_import_device()` sends `OP_REQ_IMPORT`, sends the busid request, validates the `OP_REP_IMPORT` reply, and passes device metadata to `import_device()`. `attach_device()` performs TCP connect, import query, socket close, and state-file recording. `usbip_attach()` parses `-r`, `-b`, and `-d`.

Control flow and integration: the remote server takes ownership of the connection by receiving the socket fd in its kernel driver, while the local client passes the connected socket to `vhci_hcd`. `-d` is treated like `-b` for vUDC busids.

State and dependencies: persistent state is `/var/run/vhci_hcd/portN`; kernel state changes through VHCI sysfs. Dependencies are `vhci_hcd`, remote `usbipd`, TCP, and protocol helpers. Risks include leaking the socket on some failure paths, closing the fd after attach assuming the kernel duplicated/owns it, no validation of host/port string length beyond fixed buffer, and no rollback if `record_connection()` fails after kernel attach. Test signals are `usbip attach -r HOST -b BUSID`, new imported device under `usbip port`, and matching state file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_bind.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_bind.c

Purpose: `usbip_bind.c` implements `usbip bind`, preparing a local physical USB device for export by rebinding it to the `usbip-host` kernel driver.

Important functions: `bind_usbip()` writes the busid to `/sys/bus/usb/drivers/usbip-host/bind`. `unbind_other()` uses libudev to locate the device, skips hubs, detects if already bound to `usbip-host`, and writes to the current driver's `unbind` attribute when needed. `bind_device()` validates existence, rejects devices already under `vhci_hcd` to avoid loops, updates `match_busid` with `modify_match_busid(add=1)`, and binds to usbip-host. `usbip_bind()` parses `-b`.

Control flow and integration: binding is a two-step kernel-driver protocol: first add the busid to usbip-host's match table, then bind the driver. If bind fails after match update, it removes the busid again.

State and dependencies: it mutates sysfs driver binding state and the usbip-host match list. It depends on root privileges, libudev, `usbip-host.ko`, and writable sysfs attributes. Risks include unbinding active class drivers unexpectedly, hub detection relying on `bDeviceClass == "09"`, not unrefing some libudev objects on early returns, and races with hotplug. Test signals are `usbip bind -b BUSID`, driver showing as `usbip-host`, and remote `usbip list -r` exposing the device after daemon start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_detach.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_detach.c

Purpose: `usbip_detach.c` implements `usbip detach`, removing an imported USB device from a local VHCI port.

Important functions: `detach_port()` validates that the `-p` argument contains only digits, opens the VHCI driver, confirms the port exists and is not already empty, removes `/var/run/vhci_hcd/portN`, attempts to remove the state directory, and writes the port to the VHCI `detach` sysfs attribute. `usbip_detach()` parses `-p`.

Control flow and integration: state-file removal happens before the kernel detach request. The driver list parsed during open is used to reject invalid ports and no-op empty ports.

State and dependencies: it mutates local VHCI kernel state and `/var/run/vhci_hcd`. It depends on root privileges and loaded `vhci_hcd`. Risks include removing the state file before a detach failure, `uint8_t` truncation of large port numbers after string validation, directory removal failing silently if other ports remain, and no synchronization with concurrent attach/detach. Test signals are `usbip detach -p N`, `usbip port` no longer showing the device, and `/var/run/vhci_hcd/portN` being removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_detach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_list.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_list.c

Purpose: `usbip_list.c` implements `usbip list`, covering remote exportable devices, local physical USB devices, and local vUDC gadget devices.

Important functions: `get_exported_devices()` sends `OP_REQ_DEVLIST`, receives device/interface records, unpacks them, and prints names/classes. `list_exported_devices()` handles TCP connect. `list_devices()` enumerates non-hub USB devices through libudev, skips devices under `vhci_hcd`, and prints busid/vendor/product. `list_gadget_devices()` scans platform devices bound to `usbip-vudc`, reads the binary descriptor sysattr, and prints gadget identity. `usbip_list()` parses `-p`, `-r`, `-l`, and `-d` and initializes usb.ids names.

Control flow and integration: only one listing mode is executed per invocation. Remote mode uses the usbip daemon protocol; local modes read sysfs directly.

State and dependencies: state is transient libudev enumeration, TCP sockets, and names database globals. Dependencies include usb.ids, libudev, network protocol helpers, and Linux descriptor layout. Risks include a likely typo assigning `idProduct_buf` from `idVendor`, not unrefing skipped udev devices in all paths, strict remote PDU sequencing, and parsable mode printing only partial metadata. Test signals are useful output for `usbip list -l`, `usbip list -d`, `usbip list -r HOST`, and named products/classes when usb.ids is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.c

Purpose: `usbip_network.c` implements shared usbip TCP connection handling, socket options, common PDU send/receive, and byte-order packing.

Important APIs: global `usbip_port` and `usbip_port_string` default to 3240 and can be changed by `usbip_setup_port_number()`. `usbip_net_pack_uint32_t()`, `usbip_net_pack_uint16_t()`, `usbip_net_pack_usb_device()`, and `usbip_net_pack_usb_interface()` convert wire fields. `usbip_net_recv()` and `usbip_net_send()` loop through `recv(MSG_WAITALL)`/`send()` via `usbip_net_xmit()`. `usbip_net_send_op_common()` and `usbip_net_recv_op_common()` handle the shared header. Socket helpers set reuseaddr, nodelay, keepalive, v6only, and `usbip_net_tcp_connect()` resolves/connects IPv4 or IPv6 addresses.

Control flow and integration: CLI and daemon call these routines before command-specific PDUs. Version and status validation happen in `usbip_net_recv_op_common()`.

State and dependencies: state is global port configuration and socket options. It depends on POSIX sockets, getaddrinfo, TCP, and protocol constants. Risks include send/recv treating any zero/negative as generic failure without preserving detailed errno, `usbip_setup_port_number()` leaving previous valid port after invalid input, returning `EAI_SYSTEM` as a positive pseudo-fd on total connect failure, and no TLS/authentication in the protocol. Test signals are remote list/import success over IPv4/IPv6 and correct rejection on protocol version/status mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.h

Purpose: `usbip_network.h` defines the userspace usbip protocol PDUs and networking helper API.

Important types and constants: `struct op_common` contains version, code, and status. Request/reply opcodes are defined for devinfo, import, export, unexport, crypkey, and devlist. PDU structs include import request/reply and devlist reply layouts using `struct usbip_usb_device` and `struct usbip_usb_interface`. Packing macros call byte-order helpers for structs with multi-byte fields.

Control flow and integration: `usbip_attach`, `usbip_list`, and `usbipd` share these definitions to exchange OP_REQ_IMPORT and OP_REQ_DEVLIST messages. Some opcodes are defined but unused by current handlers.

State, dependencies, risks, and tests: it declares global port configuration and socket helpers. It depends on packed common USB structs. Risks include wire ABI coupling to struct packing, empty packing macros for currently byte-neutral structs, unused legacy protocol definitions, and no bounds for variable-length trailing arrays beyond negotiated counts. Test signals are interoperability between `usbip` and `usbipd` built from the same headers and correct network byte order on mixed-endian systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_port.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_port.c

Purpose: `usbip_port.c` implements `usbip port`, which displays devices currently imported into local VHCI ports.

Important functions: `list_imported_devices()` initializes usb.ids names, opens the VHCI driver, prints a heading, iterates all `vhci_driver->idev` entries, and delegates formatting to `usbip_vhci_imported_device_dump()`. `usbip_port_show()` is the command entry point.

Control flow and integration: the command is read-only except for tracefs/sysfs reads done by VHCI open/refresh. It uses `/var/run/vhci_hcd/portN` records indirectly through the dump helper to show remote host and busid information.

State and dependencies: transient state includes names database globals and VHCI parsed status. Dependencies are `vhci_hcd`, usb.ids, and readable state files for full remote mapping. Risks include failing the entire command on VHCI open failure, incomplete host details if state files are missing, and reliance on the global `vhci_driver`. Test signals are `usbip port` output after attach and graceful "available" handling for empty ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_unbind.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_unbind.c

Purpose: `usbip_unbind.c` implements `usbip unbind`, reversing `usbip bind` for a device currently attached to `usbip-host`.

Important functions: `unbind_device()` validates that the busid exists and that its current driver is `usbip-host`, writes the busid to the driver's `unbind` attribute, removes it from `match_busid` with `modify_match_busid(add=0)`, then writes to the driver's `rebind` attribute to trigger normal probing. `usbip_unbind()` parses `-b`.

Control flow and integration: sysfs driver operations are sequenced as unbind, update match list, rebind. The command relies on usbip-host-specific attributes and shared sysfs writing.

State and dependencies: it mutates kernel driver binding and match-list state. It depends on root privileges, libudev, and loaded `usbip-host`. Risks include no rollback if match removal or rebind fails after unbinding, unref on potentially NULL `dev` in error paths, and no protection from concurrent daemon export. Test signals are `usbip unbind -b BUSID`, device no longer bound to usbip-host, and the original or another normal driver reprobing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_unbind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbipd.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbipd.c

Purpose: `usbipd.c` is the usbip daemon. It listens on TCP, enumerates exportable devices through a selected backend, serves devlist requests, and hands accepted sockets to kernel usbip drivers for import requests.

Important functions: `recv_request_import()` receives an import busid, finds the exported device, writes the accepted socket fd to `usbip_sockfd`, replies with status, and sends device metadata. `send_reply_devlist()` counts non-used devices and sends device/interface records. `recv_pdu()` receives the common header, refreshes the device list, and dispatches opcodes. `do_accept()` accepts TCP connections and optionally applies libwrap. `process_request()` forks a child per accepted connection. `listen_all_addrinfo()` opens sockets. `do_standalone_mode()` opens the selected backend, daemonizes if requested, writes PID file, polls listening fds, and handles shutdown. `main()` parses IPv4/IPv6, daemon, debug, device-mode, pid, port, help, and version options.

Control flow and integration: default mode exports physical `usbip-host` devices; `--device` exports `usbip-vudc` gadgets. Each request is handled in a child process, with the parent keeping listening sockets open.

State and dependencies: persistent state may include a PID file; kernel state changes when sockets are exported. Dependencies are root privileges, libudev, kernel usbip modules, TCP sockets, optional libwrap, and protocol helpers. Risks include fork-per-request scaling, ignored SIGCHLD to reap children, device-list refresh per request under hotplug races, no authentication unless libwrap is enabled, duplicate longopt entry for daemon, and accepted socket lifetime relying on kernel handoff. Test signals are daemon listening logs, `usbip list -r`, successful attach/import, PID file lifecycle, and device-mode operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbipd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.c -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.c

Purpose: `utils.c` provides the CLI helper for modifying the `usbip-host` driver's `match_busid` sysfs attribute.

Important API: `modify_match_busid(char *busid, int add)` builds `/sys/bus/usb/drivers/usbip-host/match_busid`, formats either `add BUSID` or `del BUSID`, and writes it with `write_sysfs_attribute()`.

Control flow and integration: `usbip bind` calls it before binding to allow the usbip-host driver to match the target device; `usbip unbind` calls it after unbinding to remove the special match.

State and dependencies: it mutates kernel driver matching state and depends on sysfs helper, root privileges, and a loaded usbip-host driver. Risks include command buffer truncation for maximum-length busids because the fixed buffer is `SYSFS_BUS_ID_SIZE + 4`, not checking `snprintf()` for truncation before writing, and no rollback logic in this helper. Test signals are visible match-list changes and successful bind/unbind workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.h -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.h

Purpose: `utils.h` declares the usbip CLI utility function for editing `usbip-host` match state.

Important API: `int modify_match_busid(char *busid, int add);` returns `0` on write success and `-1` on failure.

Control flow and integration: the bind and unbind subcommands include this header to coordinate driver match-table changes with sysfs bind/unbind operations.

State, dependencies, risks, and tests: the header has no state and no external dependencies beyond matching the implementation signature. Risks are minimal; semantics of `add` are implicit rather than an enum. Test signals are clean command compilation and bind/unbind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/vudc/vudc_server_example.sh -->
# sources/distributed-fs/ceph-client/tools/usb/usbip/vudc/vudc_server_example.sh

Purpose: this example script demonstrates creating a ConfigFS USB gadget, binding it to `usbip-vudc`, and exporting it with `usbipd --device`.

Important commands and variables: `CONFIGFS_MOUNT_POINT`, `GADGET_NAME`, `ID_VENDOR`, and `ID_PRODUCT` define gadget placement and identity. The script creates `functions/acm.ser0`, `configs/c.1`, symlinks the ACM function into the configuration, writes vendor/product IDs, loads `usbip-vudc` if needed, binds by writing `usbip-vudc.0` to `UDC`, and starts `usbipd --device` in the background.

Control flow and integration: `set -e` stops on errors. The comments document client-side `modprobe usbip-vhci`, remote list, and attach commands. It exercises the same device backend implemented by `usbip_device_driver.c`.

State and dependencies: it creates persistent ConfigFS gadget directories and starts a background daemon. It depends on root privileges, mounted configfs, ACM gadget support, `usbip-vudc`, and installed usbip tools. Risks include leaving gadget/daemon state behind, hard-coded gadget name and UDC instance, no cleanup trap, and a typo in comments. Test signals are `usbip list -r SERVER` showing `usbip-vudc.0` and `usbip attach -r SERVER -d usbip-vudc.0` creating a client-side serial device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/usb/usbip/vudc/vudc_server_example.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/Makefile -->
# sources/distributed-fs/ceph-client/tools/verification/rv/Makefile

Purpose: this Makefile builds the `rv` userspace tool for the Linux runtime verification subsystem.

Important variables and targets: it derives `srctree`, handles `O=`/`OUTPUT`, sets `RV` and `RV_IN`, computes `VERSION` from the kernel top-level makefile, and points `DOCSRC` to RV tool docs. Feature tests require/display `libtraceevent` and `libtracefs`. It includes tools build infrastructure, `Makefile.rv`, feature detection, and `Makefile.config`. `$(RV)` links `rv-in.o` with `$(EXTLIBS)`, `static` builds `rv-static`, pattern `rv.%` and `$(RV_IN)` delegate to `tools/build`, and `clean` removes objects, feature dumps, and generated binaries.

Control flow and integration: the Makefile is meant to be invoked from the kernel tools build system or directly. It exports build variables for sub-make and avoids dependency configuration for non-build targets such as clean/install/doc.

State, dependencies, risks, and tests: generated state lives under `OUTPUT`. Dependencies include kernel tools build scripts, libtraceevent, libtracefs, and compiler/linker settings. Risks include relative srctree assumptions, dependency-feature drift, and output path normalization errors. Test signals are successful `make`, `make static`, feature detection, and `./rv list` running on a kernel with CONFIG_RV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/in_kernel.h -->
# sources/distributed-fs/ceph-client/tools/verification/rv/include/in_kernel.h

Purpose: `in_kernel.h` declares the interface from the top-level `rv` CLI into in-kernel monitor support.

Important APIs: `ikm_list_monitors(char *container)` lists available monitors, optionally scoped to a container; `ikm_run_monitor(char *monitor, int argc, char **argv)` runs a named in-kernel monitor with monitor-specific options.

Control flow and integration: `rv.c` calls these functions for `rv list` and `rv mon`. The implementation in `src/in_kernel.c` maps CLI actions onto tracefs `rv/` files.

State, dependencies, risks, and tests: the header has no state. It depends on callers obeying root and tracefs availability requirements handled elsewhere. Risks are sparse documentation and return-code semantics that require consulting the implementation. Test signals are successful compile/link and `rv list`/`rv mon` reaching in-kernel monitor logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/in_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/rv.h -->
# sources/distributed-fs/ceph-client/tools/verification/rv/include/rv.h

Purpose: `rv.h` contains common runtime-verification tool definitions.

Important types and APIs: `MAX_DESCRIPTION` and `MAX_DA_NAME_LEN` bound monitor metadata. `struct monitor` stores a monitor name, description, enabled state, and nested flag. `should_stop()` lets monitor-running loops observe top-level signal-triggered shutdown.

Control flow and integration: `in_kernel.c` fills `struct monitor` records when listing tracefs monitors and calls `should_stop()` during monitor execution. `trace.c` also uses `should_stop()` to stop raw trace iteration.

State, dependencies, risks, and tests: state is implemented in `rv.c` as a static stop flag. Risks are truncation from fixed-size arrays and a process-global stop condition. Test signals are clean monitor listing with descriptions, and Ctrl-C/SIGTERM causing `rv mon` loops and trace collection to exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/rv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/trace.h -->
# sources/distributed-fs/ceph-client/tools/verification/rv/include/trace.h

Purpose: `trace.h` declares tracefs/libtraceevent helper state and functions used when `rv mon --trace` is enabled.

Important types and APIs: `struct trace_instance` combines a `tracefs_instance`, a local `tep_handle`, and a `trace_seq` buffer. `trace_instance_init()`, `trace_instance_start()`, and `trace_instance_destroy()` manage that state. `collect_registered_events()` is the callback passed to raw event iteration.

Control flow and integration: `in_kernel.c` creates a per-monitor trace instance, enables RV events, registers event handlers, and iterates raw events through `collect_registered_events()`.

State, dependencies, risks, and tests: the header depends on libtracefs/libtraceevent headers. Risks include trace instance lifecycle leaks if callers skip destroy, and callback behavior tied to event handlers registered in TEP. Test signals are trace instance creation/destruction and formatted event/error output from `rv mon MONITOR -t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/utils.h -->
# sources/distributed-fs/ceph-client/tools/verification/rv/include/utils.h

Purpose: `utils.h` declares shared diagnostic helpers for the `rv` tool.

Important APIs: `debug_msg()` prints only when `config_debug` is set; `err_msg()` always prints to stderr. `MAX_PATH` provides a local path buffer bound. `config_debug` is a global flag implemented in `src/utils.c`.

Control flow and integration: in-kernel monitor code uses these helpers for tracefs/read/write diagnostics, and CLI option parsing toggles `config_debug` on verbose mode.

State, dependencies, risks, and tests: state is a single global debug flag. Risks are fixed 1024-byte message/path buffers in callers and no syslog integration. Test signals are verbose messages appearing with `rv mon ... -v` and errors going to stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/include/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/in_kernel.c -->
# sources/distributed-fs/ceph-client/tools/verification/rv/src/in_kernel.c

Purpose: `in_kernel.c` implements the `rv` tool's control path for in-kernel runtime verification monitors exposed through tracefs.

Important functions: monitor discovery uses `__ikm_find_monitor_name()`, `__ikm_read_enable()`, `ikm_read_enable()`, `ikm_read_desc()`, and `ikm_fill_monitor_definition()`. Runtime control uses `ikm_enable()`, `ikm_disable()`, `ikm_write_reactor()`, `ikm_get_current_reactor()`, and `parse_arguments()`. Listing is exposed as `ikm_list_monitors()`. Trace setup uses `ikm_setup_trace_instance()`, `ikm_enable_trace_events()`, and `ikm_enable_trace_container()`. Event formatting is handled by `ikm_event_handler()` and `ikm_error_handler()`. `ikm_run_monitor()` finds a monitor, applies options, enables tracing and monitor execution, loops until `should_stop()`, then disables and restores the initial reactor.

Control flow: `rv mon` calls `ikm_run_monitor()`. The function rejects already-enabled monitors, parses options (`--reactor`, `--self`, `--trace`, `--verbose`), optionally creates a trace instance, enables the monitor through tracefs, drains trace events once per second, and cleans up on signal. Containers are represented by colon-separated monitor names in `available_monitors`, converted to slash paths for tracefs.

State and dependencies: process globals track id filtering, container mode, current PID, trace mode, and reactor state. Kernel state is changed through tracefs files under `rv/monitors/*`. Dependencies are tracefs, libtraceevent field access, CONFIG_RV, available monitor event formats, and reactor files. Risks include heavy string parsing of tracefs text, possible null dereference when expected newlines/brackets are absent, global config not reset between runs, and partial cleanup if enable succeeds but later trace setup fails. Test signals are `rv list`, container-scoped listing, `rv mon MON -t` formatted event/error rows, `--reactor` restoration, and Ctrl-C disabling the monitor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/in_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/rv.c -->
# sources/distributed-fs/ceph-client/tools/verification/rv/src/rv.c

Purpose: `rv.c` is the top-level CLI for the runtime verification tool.

Important functions: `stop_rv()` sets a process-global stop flag on SIGINT/SIGTERM. `should_stop()` exposes that flag. `rv_list()` parses `rv list [-h] [container]` and calls `ikm_list_monitors()`. `rv_mon()` validates `rv mon monitor [options]`, calls `ikm_run_monitor()`, and reports missing monitors. `usage()` prints global help. `main()` enforces root, dispatches commands, and installs signal handlers for monitor execution.

Control flow and integration: `main()` dispatches only `list` and `mon`. Subcommands exit directly. `rv_mon()` is written to support multiple monitor implementations by accumulating run results, currently only in-kernel monitors.

State and dependencies: state is the static `stop_session` flag. Dependencies include root privileges, in-kernel monitor support, and generated `VERSION` from the Makefile. Risks include subcommands exiting rather than returning, negative return from `ikm_run_monitor()` still contributing to `run` truthiness in some paths, and no non-root degraded mode. Test signals are help text, root check, monitor-not-found errors, and signal-driven shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/rv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/trace.c -->
# sources/distributed-fs/ceph-client/tools/verification/rv/src/trace.c

Purpose: `trace.c` provides tracefs/libtraceevent lifecycle and event-collection helpers for `rv mon --trace`.

Important functions: `create_instance()` wraps `tracefs_instance_create()`. `destroy_instance()` destroys and frees a tracefs instance. `collect_registered_events()` checks `should_stop()`, ignores events without handlers, and invokes registered event handlers with the shared `trace_seq`. `trace_instance_init()` allocates a sequence buffer, creates a trace instance, loads local events with `tracefs_local_events()`, and leaves tracing off. `trace_instance_start()` enables tracing; `trace_instance_destroy()` frees all components.

Control flow and integration: `in_kernel.c` initializes a trace instance, enables specific RV events, registers handlers on the `tep_handle`, turns tracing on, and iterates raw events. Cleanup destroys the trace instance and TEP data.

State and dependencies: state is held in `struct trace_instance`. Dependencies are libtracefs, libtraceevent, and tracefs permissions. Risks include `trace_instance_start()` currently being bypassed in favor of direct `tracefs_trace_on()`, no detailed error codes from init, and event handler callbacks relying on mutable `event->handler`. Test signals are creation of a named trace instance, event output, and absence of leftover trace instances after exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/utils.c -->
# sources/distributed-fs/ceph-client/tools/verification/rv/src/utils.c

Purpose: `utils.c` implements minimal stderr diagnostics for the `rv` tool.

Important APIs: global `config_debug` gates `debug_msg()`. `err_msg()` and `debug_msg()` format variadic messages into a 1024-byte stack buffer with `vsnprintf()` and write them to stderr.

Control flow and integration: in-kernel monitor support sets `config_debug` when `-v/--verbose` is parsed and calls these helpers for tracefs and parsing diagnostics.

State and dependencies: state is just `config_debug`. Dependencies are stdio/stdarg. Risks include message truncation without indication and no automatic newline insertion; callers must include desired formatting. Test signals are errors visible by default and debug lines visible only with verbose monitor options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rv/src/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/Makefile -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/Makefile

Purpose: this Makefile installs the Python `rvgen` runtime-verification monitor generator and its helper command.

Important variables and targets: `prefix`, `bindir`, `mandir`, and `srcdir` define install roots. `PYLIB` is detected through `python3 -c 'import sysconfig'`. `all` and `clean` are no-ops. `install` copies Python modules into `$(PYLIB)/rvgen`, installs `dot2c` and `rvgen` entry scripts into `$(bindir)`, and recursively copies templates.

Control flow and integration: there is no build step; installation is file copying. The module list includes files outside this subset such as `ltl2ba.py` and `ltl2k.py`, showing rvgen supports DOT and LTL monitor generation.

State, dependencies, risks, and tests: state is installed files under `DESTDIR`/system paths. Dependencies include Python 3 and `install`. Risks include no uninstall, no byte-compilation, no package metadata, and recursive template copy leaving stale files if reinstalling over older content. Test signals are `make install DESTDIR=...`, executable `rvgen`, executable `dot2c`, and imports from the installed `rvgen` package.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/__main__.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/__main__.py

Purpose: `__main__.py` is the installed `rvgen` CLI for generating kernel RV monitors or monitor containers.

Important APIs and flow: argparse defines global `--description` and `--auto_patch`, then subcommands `monitor` and `container`. Monitor generation requires model name, optional parent, class (`da`, `ha`, or `ltl`), spec file, and monitor type from `Monitor.monitor_types`. It dispatches to `da2k`, `ha2k`, or `ltl2k`, or constructs `Container`. `AutomataError` is caught and reported. On success it writes files with `monitor.print_files()` and prints follow-up checklist text for tracepoints, Makefile, Kconfig, and monitor placement.

State and dependencies: output state is a generated monitor directory or direct kernel-tree patches when `--auto_patch` is active. Dependencies are rvgen modules, templates, and writable current/kernel tree. Risks include `params.spec` being referenced in the exception path even for container errors, generated files overwriting existing monitor files through generator writes, and auto-patch marker matching being text-replace based. Test signals are generated files for deterministic, hybrid, LTL, and container modes, plus expected error handling for malformed specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/__main__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/dot2c -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/dot2c

Purpose: `dot2c` is a small executable wrapper that converts a DOT automaton into a C automaton model printed on stdout.

Important flow: it imports `rvgen.dot2c`, parses one positional `dot_file`, instantiates `Dot2c`, and calls `print_model_classic()`.

Control flow and integration: unlike `rvgen monitor`, it does not generate a full kernel monitor scaffold. It is useful for inspecting or embedding just the deterministic/hybrid automaton C representation produced from DOT.

State and dependencies: no persistent state is written by this script. It depends on Python 3, the installed/importable `rvgen` package, and a valid DOT file accepted by `Automata`. Risks include uncaught `AutomataError` tracebacks in this wrapper and stdout-only output without file selection. Test signals are `dot2c model.dot` producing enum definitions, transition matrix, and automaton initializer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/dot2c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/automata.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/automata.py

Purpose: `automata.py` parses Graphviz DOT deterministic or hybrid automata into normalized Python state/event/transition data used by rvgen generators.

Important types and functions: `_StateConstraintKey` and `_EventConstraintKey` distinguish state invariants from edge guards/resets in the `constraints` dictionary. `AutomataError` reports validation failures. `Automata.__init__()` loads DOT lines, derives model name, states, initial/final states, events, environment variables, transition matrix, constraints, and start-event metadata. Parsing helpers find node/event regions, extract constraints using regexes, infer environment units/storage needs, build the matrix, and identify events that always return to initial state or only run from initial state.

Control flow and integration: `Dot2c` and `dot2k` subclass `Automata` to format C model data and kernel monitor skeletons. Hybrid automata use constraints of the form `env op value` and `reset(env)` on labels; state labels can carry invariants.

State and dependencies: state is per parser object. Dependencies are DOT formatting conventions from RV docs and Python regex/string parsing. Risks include fragile parsing based on token positions, only supporting limited constraint/reset counts, unescaped labels being converted directly into C identifiers, and no graph determinism conflict detection beyond matrix overwrite behavior. Test signals are successful parsing of valid `.dot`/`.gv`, expected `AutomataError` on malformed specs, correct states/events ordering, and generated matrix matching DOT transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/automata.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/container.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/container.py

Purpose: `container.py` generates a kernel RV monitor container scaffold rather than a concrete automaton monitor.

Important class: `Container` subclasses `generator.RVGenerator` with `template_dir = "container"`. Its constructor reads the container `main.h` template and sets `self.name`. `fill_model_h()` substitutes `%%MODEL_NAME%%`. `fill_kconfig_tooltip()` appends or auto-patches a container-specific Kconfig marker so nested monitors can be inserted under that container.

Control flow and integration: the top-level `rvgen container -n NAME` command constructs this class and calls `print_files()`, which is inherited from `RVGenerator` to create `NAME.c`, `NAME.h`, and `Kconfig`.

State and dependencies: output files are written to a new local directory or kernel RV monitor directory with `--auto_patch`. Dependencies are generic and container templates. Risks include returning silently if the output directory already exists, marker-based auto-patching duplicating entries, and no validation of model name as a C/Kconfig-safe identifier. Test signals are generated container files and Kconfig tooltip/patch containing the new container marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/container.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2c.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2c.py

Purpose: `dot2c.py` formats an `Automata` object as C enums, transition matrix, and automaton initializer.

Important class and methods: `Dot2c` subclasses `Automata`. It defines enum/struct/variable names, invalid-state marker, and line length. Formatting methods emit states, events, optional env enums, minimal state storage type, automaton struct, string arrays, function matrix, initial state, and final-state bitmap. `get_minimun_type()` chooses `unsigned char`, `unsigned short`, or `unsigned int` based on state count and rejects extremely large models. `print_model_classic()` prints the full model.

Control flow and integration: `dot2c` executable uses this class directly. `dot2k` adjusts enum suffix/name fields and reuses `format_model()` to generate monitor header content.

State and dependencies: state is inherited automaton parse data plus output naming fields. Risks include generated C identifiers coming from DOT labels, typo in method name `get_minimun_type`, static assertions only for hybrid env storage, and output formatting not escaping quotes in labels. Test signals are compilable generated C for representative deterministic and hybrid DOT inputs, including large enough models to exercise type selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2c.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2k.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2k.py

Purpose: `dot2k.py` converts DOT deterministic (`da`) or hybrid (`ha`) automata into kernel RV monitor scaffolds.

Important classes and methods: `dot2k` inherits from `Monitor` and `Dot2c`, combines templates with automaton data, sets enum suffixes, and emits tracepoint handler skeletons, attach/detach stubs, model headers, tracepoint prototypes, monitor class type, and main C replacements. `da2k` rejects hybrid automata. `ha2k` requires hybrid automata, switches to hybrid trace templates, parses constraints into guards/invariants, emits env getter/resetter stubs, timer setup, invariant verification, guard verification, invariant/guard conversion, and hybrid constraint verification.

Control flow and integration: top-level `rvgen monitor -c da|ha` constructs these classes and writes monitor files. Generated code still contains `XXX` tracepoint and environment placeholders that developers must fill.

State and dependencies: state includes parsed automaton, monitor type (`global`, `per_cpu`, `per_task`, `per_obj`), parent/container, and templates. Dependencies are DOT label conventions, kernel RV DA/HA monitor APIs, and template placeholders. Risks include heavy f-string code generation requiring Python versions supporting the syntax, fragile string-based constraint parsing, multiple-inheritance initialization ordering, no validation that generated handler names are valid C, and subtle HA timer semantics if resets/invariants are modeled incorrectly. Test signals are generated scaffolds compiling after filling `XXX` hooks, expected errors when DA/HA class mismatches the spec, and unit examples covering guard, reset, invariant, stored env, and timer conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2k.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/generator.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/generator.py

Purpose: `generator.py` provides the abstract file/template generation framework for rvgen monitors and containers.

Important classes and methods: `RVGenerator` locates template directories, reads `main.c` and `Kconfig`, tracks name, parent, description, and auto-patch mode, and can locate the kernel `kernel/trace/rv` directory. It fills common template placeholders, emits Kconfig/Makefile/tracepoint tooltips or patches, creates output directories, and writes generated files. `Monitor` extends it with `monitor_types`, loads `trace.h`, fills tracepoint class placeholders, and writes the extra trace header.

Control flow and integration: concrete generators override `fill_model_h()`, monitor class methods, tracepoint skeleton methods, and sometimes Kconfig tooltip behavior. `print_files()` is the main side-effecting entry point used by `__main__.py`.

State and dependencies: output state is local monitor directories or direct kernel-tree modifications. Dependencies are template files, filesystem write permissions, and marker comments in kernel RV files for auto-patching. Risks include mutable default `extra_params={}`, text replacement without duplicate detection, silent reuse of existing directories, overwriting files, no atomic writes, and model names not sanitized for paths/C identifiers. Test signals are correct file sets for monitor/container generators, auto-patch finding intended kernel tree, and generated tooltip text matching manual integration points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/generator.py -->

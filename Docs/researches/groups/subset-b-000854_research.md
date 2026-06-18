# Research: subset-b-000854

Grouped research for the User-Mode Linux architecture Kconfig/build files and UML driver subset covering channels, consoles, management console, COW/UBD storage, host audio, watchdog, RTC, random, and vector networking. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Kconfig -->
# sources/distributed-fs/ceph-client/arch/um/Kconfig

Purpose: defines the top-level User-Mode Linux architecture configuration menu. It declares UML as the active architecture, selects generic kernel capabilities, exposes UML-specific memory, SMP, static-linking, hostfs, management-console, SysRq, stack, page-table, time-travel, KASAN-shadow, suspend, and power-management options, and includes subarchitecture and driver Kconfig fragments.

Important APIs/types/functions: this is Kconfig metadata rather than C code. Important symbols are `UML`, `MMU`, `UML_DMA_EMULATION`, `NO_IOMEM`, `UML_IOMEM_EMULATION`, `STATIC_LINK`, `LD_SCRIPT_*`, `HOSTFS`, `MCONSOLE`, `MAGIC_SYSRQ`, `KERNEL_STACK_ORDER`, `UML_TIME_TRAVEL_SUPPORT`, `UML_MAX_USERSPACE_ITERATIONS`, and `KASAN_SHADOW_OFFSET`.

Control flow: Kconfig evaluation starts by enabling `UML` and its selected generic features, imports `arch/$(HEADER_ARCH)/um/Kconfig`, then exposes user-visible options. The file finally sources `arch/um/drivers/Kconfig`, marks suspend possible when not SMP, and includes `kernel/power/Kconfig`.

State and persistence: selected symbols persist in `.config` and generated autoconf headers. They control compile-time inclusion of drivers, memory emulation, link mode, time-travel hooks, and exported kernel features, but no runtime state is stored here.

Dependencies and integration points: integrates with arch-specific `HEADER_ARCH` Kconfig, generic TTY, procfs, power management, KASAN, LTO, Rust, syscall tracing, seccomp, hostfs, and UML drivers. `MCONSOLE` gates management console code; `UML_TIME_TRAVEL_SUPPORT` affects channels and RTC behavior; `STATIC_LINK` affects Makefile link flags and KASAN choices.

Risks: Kconfig selects are architectural ABI and build-contract knobs. Incorrect `select` or dependency changes can silently enable generic code UML cannot support. Time-travel is deliberately incompatible with SMP; static linking can conflict with runtime-loaded host dependencies; `NO_DMA` must stay disabled when UML DMA emulation is required.

Test signals: all relevant defconfigs should resolve without dependency warnings, UML should build both 32-bit and 64-bit where supported, static/dynamic link variants should link, `mconsole`/hostfs/time-travel options should include or exclude expected objects, and `make olddefconfig` should keep stable defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Makefile -->
# sources/distributed-fs/ceph-client/arch/um/Makefile

Purpose: supplies the architecture Makefile glue for building a UML kernel binary. It chooses the default config, maps `SUBARCH` to `HEADER_ARCH`, includes subarchitecture and SKAS make fragments, prepares UML-specific include paths and defines, separates kernel-space and host-user C flags, configures linker flags, and creates the legacy `linux` hard link to `vmlinux`.

Important APIs/types/functions: important variables are `KBUILD_DEFCONFIG`, `ARCH_DIR`, `HEADER_ARCH`, `HOST_DIR`, `ARCH_INCLUDE`, `MODE_INCLUDE`, `KBUILD_CFLAGS`, `USER_CFLAGS`, `KERNEL_DEFINES`, `LINK-*`, `LINK_WRAPS`, `LDFLAGS_EXECSTACK`, `CFLAGS_vmlinux`, `CFLAGS_NO_HARDENING`, and exported `HEADER_ARCH SUBARCH USER_CFLAGS CFLAGS_NO_HARDENING DEV_NULL_PATH`.

Control flow: the top-level kbuild includes this file, it selects a defconfig based on `SUBARCH` and host `uname -m`, includes `Makefile-skas`, `$(HOST_DIR)/Makefile.um`, and `Makefile-os-Linux`, then defines `linux`, `archheaders`, `archprepare`, and cleanup targets. Link mode is derived from `CONFIG_LD_SCRIPT_STATIC`, `CONFIG_LD_SCRIPT_DYN`, and `CONFIG_LD_SCRIPT_DYN_RPATH`.

State and persistence: generated outputs are build artifacts: `vmlinux`, `linux`, generated arch headers, gcov files, and make variables exported to sub-makes. It does not define runtime state.

Dependencies and integration points: depends on bash, host architecture make fragments, shared UML headers, OS-Linux build rules, kbuild's link-vmlinux support, binutils/ld features, LTO flags, and libc symbol-renaming workarounds. `USER_CFLAGS` is consumed by user-mode helper objects in `arch/um/drivers`.

Risks: incorrect filtering between `KBUILD_CFLAGS` and `USER_CFLAGS` can leak kernel-only defines into host helper code or vice versa. Symbol remapping such as `strrchr=kernel_strrchr` and `errno=kernel_errno` prevents libc/kernel collisions; removing it can break links. Static/dynamic link flags are sensitive to toolchain changes.

Test signals: build UML for x86/i386/x86_64 subarchitectures, verify user objects compile with host headers, run `make linux`, inspect `CFLAGS_vmlinux` under static and dynamic configs, run clean/mrproper, and validate no libc symbol conflicts appear at link time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Kconfig -->
# sources/distributed-fs/ceph-client/arch/um/drivers/Kconfig

Purpose: declares UML driver configuration options for character channels, consoles, sound, vector networking, virtio/vhost-user, RTC wakeup, and PCI emulation/passthrough. It determines which channel backends and device families are compiled into the UML architecture driver directory.

Important APIs/types/functions: key symbols are `STDERR_CONSOLE`, `SSL`, `NULL_CHAN`, `PORT_CHAN`, `PTY_CHAN`, `TTY_CHAN`, `XTERM_CHAN`, `XTERM_CHAN_DEFAULT_EMULATOR`, `NOCONFIG_CHAN`, `CON_ZERO_CHAN`, `CON_CHAN`, `SSL_CHAN`, `UML_SOUND`, `UML_NET_VECTOR`, `VIRTIO_UML`, `UML_RTC`, `UML_PCI`, `UML_PCI_OVER_VIRTIO`, `UML_PCI_OVER_VIRTIO_DEVICE_ID`, and `UML_PCI_OVER_VFIO`.

Control flow: Kconfig presents character-device options first, derives `NOCONFIG_CHAN` when any channel backend is absent, sets default command-line channel strings, then exposes network and virtio/PCI/RTC options with dependencies and selects.

State and persistence: selections persist in `.config` and control object inclusion in `drivers/Makefile`. Default strings become compiled-in defaults used by `stdio_console.c` and `ssl.c`.

Dependencies and integration points: integrates with generic `NET`, `SOUND`, `SOUND_OSS_CORE`, `VIRTIO`, `RTC_CLASS`, `PM_SLEEP`, PCI/MSI helpers, UML I/O memory and DMA emulation, and runtime dependency handling through `MAY_HAVE_RUNTIME_DEPS`.

Risks: channel defaults can reference a backend configured out of the build, causing runtime `not_configged_ops` failures. `UML_NET_VECTOR` depends on host kernel/libc capabilities and runtime components. `UML_RTC` is intentionally tied to suspend/time-travel usefulness.

Test signals: build matrix with each channel enabled/disabled, boot with `con=` and `ssl=` defaults, verify missing backends report clear errors, exercise vector network config parsing, and validate virtio/PCI options select required lower-level support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Makefile -->
# sources/distributed-fs/ceph-client/arch/um/drivers/Makefile

Purpose: maps UML driver Kconfig symbols to compiled objects and object groups. It composes multi-object drivers such as vector networking, management console, hostaudio, UBD, port channel, watchdog, RTC, and VFIO, and marks user-mode helper objects for special UML build rules.

Important APIs/types/functions: important object groups are `vector-objs`, `mconsole-objs`, `hostaudio-objs`, `ubd-objs`, `port-objs`, `harddog-objs`, `rtc-objs`, and `vfio_uml-objs`. Important selectors are `obj-y`, `obj-$(CONFIG_*)`, `harddog-builtin-*`, `USER_OBJS`, `CFLAGS_null.o`, and `CFLAGS_xterm.o`.

Control flow: kbuild always builds the stdio console, fd channel, channel core, channel user helpers, and line core. Optional Kconfig symbols append backend and device objects. `USER_OBJS` lets `arch/um/scripts/Makefile.rules` build selected files with `USER_CFLAGS` because they call host libc/syscalls.

State and persistence: no runtime state; output is object composition in the build tree.

Dependencies and integration points: depends on the top-level UML Makefile for `USER_CFLAGS` and `DEV_NULL_PATH`, on channel symbols from `drivers/Kconfig`, and on block/watchdog/random symbols defined in generic subsystem Kconfig files.

Risks: placing a host-helper file outside `USER_OBJS` can compile it with kernel flags and break libc/syscall assumptions. Multi-object grouping must match exported symbols, especially `harddog_user_exp.o` for module builds and `cow_user.o` for common COW parsing.

Test signals: inspect `make V=1 arch/um/drivers/` compile commands, build all listed Kconfig combinations, verify user objects receive host flags, and ensure no unresolved symbols appear when optional drivers are modular or built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan.h

Purpose: declares the kernel-side UML channel abstraction used by virtual consoles and serial lines. A channel joins a `struct line` TTY endpoint to one host-side backend such as fd, null, port, pty, tty, or xterm.

Important APIs/types/functions: `struct chan` stores list membership, owning `line`, device string, primary/input/output/opened/enabled flags, input/output FDs, backend `chan_ops`, and backend-private data. Exported functions include `parse_chan_pair()`, `enable_chan()`, `close_chan()`, `deactivate_chan()`, `write_chan()`, `console_write_chan()`, `console_open_chan()`, `chan_interrupt()`, `chan_enable_winch()`, `chan_window_size()`, and `chan_config_string()`.

Control flow: users do not call backend operations directly; `line.c` calls the channel API, and `chan_kern.c` dispatches through `chan_ops` while managing IRQs and file descriptor lifecycle.

State and persistence: channel state is per-line runtime state. It tracks opened host FDs and parsed configuration strings but has no persistence beyond boot command-line or mconsole reconfiguration.

Dependencies and integration points: depends on Linux TTY/console/list APIs, `chan_user.h` backend operations, and `line.h`. It is used by stdio console and software serial drivers.

Risks: the same backend FD can be input and output or split across two channels, so close order and primary-channel semantics matter. Fields are bitflags with lifecycle-sensitive transitions.

Test signals: compile all channel backends, boot with single and split `con=`/`ssl=` channel pairs, reconfigure via mconsole, and verify hangup/window-size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan_kern.c

Purpose: implements the kernel-side channel core for UML TTY devices. It parses backend strings, opens host descriptors, installs read/write IRQs, routes input bytes into TTY flip buffers, writes console/TTY output, handles window-change setup, and tears down disappearing interrupt sources safely.

Important APIs/types/functions: key functions are `open_one_chan()`, `enable_chan()`, `free_irqs()`, `close_one_chan()`, `close_chan()`, `write_chan()`, `console_write_chan()`, `console_open_chan()`, `chan_window_size()`, `chan_config_string()`, `parse_chan()`, `parse_chan_pair()`, and `chan_interrupt()`. `struct chan_type` maps backend names to `fd_ops`, `null_ops`, `port_ops`, `pty_ops`, `pts_ops`, `tty_ops`, `xterm_ops`, or `not_configged_ops`.

Control flow: `parse_chan_pair()` replaces any existing channel list, splitting `input,output` strings or using one backend for both directions. `enable_chan()` opens each channel, sets nonblocking input, optionally duplicates output as blocking in time-travel external/infinite-CPU modes, and requests UML read/write IRQs. Read IRQs call `chan_interrupt()`, which drains bytes until EAGAIN/EIO, inserts them into the TTY flip buffer, schedules retry work if the flip buffer is full, and hangs up/defers IRQ freeing on EOF. Writes go through the active output channel and return only the primary channel result.

State and persistence: per-channel runtime state includes host FDs, enabled/opened flags, backend data, and line membership. `irqs_to_free` is a global deferred-free list for IRQ cleanup that cannot happen in IRQ context. No disk state is written.

Dependencies and integration points: depends on UML IRQ allocation/freeing, `os_*` host FD helpers, `time_travel_mode`, Linux TTY flip buffers, delayed work, and backend `chan_ops`. It is driven by `line.c`, `stdio_console.c`, and `ssl.c`.

Risks: close paths run from both process and interrupt contexts; freeing IRQs immediately in the wrong context can crash. Time-travel blocking-output mode deliberately avoids output IRQs and changes FD semantics. Bad parser lifetime handling can free strings still referenced by backend `dev` pointers.

Test signals: boot with `fd`, `null`, `port`, `pty/pts`, `tty`, and configured-out channels; exercise split input/output pairs; close host endpoints to trigger hangups; fill TTY flip buffers; run time-travel modes; and use mconsole config/get_config/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.c

Purpose: provides host-user helper routines shared by UML channel backends. It wraps read/write/close/window-size operations and implements SIGWINCH relay support for host TTYs attached to UML consoles.

Important APIs/types/functions: exported helpers are `generic_close()`, `generic_read()`, `generic_write()`, `generic_window_size()`, `generic_free()`, `generic_console_write()`, and `register_winch()`. Internal SIGWINCH support uses `winch_handler()`, `struct winch_data`, `winch_thread()`, and `winch_tramp()`.

Control flow: generic reads return a positive byte count, zero for EAGAIN, `-EIO` on EOF, or `-errno`. Writes retry interrupted short writes and distinguish EAGAIN/EOF/errors. Console writes temporarily enable terminal output processing so newline output behaves as users expect, then restore raw terminal state. `register_winch()` detects host TTYs, either uses existing SKAS winch handling or starts a helper thread with a controlling TTY; that thread waits in `sigsuspend()` for SIGWINCH and writes a byte to a pipe registered as a UML IRQ.

State and persistence: state is per-call except helper thread pipe FDs, helper pid, and stack passed to `line.c` through `register_winch_irq()`. Terminal attributes are saved and restored per backend.

Dependencies and integration points: depends on libc/syscalls, `termios`, `TIOCGWINSZ`, UML helper-thread APIs, signal masking, `os_*` wrappers, and `line.c` WINCH IRQ handling.

Risks: helper threads use host process/session/controlling-terminal semantics and synchronization pipes rather than kernel locks. Terminal state restoration must survive errors. `generic_write()` must handle blocking FDs used by time-travel output without losing short writes.

Test signals: attach consoles to host TTYs, resize terminal windows and watch guest SIGWINCH delivery, test raw-mode restoration on close/errors, verify EAGAIN and EOF mapping, and run console writes to ensure newline handling is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.h

Purpose: defines the host-side channel backend interface and shared option structure. It is the contract between kernel channel management in `chan_kern.c` and individual host descriptor backends.

Important APIs/types/functions: `struct chan_opts` carries an announce callback, xterm title, and raw-mode flag. `struct chan_ops` supplies backend type, init/open/close/read/write/console_write/window_size/free callbacks, and a `winch` capability flag. It declares backend ops objects and generic helper functions.

Control flow: backend code populates one `chan_ops` instance. `chan_kern.c` parses backend names and calls `init`, `open`, I/O callbacks, and `free`; `line.c` asks `register_winch_irq()` to translate window-change pipe events into guest signals.

State and persistence: the header owns no state. Backend-private state is opaque `void *` returned from `init`.

Dependencies and integration points: includes UML init and Linux types, forward-declares `tty_port`, and integrates with `__uml_help` through `__channel_help()`.

Risks: callback prototypes must stay synchronized across all backends. The `type` string is exposed in `mconsole config` query output. Backends that claim `winch` must provide FDs valid for TTY window handling.

Test signals: build every backend, verify parser accepts each declared `type`, query config strings through mconsole, and compile with backends excluded so declarations still match fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/cow.h

Purpose: declares the UML COW disk-image format helpers used by the UBD block driver. The helpers create, read, and size copy-on-write image headers and bitmap/data regions.

Important APIs/types/functions: exported functions are `init_cow_file()`, `file_reader()`, `read_cow_header()`, `write_cow_header()`, and `cow_sizes()`. The API returns backing-file path, mtime, virtual size, sector size, alignment, bitmap offset/length, and data offset.

Control flow: UBD calls `read_cow_header()` to detect COW images and validate backing files, `write_cow_header()` when switching or creating COW files, and `cow_sizes()` to compute bitmap/data placement.

State and persistence: this header describes persistent COW-image metadata stored in host files, but owns no state itself.

Dependencies and integration points: depends on `asm/types.h` and COW implementation in `cow_user.c`; UBD uses it for COW-backed block devices.

Risks: function signatures are part of the storage driver's internal ABI. Type sizes and endian assumptions must match the on-disk COW format implementation.

Test signals: compile UBD with COW enabled, create/read COW images, validate bitmap/data offsets, and exercise old COW header versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_sys.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/cow_sys.h

Purpose: adapts generic COW image code to UML kernel/host helper services. It provides allocation, logging, string duplication, seek, size, and write wrappers used by `cow_user.c`.

Important APIs/types/functions: inline helpers are `cow_malloc()`, `cow_free()`, `cow_strdup()`, `cow_seek_file()`, `cow_file_size()`, and `cow_write_file()`. `cow_printf` maps to `printk`.

Control flow: COW code calls these wrappers instead of directly using allocator or OS helpers, keeping `cow_user.c` portable across UML build contexts.

State and persistence: no state is owned here; helper calls may query or write host files through `os_*` functions.

Dependencies and integration points: depends on `kern_util.h`, `os.h`, and `um_malloc.h`. It bridges the user-flavored COW code to UML kernel logging and memory helpers.

Risks: wrapper behavior affects storage image creation and parsing. Allocation flags must be safe in the call contexts where UBD opens/configures devices.

Test signals: compile COW helpers, run COW image create/read paths, and fault-inject allocation or host file size/seek/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/cow_user.c

Purpose: implements UML COW disk-image header creation and parsing for UBD. It supports historical COW header versions, endian conversion, backing-file validation data, bitmap/data layout computation, and initialization of sparse COW image files.

Important APIs/types/functions: persistent structures are `cow_header_v1`, `cow_header_v2`, `cow_header_v3`, broken 64-bit `cow_header_v3_broken`, and `union cow_header`. Public functions are `cow_sizes()`, `write_cow_header()`, `file_reader()`, `read_cow_header()`, and `init_cow_file()`. `absolutize()` canonicalizes backing-file paths.

Control flow: `write_cow_header()` seeks to offset 0, allocates a v3 header, stores magic/version/backing path/mtime/size/sectorsize/alignment/cow_format in big-endian form, and writes it. `read_cow_header()` reads a full union, detects native or big-endian magic, dispatches version 1/2/3/broken-v3 layouts, computes offsets, and duplicates the backing path. `init_cow_file()` writes the header, calculates bitmap/data offsets, seeks to the final byte of the virtual data area, and writes one zero byte to size the sparse image.

State and persistence: state is host-file persistent COW metadata plus zeroed bitmap/data extents. No global runtime state exists.

Dependencies and integration points: depends on libc `pread`, endian helpers, UML COW system wrappers, `os_file_modtime()`, and UBD's COW open/read/write path.

Risks: this is an on-disk format compatibility surface. Incorrect packing, endian conversion, broken-v3 detection, or path canonicalization can make old images unreadable or point at the wrong backing file. `absolutize()` temporarily changes cwd and must restore it.

Test signals: create v3 COW files, read v1/v2/v3 and broken-v3 fixtures, verify backing-file path/mtime/size mismatch detection in UBD, test long path rejection, sparse EOF sizing, sector/alignment variations, and host endian portability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/fd.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/fd.c

Purpose: implements the `fd:` UML channel backend, attaching a console or serial line to an already-open host file descriptor.

Important APIs/types/functions: `struct fd_chan` stores the host FD, raw-mode flag, saved terminal attributes, and printable FD string. Backend callbacks are `fd_init()`, `fd_open()`, and `fd_close()`, exported through `fd_ops`.

Control flow: `fd_init()` requires `:number` syntax and records the descriptor. `fd_open()` optionally switches terminal FDs to raw mode, formats the descriptor for config output, and returns the existing FD. `fd_close()` restores saved terminal attributes if raw mode was enabled on a TTY.

State and persistence: state is backend-private and lives as long as the channel configuration. It does not own the underlying FD lifetime in the normal sense; it merely uses the descriptor supplied by the UML process environment.

Dependencies and integration points: uses generic channel I/O helpers, libc `isatty`, termios, and UML `raw()` helper. `winch=1` lets line code register window-size notifications for TTY descriptors.

Risks: using process-standard FDs means close/restore semantics can affect the host terminal running UML. Invalid FD numbers fail only when used. Raw-mode restoration must be reliable.

Test signals: boot with `con0=fd:0,fd:1`, use raw/non-raw modes, close stdin/stdout externally, resize the terminal, and verify config strings report numeric FDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog.h

Purpose: declares the host-side helper interface for the UML watchdog driver.

Important APIs/types/functions: exported prototypes are `start_watchdog()`, `stop_watchdog()`, and `ping_watchdog()`.

Control flow: kernel watchdog file operations call these functions to spawn `/usr/bin/uml_watchdog`, stop it, and send keepalive bytes.

State and persistence: no state is defined in the header. FDs and helper process IDs are tracked by the C files.

Dependencies and integration points: connects `harddog_kern.c` to `harddog_user.c`, and optionally exports symbols through `harddog_user_exp.c` for module builds.

Risks: prototype mismatch would break the kernel/user helper boundary. The functions are part of the small internal ABI between watchdog halves.

Test signals: build built-in and modular watchdog configurations and exercise open/write/ioctl/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog_kern.c

Purpose: implements the UML `/dev/watchdog` misc driver. It presents the Linux watchdog character-device ABI and delegates actual timeout enforcement to the host `uml_watchdog` helper.

Important APIs/types/functions: file operations are `harddog_open()`, `harddog_release()`, `harddog_write()`, `harddog_ioctl_unlocked()`, and mutex-wrapped `harddog_ioctl()`. Global state includes `timer_alive`, `harddog_in_fd`, `harddog_out_fd`, `harddog_mutex`, and `lock`. `harddog_miscdev` registers minor `WATCHDOG_MINOR`.

Control flow: open enforces single-open, optionally obtains the mconsole notify socket, starts the watchdog helper, and records FDs. Writes and `WDIOC_KEEPALIVE` call `ping_watchdog()`. Release closes both helper pipes through `stop_watchdog()` and marks the timer inactive. Ioctl supports `WDIOC_GETSUPPORT`, status/bootstatus zero, and keepalive.

State and persistence: runtime state is global watchdog open state and host pipe FDs. No persistent watchdog settings are stored; timeout is handled externally by the helper.

Dependencies and integration points: depends on miscdevice/watchdog ABI, mconsole notification when available, module nowayout behavior, and host functions from `harddog_user.c`.

Risks: locking combines a mutex and spinlock around single-open and FD state. `CONFIG_WATCHDOG_NOWAYOUT` takes a module reference but release still calls stop, so behavior should be checked against expected nowayout semantics. Helper startup failure must leave state clean.

Test signals: open exclusivity, keepalive writes, ioctl support/status, helper missing/failing cases, close behavior, mconsole notify socket mode, and modular unload with active watchdog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user.c

Purpose: starts and communicates with the host-side `uml_watchdog` helper process for the UML watchdog device.

Important APIs/types/functions: `struct dog_data` carries pipe FDs into `pre_exec()`. Public functions are `start_watchdog()`, `stop_watchdog()`, and `ping_watchdog()`.

Control flow: `start_watchdog()` creates two pipes, wires helper stdin/stdout/stderr in `pre_exec()`, chooses either `-mconsole <socket>` or `-pid <uml-pid>` arguments, runs `/usr/bin/uml_watchdog`, closes unused pipe ends, waits for an initial byte from the helper, and returns input/output FDs to the kernel side. `ping_watchdog()` writes a newline keepalive. `stop_watchdog()` closes both FDs.

State and persistence: only pipe FDs and helper process lifetime are involved. No persistent data is stored.

Dependencies and integration points: depends on UML `os_pipe()`, `run_helper()`, `helper_wait()`, `os_getpid()`, and host executable `/usr/bin/uml_watchdog`.

Risks: helper path is hard-coded. The PID mode comment notes `os_getpid()` is not SMP-correct. Startup synchronization treats EOF and read errors as fatal. File descriptor wiring must avoid leaking unused pipe ends.

Test signals: run with helper installed/missing, with and without mconsole socket, validate startup byte handshake, send repeated keepalives, terminate helper early, and confirm pipe cleanup on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user_exp.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user_exp.c

Purpose: conditionally exports the host-watchdog helper symbols when the UML watchdog is built as a module.

Important APIs/types/functions: uses `EXPORT_SYMBOL()` for `start_watchdog`, `stop_watchdog`, and `ping_watchdog` under `IS_MODULE(CONFIG_UML_WATCHDOG)`.

Control flow: there is no runtime control flow beyond module symbol export generation.

State and persistence: no state is owned.

Dependencies and integration points: depends on Linux export macros and `harddog.h`. It lets modular `harddog_kern.o` resolve helper functions that may be built into the UML image.

Risks: missing exports break modular watchdog builds; unconditional exports could expose unnecessary symbols in built-in configurations.

Test signals: build `CONFIG_UML_WATCHDOG=m` and `=y`, inspect module symbol resolution, and load/unload the watchdog module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user_exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/hostaudio_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/hostaudio_kern.c

Purpose: implements UML OSS sound relay devices that proxy guest DSP and mixer operations to host audio device files.

Important APIs/types/functions: state structs are `hostaudio_state` and `hostmixer_state`. Module parameters and boot options configure `dsp` and `mixer`. DSP operations include `hostaudio_read()`, `hostaudio_write()`, `hostaudio_poll()`, `hostaudio_ioctl()`, `hostaudio_open()`, and `hostaudio_release()`. Mixer operations include `hostmixer_ioctl_mixdev()`, `hostmixer_open_mixdev()`, and `hostmixer_release()`.

Control flow: module init registers OSS DSP and mixer devices. Opening a guest audio node opens the configured host path with matching read/write flags. Reads allocate a kernel buffer, read from host, and copy to user. Writes duplicate user data and write it to host. Selected DSP ioctls copy integer arguments through a local variable before forwarding to the host FD; mixer ioctls are forwarded directly.

State and persistence: global `dsp` and `mixer` paths persist for the module lifetime. Each open file stores a host FD in `private_data`. No audio data is persisted by the driver.

Dependencies and integration points: depends on OSS sound registration APIs, UML host `os_open_file`, `os_read_file`, `os_write_file`, `os_ioctl_generic`, kernel parameter locking, and host `/dev/sound/dsp`/`mixer` or configured equivalents.

Risks: OSS interfaces are legacy and host device availability varies. `hostmixer_open_mixdev()` allocates `state` but does not assign `state->fd` before storing `private_data`, which is a correctness risk for ioctl/release. Poll is unimplemented. Large reads/writes allocate buffers proportional to user count.

Test signals: module load/unload, open/read/write DSP, supported DSP ioctls, mixer open/ioctl/release, invalid host paths, concurrent opens while changing module parameters, and large I/O allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/hostaudio_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/line.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/line.c

Purpose: implements shared TTY line management for UML virtual consoles and software serial lines. It handles TTY registration/open/close, channel activation, buffering, IRQ setup, write draining, mconsole configuration, and SIGWINCH delivery.

Important APIs/types/functions: exported functions include `line_open()`, `line_install()`, `line_close()`, `line_hangup()`, `line_write()`, `line_write_room()`, `line_chars_in_buffer()`, `line_flush_buffer()`, `line_flush_chars()`, `line_throttle()`, `line_unthrottle()`, `line_setup_irq()`, `register_lines()`, `setup_one_line()`, `line_setup()`, `line_config()`, `line_get_config()`, `line_id()`, `line_remove()`, `close_lines()`, `register_winch_irq()`, and `add_xterm_umid()`.

Control flow: TTY open calls `tty_port_open()`, whose activation enables channels, sets IRQs, registers winch handling, and reads initial window size. Writes either go directly to the output channel or enter a 4 KiB ring buffer; write IRQs call `flush_buffer()` and wake the TTY. Input IRQs are installed by `line_setup_irq()` and handled through `chan_interrupt()`. Configuration functions parse boot/mconsole strings, register/unregister TTY devices, and rebuild channel pairs.

State and persistence: each `struct line` owns `tty_port`, validity, IRQ numbers, channel list, input/output channel pointers, spinlock, throttle flag, lazy ring buffer, SIGWINCH flag, delayed work, and driver pointer. A global `winch_handlers` list tracks helper FDs/pids/stacks.

Dependencies and integration points: depends on Linux TTY core, UML IRQs, channel core, mconsole device registration, workqueues, pgrp signaling, and host process cleanup helpers.

Risks: ring-buffer logic is hand-rolled and lock-sensitive. Winch unregistering uses tty references and process cleanup; leaks or double frees can happen if close and IRQ failure race. `setup_one_line()` changes live device registration and must reject open devices.

Test signals: TTY open/close/hangup, heavy output causing buffering and write IRQs, throttle/unthrottle input, mconsole config/remove/query, terminal resize propagation, xterm title with UMID, and backend disconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/line.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/line.h

Purpose: declares the shared UML TTY line structures and operations used by console and serial drivers.

Important APIs/types/functions: `struct line_driver` defines static driver identity, device name, major/minor, TTY type/subtype, IRQ names, mconsole device, and registered `tty_driver`. `struct line` stores per-line TTY port, validity, IRQs, init string, channel list, channel pointers, lock, throttled flag, ring-buffer pointers, SIGWINCH state, delayed work, and owning driver.

Control flow: the header supplies prototypes for TTY operations, setup/config/remove helpers, IRQ setup, channel close, driver registration, and xterm title augmentation.

State and persistence: no state is instantiated here, but the structs define runtime state layout for console and serial arrays.

Dependencies and integration points: depends on Linux list/workqueue/TTY/interrupt/spinlock/mutex APIs, `chan_user.h`, and `mconsole_kern.h`.

Risks: structure fields are shared by several C files; changing layout or semantics affects channel activation, buffering, and mconsole config. The buffer comments note a future kfifo replacement but current callers depend on raw pointers.

Test signals: compile users of all declared functions, register both console and serial line drivers, and exercise per-line state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/line.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole.h

Purpose: defines the UML management-console wire protocol and shared request/reply structures used by kernel and host-side mconsole code.

Important APIs/types/functions: protocol constants are `MCONSOLE_MAGIC`, `MCONSOLE_MAX_DATA`, and `MCONSOLE_VERSION`. Wire structs are `mconsole_request`, `mconsole_reply`, and `mconsole_notify`. Internal structs are `mconsole_command` and `mc_request`; `enum mc_context` distinguishes interrupt-context and process-context handlers. It declares command handlers and request/reply/notify functions.

Control flow: `mconsole_user.c` parses datagrams into `mc_request` and dispatch metadata; `mconsole_kern.c` executes handlers and uses reply helpers.

State and persistence: no state is defined here except the external `mconsole_socket_name`. The protocol is runtime IPC over Unix datagram sockets.

Dependencies and integration points: includes host `stdint.h` when building user-side code and UML ptrace register definitions for captured IRQ register state.

Risks: this header defines a compatibility protocol. Changing sizes, magic, version, or enum values can break `uml_mconsole` clients and boot notifications.

Test signals: send valid/invalid versioned datagrams, oversized requests, notifications, and command replies split across multiple packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.c

Purpose: implements the kernel-side UML management console. It creates the control socket, handles mconsole commands, supports dynamic device configuration/removal, memory plug/unplug, proc reads, SysRq/stack/log/control operations, console-output streaming, boot/panic/user notifications, and socket cleanup.

Important APIs/types/functions: command handlers include `mconsole_version()`, `mconsole_log()`, `mconsole_proc()`, `mconsole_help()`, `mconsole_halt()`, `mconsole_reboot()`, `mconsole_cad()`, `mconsole_stop()`, `mconsole_go()`, `mconsole_config()`, `mconsole_remove()`, `mconsole_sysrq()`, and `mconsole_stack()`. Device registration uses `mconsole_register_dev()` and `struct mc_device`. Init paths include `mem_mc_init()`, `mc_add_console()`, `mconsole_init()`, `create_proc_mconsole()`, and panic notifier setup.

Control flow: the mconsole Unix socket is registered as a UML IRQ. `mconsole_interrupt()` drains requests; interrupt-safe commands run immediately, while process-context commands are copied into `mc_requests` and processed by `mc_work_proc()`. Config/remove locate registered `mc_device` entries and call their callbacks. `mconsole_stop()` blocks signals and synchronously loops on the socket until `go`. Notifications send datagrams to an optional `mconsole=notify:<socket>` target.

State and persistence: runtime globals include proc mount, request queue, registered mconsole devices, unplugged-memory page lists/counts, console streaming clients, notify socket string and socket FD, and mconsole socket path. No state is persisted beyond the host socket file, which is unlinked on reboot.

Dependencies and integration points: depends on UML IRQ/user socket helpers, procfs mounting/reading, reboot and panic notifiers, workqueues, console subsystem, SysRq, task lookup/stack dump, memory dropping support, and mconsole user protocol.

Risks: this is a privileged control plane. Command context classification matters because some operations cannot run in IRQ context. `proc` reads expose guest `/proc` data to the host-side mconsole client. Memory unplug stores dropped pages in custom lists and must keep accounting consistent. Socket cleanup and notification locking must avoid stale paths and races.

Test signals: run `uml_mconsole version/help/config/remove/sysrq/proc/stack/log/stop/go/halt/reboot`, boot with notify socket, panic notification, memory plug/unplug if supported, dynamic console/ubd/vector config through registered devices, and malformed datagrams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.h

Purpose: declares the kernel-side management-console device registration interface and helper macro for config-string assembly.

Important APIs/types/functions: `struct mconsole_entry` wraps a list node and copied `mc_request`. `struct mc_device` defines configurable device callbacks: `config`, `get_config`, `id`, and `remove`. `CONFIG_CHUNK()` appends config fragments while tracking required output size. `mconsole_register_dev()` is real when `CONFIG_MCONSOLE` is enabled and a stub otherwise.

Control flow: drivers such as line, UBD, and vector networking register `mc_device` instances; `mconsole_kern.c` later dispatches config/remove requests to them.

State and persistence: no state is instantiated here, but it defines the callback contract for runtime mconsole reconfiguration.

Dependencies and integration points: depends on Linux lists and `mconsole.h`. Used by console, serial, UBD, vector, and memory config code.

Risks: `CONFIG_CHUNK()` deliberately returns required size even when the destination buffer is too small; callers must honor that contract. Callback contexts are process-context according to the comment.

Test signals: compile with and without `CONFIG_MCONSOLE`, query config strings that require buffer growth, and exercise all registered device callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_user.c

Purpose: implements host/user-side management-console protocol parsing, reply sending, notification sending, and socket unlinking for UML.

Important APIs/types/functions: `commands[]` maps command prefixes to handlers and context. Public functions are `mconsole_get_request()`, `mconsole_reply_len()`, `mconsole_reply()`, `mconsole_unlink_socket()`, and `mconsole_notify()`. Internal helpers are `mconsole_reply_v0()` and `mconsole_parse()`.

Control flow: `mconsole_get_request()` receives a datagram, records sender address, rejects legacy unversioned clients, checks size and version, NUL-terminates payload, and finds a command. Reply helpers split large output into protocol-sized packets with `err` only on the first packet and `more` markers. `mconsole_notify()` lazily opens a Unix datagram socket, builds a notification packet, and sends it to the configured path under notify locking.

State and persistence: global `mconsole_socket_name` holds the bound control socket path, and static `notify_sock` caches the notification socket FD. `mconsole_unlink_socket()` removes the host socket path.

Dependencies and integration points: depends on Unix datagram sockets, `sendto`/`recvfrom`, command handlers in `mconsole_kern.c`, and notify locks provided by kernel-side code.

Risks: command matching is prefix-based, so ambiguous prefixes must be avoided. `strcpy(target.sun_path, sock_name)` assumes the path fits `sockaddr_un`. Legacy version-0 clients are explicitly unsupported.

Test signals: send each command over a Unix datagram socket, oversized request rejection, bad magic/version handling, multi-packet replies, boot/panic/user notifications, and socket unlink on reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/null.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/null.c

Purpose: implements the `null` UML channel backend, providing a console/serial endpoint similar to `/dev/null`.

Important APIs/types/functions: `null_init()`, `null_open()`, `null_read()`, `null_free()`, and `null_ops`.

Control flow: initialization returns a unique static token. Open opens the configured host `DEV_NULL` path read/write and reports no device string. Reads always return `-ENODEV`; writes use the generic write path and disappear into the null device.

State and persistence: no per-channel allocated state is used. Host `/dev/null` has no persisted output.

Dependencies and integration points: depends on `DEV_NULL` from Makefile-provided `DEV_NULL_PATH`, generic channel helpers, and host `open()`.

Risks: read side intentionally never produces input, so attaching an interactive console to `null` can make it unusable. Build-time `DEV_NULL` must be valid for the host platform.

Test signals: boot with `con1=null`, verify output is discarded, reads fail cleanly, and mconsole config reports null/empty device details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/port.h

Purpose: declares kernel/user functions for the UML `port:` channel backend, which accepts host TCP/telnet connections and binds them to waiting UML lines.

Important APIs/types/functions: prototypes include `port_data()`, `port_wait()`, `port_kern_close()`, `port_connection()`, `port_listen_fd()`, `port_read()`, `port_kern_free()`, `port_rcv_fd()`, and `port_remove_dev()`.

Control flow: kernel-side code allocates/listens/waits through `port_kern.c`; user-side code opens TCP sockets and helper processes through `port_user.c`.

State and persistence: no state is owned here. Runtime state is in `port_list`, `port_dev`, and `connection` objects in implementation files.

Dependencies and integration points: bridges `port_user.c` and `port_kern.c`, and is used by the `port_ops` channel backend.

Risks: the header includes some historical declarations not implemented in the researched files, so changes should confirm actual users before removing them.

Test signals: compile port backend and boot `con=port:<n>` or `ssl=port:<n>`, then connect with telnet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/port_kern.c

Purpose: implements the kernel-side listener and connection queue for UML `port:` channels. It accepts host TCP connections, starts telnet helper handoff, queues completed connections, and wakes UML line openers waiting for a connection.

Important APIs/types/functions: main structs are `port_list`, `port_dev`, and `connection`. Key functions are `port_data()`, `port_wait()`, `port_remove_dev()`, `port_kern_free()`, `free_port()`, plus IRQ/work handlers `port_interrupt()`, `port_work_proc()`, `port_accept()`, and `pipe_interrupt()`.

Control flow: `port_data()` finds or creates a shared listener for a TCP port, registers an accept IRQ, and returns a per-device `port_dev`. Accept IRQs schedule work; work calls `port_accept()` until no more connections. A helper/telnetd pipe IRQ receives the connected FD and helper PID, moves the connection from pending to completed, and completes waiters. `port_wait()` waits interruptibly, consumes a completed connection, frees the helper IRQ, and returns the connected FD.

State and persistence: global `ports` stores listeners, each with wait count, pending/completed lists, completion, socket FD, and lock. Per-device state tracks helper/telnetd PIDs for cleanup. No persistent data is written.

Dependencies and integration points: depends on UML IRQs, completions, workqueues, host FD-passing helpers, `port_user.c`, and channel backend lifecycle.

Risks: list operations span IRQ, workqueue, and process contexts. Some connection-list manipulation relies on serialized paths and minimal locking. If no UML line waits, a telnet client receives a message but the connection is still queued/pending until helper completion. Cleanup must kill helper processes and free IRQs outside IRQ context.

Test signals: connect multiple telnet clients to one port, open/close UML lines, no-waiter behavior, helper failure, interrupted `port_wait()`, mconsole remove, and UML exit cleanup of listening sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/port_user.c

Purpose: implements the host-side `port:` channel backend. It parses TCP port numbers, opens listening sockets, accepts host connections, and starts `in.telnetd` with UML's port-helper.

Important APIs/types/functions: `struct port_chan` stores raw-mode flag, saved termios, kernel-side port data, and printable port string. Backend callbacks are `port_init()`, `port_open()`, `port_close()`, `port_free()`, and `port_ops`. Host helpers are `port_listen_fd()`, `port_pre_exec()`, and `port_connection()`.

Control flow: `port_init()` parses `:port`, obtains shared kernel listener state through `port_data()`, and stores channel data. `port_open()` waits for a completed port connection, optionally sets raw mode, and returns the connected FD. `port_connection()` accepts a TCP connection, verifies the helper executable from `UML_PORT_HELPER` or default `OS_LIB_PATH/uml/port-helper`, creates a pipe, runs `in.telnetd -L <helper>`, and returns the accepted FD plus helper PID.

State and persistence: listener and connection state is runtime-only; no data is persisted. Environment variable `UML_PORT_HELPER` influences helper path.

Dependencies and integration points: depends on TCP sockets, `in.telnetd`, UML port-helper, FD pipes, `run_helper()`, raw terminal helpers, and `port_kern.c` queueing.

Risks: external helper availability is mandatory for useful telnet sessions. Accepted sockets and helper pipes must be closed on all failure paths. Raw-mode saved termios is captured but close does not restore it directly because telnet sessions are helper-managed.

Test signals: bind port, connect with telnet, missing helper path, custom `UML_PORT_HELPER`, multiple waiting devices, raw/non-raw sessions, and port removal while helper processes exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/pty.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/pty.c

Purpose: implements UML `pty` and `pts` channel backends, allocating host pseudo-terminal masters for consoles and serial lines.

Important APIs/types/functions: `struct pty_chan` stores announce callback, device index, raw flag, saved terminal state, and device-name buffer. Backend callbacks are `pty_chan_init()`, `pts_open()`, `pty_open()`, and ops objects `pty_ops`/`pts_ops`. `getmaster()` scans legacy BSD pty devices.

Control flow: `pts_open()` obtains a Unix98 pty via `get_pty()`, optionally sets raw mode, records `ptsname()`, and announces it. `pty_open()` scans `/dev/pty[p-s][0-f]`, verifies the slave side is accessible, sets raw mode if requested, announces, and returns the master FD.

State and persistence: backend state is per-channel and stores only host terminal attributes/name. Host pty allocation is runtime-only.

Dependencies and integration points: depends on host pty APIs, termios/raw helpers, generic channel I/O, and line announce callbacks used by console/serial setup.

Risks: legacy pty scanning is host-distribution dependent. Device-name buffer sizing assumes limited pts path length. Raw-mode error paths must close allocated masters.

Test signals: boot with `con=pty`, `con=pts`, and `ssl=pty`; verify announced host devices work; test absence of legacy ptys; resize/input/output behavior; and raw mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/pty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/random.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/random.c

Purpose: registers a UML hardware RNG provider backed by the host `/dev/random`.

Important APIs/types/functions: global state is `random_fd`, `hwrng`, and completion `have_data`. Key functions are `rng_dev_read()`, `random_interrupt()`, `rng_init()`, `cleanup()`, and `rng_cleanup()`.

Control flow: init opens host `/dev/random`, registers a UML read IRQ on the FD, marks SIGIO broken, fills `hwrng.name/read`, and registers with the hwrng core. Reads call `os_read_file()`; blocking reads temporarily add the FD to SIGIO monitoring, wait for completion, remove monitoring, and deactivate the FD IRQ before retry/return. The IRQ handler completes the wait.

State and persistence: runtime state is the host random FD and hwrng registration. No entropy is persisted by this driver.

Dependencies and integration points: depends on hwrng core, UML IRQ/SIGIO helpers, host `/dev/random`, completions, and module/exitcall cleanup.

Risks: cleanup differs between module exit and UML exitcall; double-close/free paths should be checked. Blocking waits must handle signals and avoid leaving SIGIO registrations active. Reading host `/dev/random` can block depending on host entropy policy.

Test signals: boot with UML_RANDOM, inspect hwrng registration, read from guest hwrng paths, block/unblock behavior under low entropy, unload module, and UML shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/rtc.h

Purpose: declares host/timetravel helper functions for the UML RTC driver.

Important APIs/types/functions: prototypes are `uml_rtc_start()`, `uml_rtc_enable_alarm()`, `uml_rtc_disable_alarm()`, `uml_rtc_stop()`, and `uml_rtc_send_timetravel_alarm()`.

Control flow: `rtc_kern.c` calls these helpers to create an interrupt source, program real-time alarms, cancel alarms, and inject time-travel alarm events.

State and persistence: no state is defined here; implementation state is in `rtc_user.c` and `rtc_kern.c`.

Dependencies and integration points: bridges the Linux RTC class driver to host `timerfd`/pipe behavior.

Risks: prototypes rely on `bool`; users must include suitable headers before this file, as the C files do.

Test signals: compile RTC driver and exercise alarm setup in normal and time-travel modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/rtc_kern.c

Purpose: implements a UML RTC class device that can wake the guest from suspend and integrate with UML time-travel mode.

Important APIs/types/functions: global state includes `uml_rtc_alarm_time`, `uml_rtc_alarm_enabled`, `uml_rtc`, `uml_rtc_irq_fd`, and `uml_rtc_irq`. RTC ops are `uml_rtc_read_time()`, `uml_rtc_read_alarm()`, `uml_rtc_alarm_irq_enable()`, and `uml_rtc_set_alarm()`. Driver lifecycle functions are `uml_rtc_setup()`, `uml_rtc_cleanup()`, `uml_rtc_probe()`, `uml_rtc_remove()`, and `uml_rtc_init()`.

Control flow: probe starts a host interrupt source with `uml_rtc_start()`, registers a read IRQ, marks it wake-capable, allocates/registers an RTC device, and enables device wakeup. Alarm enable computes seconds from persistent clock to target time; in normal mode it programs host `timerfd`, while time-travel mode schedules a relative `time_travel_event`. IRQ handling disables the alarm, drains the FD, calls `pm_system_wakeup()`, and reports `RTC_IRQF | RTC_AF`.

State and persistence: alarm target/enabled state is in memory only. Time reading uses persistent clock so time-travel mode sees simulated time. No RTC NVRAM is implemented.

Dependencies and integration points: depends on platform device/driver, RTC class, PM wakeup, UML IRQs, `read_persistent_clock64()`, time-travel APIs, and host helpers in `rtc_user.c`.

Risks: negative or past alarm deltas are not deeply validated before unsigned conversion. Cleanup must free IRQ and stop host timer/pipe. Time-travel and normal modes have different FD semantics.

Test signals: register `/dev/rtc*`, read time, set/read/enable/disable alarms, suspend wakeup via `rtcwake`, time-travel alarm delivery, remove driver, and verify IRQ wake flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/rtc_user.c

Purpose: provides host-side alarm interrupt sources for UML RTC: a pipe for time-travel mode or `timerfd` for normal real-time mode.

Important APIs/types/functions: static `uml_rtc_irq_fds[2]` stores pipe/timer descriptors. Public functions are `uml_rtc_send_timetravel_alarm()`, `uml_rtc_start()`, `uml_rtc_enable_alarm()`, `uml_rtc_disable_alarm()`, and `uml_rtc_stop()`.

Control flow: in time-travel mode `uml_rtc_start()` creates a nonblocking close-on-exec pipe; simulated alarm callbacks write a counter to the pipe. In normal mode it creates a `CLOCK_REALTIME` timerfd, marks SIGIO broken, and adds the FD to SIGIO monitoring. Enabling an alarm calls `timerfd_settime()` with a relative seconds value. Stop closes the write end for pipes or removes SIGIO for timerfd, then closes the read FD.

State and persistence: only runtime FDs are stored. No alarm state is persisted here.

Dependencies and integration points: depends on `timerfd_create`, `timerfd_settime`, pipe helpers, SIGIO helpers, `os_close_file()`, and `rtc_kern.c`.

Risks: timerfd does not send SIGIO, so the workaround must remain aligned with UML IRQ handling. Time-travel writes ignore short-write errors. `uml_rtc_disable_alarm()` uses zero-time timer programming.

Test signals: normal timerfd alarm firing, time-travel pipe injection, start failure cleanup, repeated enable/disable, and stop in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ssl.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ssl.c

Purpose: implements UML virtual serial lines (`ttyS*`) using the common line/channel framework.

Important APIs/types/functions: `NR_PORTS` is 64. Static state includes `opts`, `driver`, `conf[]`, `def_conf`, `serial_lines[]`, and `ssl_init_done`. Functions include `ssl_config()`, `ssl_get_config()`, `ssl_remove()`, `ssl_install()`, `ssl_console_write()`, `ssl_console_device()`, `ssl_console_setup()`, `ssl_init()`, `ssl_exit()`, `ssl_chan_setup()`, and `ssl_non_raw_setup()`.

Control flow: boot-time `ssl...` setup records per-line or default channel strings. Late init registers a TTY serial driver, updates xterm titles with UMID, configures all 64 lines from command/default strings, and registers a `ttyS` console. TTY operations delegate to `line.c`; mconsole config/remove/query use the embedded `mc_device`.

State and persistence: per-line runtime state lives in `serial_lines[]`; boot command strings persist as pointers in `conf[]`/`def_conf`. No host data is persisted.

Dependencies and integration points: depends on TTY, console, channel/line framework, mconsole, UML setup/help macros, and default `CONFIG_SSL_CHAN`.

Risks: all 64 lines are configured at init, so invalid defaults can produce repeated errors. `ssl-non-raw` changes global channel options before line setup. Console registration depends on line setup success.

Test signals: boot with `ssl0=pty`, `ssl=tty:/dev/...`, `ssl-non-raw`, use `/dev/ttyS*`, mconsole `config sslN=...`, remove/query serial lines, and serial console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ssl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stderr_console.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/stderr_console.c

Purpose: provides an early, optional console that writes printk output directly to host stderr.

Important APIs/types/functions: static `use_stderr_console` is set by `stderr=`. `stderr_console_write()` writes to FD 2 through `generic_write()`. `stderr_console_init()` registers the console during console init, and `unregister_stderr()` unregisters it later.

Control flow: if boot option `stderr=<nonzero>` is present, console init registers a `stderr` console with `CON_PRINTBUFFER`. A later initcall always unregisters it so the real UML console can become `/dev/console`.

State and persistence: only a boot-time boolean is stored. Output goes to host stderr and is not persisted by the driver.

Dependencies and integration points: depends on Linux console initcalls, UML channel generic write helper, and `__setup`.

Risks: registering too early can make stderr the default console; the late unregister is intentional to avoid `/dev/console` open failures. Unregister is called even when not registered and should remain harmless.

Test signals: boot with and without `stderr=1`, inspect early printk destination, ensure `/dev/console` opens after normal console registration, and verify unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stderr_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.c

Purpose: implements UML virtual consoles (`tty0`-`tty15`) using common channel/line infrastructure. It provides the main guest console and configurable additional consoles.

Important APIs/types/functions: `MAX_TTYS` is 16. Static objects include `opts`, `driver`, `vt_conf[]`, `def_conf`, `vts[]`, `console_ops`, and `stdiocons`. Functions include `stdio_announce()`, `con_config()`, `con_get_config()`, `con_remove()`, `con_install()`, `uml_console_write()`, `uml_console_device()`, `uml_console_setup()`, `stdio_init()`, `console_exit()`, and `console_chan_setup()`.

Control flow: boot-time `con...` setup records default or per-console channel strings, ignoring `console=` substrings intended for generic console selection. Late init registers the TTY driver, applies UMID to xterm titles, configures each console from explicit/default/compiled defaults (`CON_ZERO_CHAN` for tty0, `CON_CHAN` for others), then registers the console driver. Writes lock the line and dispatch directly to the output channel.

State and persistence: per-console runtime state is in `vts[]`; command-line config pointers persist for boot. No host data is persisted.

Dependencies and integration points: depends on TTY major/minor conventions, Linux console subsystem, channel/line framework, mconsole dynamic config, and config defaults from `drivers/Kconfig`.

Risks: main console default uses host stdin/stdout FDs, so terminal raw-mode handling and close ordering are visible to the UML process environment. Invalid compiled channel defaults can leave consoles unavailable. Console writes occur under spinlock and must remain bounded.

Test signals: boot default console, `con0=fd:0,fd:1`, `con1=xterm/pty/null/port`, mconsole config/remove/query, `/dev/tty*` open/write, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.h

Purpose: small header for stdio console support.

Important APIs/types/functions: declares `save_console_flags()`.

Control flow: no executable flow exists in this header. In the researched subset the declaration is not implemented or used by `stdio_console.c`, suggesting it is legacy or used by other UML files outside this work item.

State and persistence: no state is defined.

Dependencies and integration points: guarded by `__STDIO_CONSOLE_H`. It can be included by code that wants to preserve console flags across UML startup.

Risks: stale declarations can mislead maintainers. Before removal, search the whole UML tree for users because this subset may not contain all call sites.

Test signals: full UML build with warnings enabled and tree-wide symbol search for `save_console_flags`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/stdio_console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/tty.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/tty.c

Purpose: implements the `tty:` channel backend, attaching a UML console/serial line to a named host terminal device.

Important APIs/types/functions: `struct tty_chan` stores the host device path, raw flag, and saved terminal attributes. Backend callbacks are `tty_chan_init()`, `tty_open()`, and `tty_ops`.

Control flow: `tty_chan_init()` requires `:device` syntax and stores a pointer to the parsed device string. `tty_open()` chooses `O_RDONLY`, `O_WRONLY`, or `O_RDWR` from channel direction, opens the host path, optionally saves and sets raw mode, reports the device string, and returns the FD. Reads/writes/window-size use generic helpers.

State and persistence: per-channel backend state stores path and terminal attributes. No persistent data is written.

Dependencies and integration points: depends on host `open`, termios/raw helpers, generic channel operations, and parser string lifetime from `chan_kern.c`.

Risks: the stored path points into the channel config string, so config lifetime must outlive the backend. Error paths after raw-mode setup return without closing FD in some failures. Raw-mode restoration is generic close only, so saved `tt` is not restored here.

Test signals: boot with `tty:/dev/tty...` for input/output/bidirectional modes, invalid paths, raw/non-raw serial config, and terminal window-size queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ubd.h

Purpose: declares the user/helper side of the UML block device I/O thread interface.

Important APIs/types/functions: prototypes are `start_io_thread()`, `io_thread()`, `ubd_read_poll()`, and `ubd_write_poll()`. External `kernel_fd` is the helper-thread side of the IPC pipe. `UBD_REQ_BUFFER_SIZE` is 64 request pointers.

Control flow: `ubd_kern.c` starts the helper with `start_io_thread()` and passes request pointers through a pipe; `io_thread()` reads them, performs host I/O, and writes completed pointers back.

State and persistence: no state is defined here beyond external declaration. Runtime state lives in the implementation and host disk image files.

Dependencies and integration points: depends on UML `os.h` helper-thread types and the block driver.

Risks: pointer-passing over a pipe assumes shared address space between UML kernel and helper thread. Buffer size must match bulk read/write logic in both halves.

Test signals: build UBD, start I/O thread, exercise asynchronous request completion, and fall back when helper startup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ubd_kern.c

Purpose: implements the UML block device driver (`ubd*`) and its helper-thread I/O engine. It maps guest block requests to host file I/O, supports read-only/sync/shared/no-COW/no-trim flags, copy-on-write images, discard/write-zeroes, dynamic mconsole config, and block-mq registration.

Important APIs/types/functions: key structs are `io_desc`, `io_thread_req`, `cow`, and `ubd`. Configuration/open helpers include `ubd_setup_common()`, `ubd_config()`, `ubd_add()`, `ubd_remove()`, `ubd_open_dev()`, `open_ubd_file()`, `create_cow_file()`, and `ubd_close_dev()`. I/O functions include `ubd_queue_rq()`, `ubd_submit_request()`, `ubd_alloc_req()`, `ubd_map_req()`, `cowify_req()`, `cowify_bitmap()`, `ubd_intr()`, `do_io()`, and `io_thread()`.

Control flow: boot or mconsole config parses `ubd<n><flags>=file[,backing][,serial]`, stores per-device config, and late init registers disks for configured entries, defaulting `ubd0` to `root_fs`. Opening detects COW headers, validates/switches backing files, reads COW bitmaps, opens backing read-only, and registers a block-mq disk. Queueing starts a block request, builds an `io_thread_req` with one descriptor per segment or special request, translates COW sector masks and bitmap updates, and writes the request pointer to the helper pipe. The helper reads pointers, performs pread/pwrite/fallocate/fsync against chosen host FD ranges, updates COW bitmap words, and writes completed pointers back. The IRQ handler completes block-mq requests.

State and persistence: persistent state lives in host disk image and COW files. Runtime state includes `ubd_devs[]`, open FDs, COW bitmap in vmalloc memory, platform devices, disks, tag sets, helper-thread pipe buffers, and remainder buffers for partial pipe reads.

Dependencies and integration points: depends on Linux block-mq, gendisk, platform devices, mconsole, UML IRQ/helper-thread/host file APIs, COW helpers, and generic block ioctls.

Risks: helper-thread code is explicitly outside normal kernel context and must not call kernel services. Pointer IPC and partial-read remainder handling are subtle. COW bitmap updates must stay consistent with data writes. Request completion frees allocated request wrappers; failure to write to the helper can leak or stall requests. `map_error()` expects positive errno inputs but callers sometimes pass negated return conventions, so error-code sign handling deserves tests.

Test signals: boot from `root_fs`, read/write block devices, read-only/sync/shared/no-trim flags, COW creation and backing mismatch/switching, discard/write-zeroes support disablement on `NOTSUPP`, flushes, HDIO identity/CDROM volume ioctls, mconsole add/remove while open/closed, helper-thread failure fallback, and high segment-count I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ubd_user.c

Purpose: starts and supports the host-side UBD I/O helper thread used by `ubd_kern.c`.

Important APIs/types/functions: static `kernel_pollfd` tracks the helper pipe. Public functions are `start_io_thread()`, `ubd_read_poll()`, and `ubd_write_poll()`. External `kernel_fd` is set to the helper side of the pipe.

Control flow: `start_io_thread()` creates a nonblocking pipe, assigns one end to `kernel_fd` and the other to the kernel side, configures poll state, starts `io_thread()` with `os_run_helper_thread()`, and returns the kernel-side FD. Poll helpers switch events between `POLLIN` and `POLLOUT` and call `poll()`.

State and persistence: runtime state is the pipe FD and pollfd. Persistent disk data is written by `io_thread()` in `ubd_kern.c`, not here.

Dependencies and integration points: depends on UML `os_pipe`, `os_set_fd_block`, `os_run_helper_thread`, host `poll`, and `io_thread()` symbol from `ubd_kern.c`.

Risks: failure paths must close both pipe ends and reset `kernel_fd`. The helper and kernel communicate raw pointers, so the thread must run in the same address space model UML expects.

Test signals: successful helper startup, nonblocking flags, read/write poll wakeups, helper thread start failure, and UBD fallback logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.c

Purpose: implements UML high-performance vector network devices (`vecN`) using batch send/receive syscalls and transport-specific host sockets. It supports vector or legacy RX/TX, NAPI, BQL, ethtool stats/coalescing/BPF firmware loading, mconsole dynamic config, and transports implemented by `vector_user.c`/`vector_transports.c`.

Important APIs/types/functions: key structs are `vector_cmd_line_arg`, `vector_device`, `vector_queue`, `vector_private`, and `vector_estats`. Major functions include option parsers (`get_mtu()`, `get_depth()`, `get_transport_options()`), queue management (`create_queue()`, `destroy_queue()`, `vector_enqueue()`, `vector_send()`, `prep_skb()`, `vector_mmsg_rx()`), netdev ops (`vector_net_open()`, `vector_net_close()`, `vector_net_start_xmit()`, `vector_poll()`, `vector_net_tx_timeout()`), ethtool ops, config functions (`vector_parse()`, `vector_config()`, `vector_remove()`), and init functions (`vector_setup()`, `vector_init()`, `vector_net_init()`).

Control flow: boot `vecN:key=value,...` arguments are stored early and parsed at late init; mconsole config can add devices later. Device configuration allocates an Ethernet netdev, sets MTU/MAC/options, registers a platform device and netdevice, and stores parsed args. Open loads optional BPF, opens host FDs, builds transport data, creates RX/TX vector queues or legacy buffers, registers NAPI and read/write IRQs, attaches BPF if needed, starts the queue, and schedules NAPI to drain preexisting host data. TX either writes one packet with writev or enqueues skb/iov entries for sendmmsg, using a timer for coalescing. RX uses recvmmsg into prepared skbs or legacy recvmsg, verifies transport headers, trims encapsulation, updates stats, and delivers with GRO.

State and persistence: runtime state includes registered vector devices list, parsed boot args, per-netdev FDs, IRQs, queues, skbs/iov arrays, transport data, BPF program, timers, NAPI state, and ethtool stats. No persistent network state is stored.

Dependencies and integration points: depends on Linux netdev/NAPI/ethtool/BQL/firmware APIs, UML IRQ/FD helpers, `vector_user.h` host socket helpers, `build_transport_data()`, mconsole, and optional inetaddr notifier.

Risks: queue ownership spans hard IRQ, NAPI, timers, and netdev close. RX queue comments note it is not a conventional wraparound queue. Error state deactivates FDs and can leave TX busy until reset/close. BPF firmware loading via ethtool is gated but powerful. Some error paths in `vector_eth_configure()` return without freeing partially registered platform resources.

Test signals: configure tap/raw/hybrid/GRE/L2TPv3/BESS devices, vector and legacy modes, ping/throughput tests, GRO/TSO/vnet-header toggles, BPF default/user/flash attach, ethtool stats/ring/coalesce, TX timeout recovery, mconsole add/remove, close/reopen, and host socket EAGAIN/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.h

Purpose: declares kernel-side data structures and constants for UML vector network devices.

Important APIs/types/functions: constants include `QUEUE_SENDMSG`, `QUEUE_SENDMMSG`, `VECTOR_RX`, `VECTOR_TX`, `VECTOR_BPF`, `VECTOR_QDISC_BYPASS`, `VECTOR_BPF_FLASH`, `ETH_MAX_PACKET`, `ETH_HEADER_OTHER`, and `MAX_FILTER_PROG`. `struct vector_queue` stores mmsg/iov/skb arrays and queue indices/locks/depth. `struct vector_estats` defines ethtool counters. `struct vector_private` is the netdev private state containing NAPI, timer, work item, FDs, queues, IRQs, parsed args, transport callbacks/data, header buffers, state flags, stats, BPF, and trailing user storage. It declares `build_transport_data()`.

Control flow: no executable flow exists here; `vector_kern.c` and `vector_transports.c` use the declarations.

State and persistence: the header defines runtime state layout but owns no instances.

Dependencies and integration points: depends on Linux netdevice/platform/skbuff/socket/list/workqueue/interrupt APIs, atomics, and `vector_user.h`.

Risks: callback fields `form_header` and `verify_header` are transport ABI between transport builders and core RX/TX paths. Queue size and feature flags must match vector core assumptions.

Test signals: compile vector core/transports, open each transport, validate ethtool stat layout, and test vnet-header transport callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_transports.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/vector_transports.c

Purpose: builds transport-specific header, verification, and offload behavior for UML vector network devices. It supports GRE, L2TPv3, raw, tap, tap/raw hybrid, and BESS transport modes.

Important APIs/types/functions: transport state structs are `gre_minimal_header`, `uml_gre_data`, and `uml_l2tpv3_data`. Header callbacks are `l2tpv3_form_header()`, `gre_form_header()`, `raw_form_header()`, `l2tpv3_verify_header()`, `gre_verify_header()`, and `raw_verify_header()`. Builders are `build_gre_transport_data()`, `build_l2tpv3_transport_data()`, `build_raw_transport_data()`, `build_hybrid_transport_data()`, `build_tap_transport_data()`, `build_bess_transport_data()`, and dispatcher `build_transport_data()`.

Control flow: vector open calls `build_transport_data()` after host FDs are opened. GRE/L2TP builders parse required and optional args, allocate transport data, set header sizes, offsets, expected keys/cookies/session IDs/counters, and assign form/verify callbacks. Raw/tap/hybrid builders try to enable virtio-net vnet headers on host FDs and, if successful, enable checksum/GSO/GRO/TSO netdev features and use virtio-net header conversion callbacks. BESS uses no extra headers.

State and persistence: per-device transport state is allocated into `vp->transport_data`; sequence/counter values advance during TX. No persistent state is stored.

Dependencies and integration points: depends on vector parsed-arg helpers, Linux Ethernet/skbuff/netdev feature APIs, GRE/L2TP constants from `vector_user.h`, virtio-net header conversion, and host FD capability helpers such as `uml_raw_enable_vnet_headers()` and `uml_tap_enable_vnet_headers()`.

Risks: encapsulation verification must account for IPv4 raw headers versus IPv6/UDP layouts. Required GRE key and L2TP session/cookie pairs must be supplied consistently; otherwise open fails. Raw vnet-header support changes advertised offloads and buffer sizing. Header offset arithmetic is security-sensitive because malformed packets are parsed from host input.

Test signals: GRE with/without keys and sequence, L2TPv3 with UDP/IP, cookies/counters, IPv4/IPv6 variants, raw/tap vnet-header negotiation, GRO/TSO checksum behavior, bad key/cookie/session packet drops, BESS no-header path, and feature toggling via ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_transports.c -->

# Group Research: group_1322_nvme_cli_sources_virtualization_nvme_cli_completions_bash_nvme_comp_c21c8351b816

Scope verified against `Docs/research_subset_a.md`: all researched files are under `sources/virtualization/nvme-cli`, which is included in subset A. The listed internal group report did not exist, so this report is generated fresh from complete reads of each listed source file.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/completions/bash-nvme-completion.sh -->
# File Research: sources/virtualization/nvme-cli/completions/bash-nvme-completion.sh

This Bash completion script registers completion for the `nvme` CLI. It is a static dispatcher around `_nvme_subcmds`, top-level command lists, vendor plugin subcommands, and per-command option tables.

Core behavior:
- `nvme_list_opts()` maps built-in nvme subcommands to supported option completions.
- Each `plugin_*_opts()` function provides option completions for a vendor or feature plugin, including Intel, WDC, Micron, Seagate, Solidigm, OCP, ZNS, and others.
- `_nvme_subcmds()` initializes completion state, declares associative arrays for plugin subcommands and option handler functions, lists top-level nvme commands, dispatches plugin completion when the second word is a plugin, and otherwise calls `nvme_list_opts`.
- It completes `/dev/nvme*` positional device arguments after a threshold number of non-option words.
- It ends with `complete -o default -F _nvme_subcmds nvme`.

Important details:
- The file mirrors many CLI options by hand, so it can drift from command definitions.
- Some option spellings appear inconsistent or typo-prone, such as `opts=+=`, missing `=` on some long options, and command-name mismatches like `changed-alloc-ns-list-log` versus `changed-alloc-cns-list-log`.
- It supports NVMe-oF commands such as `discover`, `connect-all`, `connect`, `disconnect`, `disconnect-all`, and `dim`.
- It also supports broad NVMe admin, I/O, log, namespace, security, register, telemetry, ZNS, FDP, and plugin workflows.

Integration role:
- User-facing shell ergonomics only; no runtime library logic.
- Depends on Bash completion helpers such as `_init_completion` from bash-completion.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/completions/bash-nvme-completion.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/define_cmd.h -->
# File Research: sources/virtualization/nvme-cli/define_cmd.h

This header is a macro include shim used during command declaration generation.

Core behavior:
- Only active when `CREATE_CMD` is already defined.
- Temporarily undefines `CREATE_CMD`.
- Defines stringify helpers and `CMD_INCLUDE(cmd)` to include `<cmd>.h` based on `CMD_INC_FILE`.
- Defines `CMD_HEADER_MULTI_READ`, includes the command-specific header, includes `cmd_handler.h`, then undefines `CMD_HEADER_MULTI_READ`.
- Restores `CREATE_CMD`.

Integration role:
- Supports multi-pass command macro expansion in nvme-cli.
- Keeps command header inclusion parameterized by `CMD_INC_FILE`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/define_cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/etc/discovery.conf.in -->
# File Research: sources/virtualization/nvme-cli/etc/discovery.conf.in

This is the template for the default NVMe-oF discovery configuration file.

Content:
- Comments explain that the file is used to extract default discovery parameters.
- Gives an example discovery line using `--transport`, `--traddr`, `--trsvcid`, `--host-traddr`, and `--host-iface`.

Integration role:
- Consumed by `fabrics.c` via the installed path represented by `PATH_NVMF_DISC`.
- Provides line-oriented CLI-style defaults for discovery when no explicit CLI parameters are supplied.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/etc/discovery.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/fabrics.c -->
# File Research: sources/virtualization/nvme-cli/fabrics.c

This is the nvme-cli front-end implementation for NVMe over Fabrics commands. It parses CLI options, prepares libnvme/libnvmf contexts, loads JSON/volatile/NBFT/discovery configuration, and delegates the actual fabrics operations to libnvme.

Main commands:
- `fabrics_discovery()`: implements discovery and connect-all style flows. It supports explicit endpoints, existing discovery controller devices, NBFT discovery, JSON config, volatile runtime config, and `/etc/nvme/discovery.conf`.
- `fabrics_connect()`: validates required connection fields, loads config if requested, creates a fabrics context, and connects via `libnvmf_connect()` or JSON config connection.
- `fabrics_disconnect()`: disconnects by NQN or device name after scanning current topology.
- `fabrics_disconnect_all()`: disconnects non-PCIe fabrics controllers, optionally filtered by transport.
- `fabrics_config()`: reads, scans, modifies, updates, and dumps JSON configuration.
- `fabrics_dim()`: performs Discovery Information Management register/deregister operations on controllers by NQN or device.

Key helpers:
- `nvmf_default_args()` sets defaults such as `tos = -1` and default controller loss timeout.
- `save_discovery_log()` writes raw discovery logs to a user-selected file.
- Hook functions handle retries, connected output, already-connected output, discovery log output, and parsing discovery.conf lines.
- `set_fabrics_options()` maps parsed CLI fields into `libnvmf_context` setters.
- `setup_common_context()` and `create_common_context()` configure endpoint, host identity, queues, reconnect policy, digests, TLS, DHCHAP, duplicate connect, and persistence.
- `create_discovery_context()` adds discovery hooks and discovery-specific defaults.
- `nvme_read_volatile_config()` scans runtime JSON files under the nvme run directory.
- `load_nvme_fabrics_module()` optionally uses libkmod to load `nvme-fabrics`.

Important behavior:
- Uses `libnvme_skip_namespaces()` before topology scans where namespace details are not needed.
- Supports `--config none` to disable JSON config.
- Supports `--dump-config` to write current config to stdout.
- Supports NBFT path selection and `--nbft` / `--no-nbft`.
- Suppresses disconnect errors for missing modules in common unconditional cleanup scenarios.
- Uses global static output/control flags such as `raw`, `persistent`, `quiet`, and `dump_config`.

Integration role:
- Bridges nvme-cli argument parsing and user output with libnvme/libnvmf fabrics APIs.
- Uses `fabrics.h` for declarations and is called by the command dispatch layer.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/fabrics.h -->
# File Research: sources/virtualization/nvme-cli/fabrics.h

This header declares the nvme-cli fabrics command entry points.

Declared functions:
- `fabrics_discovery`
- `fabrics_connect`
- `fabrics_disconnect`
- `fabrics_disconnect_all`
- `fabrics_config`
- `fabrics_dim`

Integration role:
- Exposes fabrics command implementations from `fabrics.c` to nvme-cli command registration and dispatch.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme-wrap.c -->
# File Research: sources/virtualization/nvme-cli/libnvme-wrap.c

This file defines wrapper macros for weak libnvme function forwarding.

Core behavior:
- Includes `dlfcn.h`, `errno.h`, `stdlib.h`, `libnvme.h`, and `nvme-print.h`.
- `VOID_FN` generates a weak wrapper for a void-returning function. It resolves the next symbol with `dlsym(RTLD_NEXT, name)`, reports an error, and exits if missing.
- `FN` generates a weak wrapper for a returning function. It resolves the next symbol and returns a default value if unavailable.

Integration role:
- Allows nvme-cli to provide compatibility wrappers around libnvme symbols while still forwarding to the real implementation when present.
- Useful when source compatibility must tolerate libnvme version differences.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme-wrap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/.readthedocs.yaml -->
# File Research: sources/virtualization/nvme-cli/libnvme/.readthedocs.yaml

This Read the Docs configuration builds libnvme documentation.

Key settings:
- Uses configuration version 2.
- Builds on Ubuntu 24.04 with Python 3.14.
- Installs Meson via apt and `asciidoc` / `sphinx` via pip.
- Runs `scripts/build.sh rst_docs` before Sphinx.
- Points Sphinx at `.build-ci/libnvme/doc/conf.py`.

Integration role:
- Documentation CI setup for libnvme hosted docs.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/.readthedocs.yaml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/Makefile -->
# File Research: sources/virtualization/nvme-cli/libnvme/Makefile

This is a convenience Makefile over Meson.

Targets:
- Default target builds `libnvme`.
- `update-subprojects` runs `meson subprojects update`.
- `.build` runs `meson setup`.
- `libnvme` runs `meson compile -C .build`.
- `clean` removes `.build` and purges subprojects.
- `install`, `uninstall`, `dist`, `test`, and `test-strict` wrap Meson operations.
- `rpm` creates a git archive, adds generated spec file, compresses it, and invokes `rpmbuild -ta`.

Integration role:
- Developer-friendly façade for the Meson project.
- `test-strict` runs only the libnvme suite instead of all subprojects.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.c

This C example discovers loop transport NVMe-oF targets and prints discovery log records.

Core flow:
- Creates a libnvme global context and libnvmf context.
- Configures discovery subsystem over `loop`.
- Scans topology, obtains a host, creates a controller, and adds it to the host.
- Allocates discovery arguments, sets max retries to 4, and calls `libnvmf_get_discovery_log`.
- Disconnects and frees the temporary controller.
- Prints discovery log header and entries as an ASCII tree.

Integration role:
- Demonstrates fabrics discovery without requiring an existing connection, assuming loop targets are configured.
- Exercises `libnvmf_context_create`, `libnvmf_context_set_connection`, topology scan, controller creation, discovery args, and discovery log retrieval.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.py

This Python example performs recursive NVMe-oF discovery using libnvme Python bindings.

Core behavior:
- Creates `GlobalCtx`, `Host`, and an initial TCP discovery controller for `127.0.0.1:4420`.
- `discover()` connects a controller, prints support for discovery log-page options, retrieves the discovery log, and recurses through discovery referrals.
- Limits recursion to 8 levels.
- Handles `ConnectError`, `DiscoverError`, and possible failures reading supported log pages.
- Prints discovered NVM and discovery subsystem records.
- Finally prints subsystems and controllers known to the host.

Integration role:
- Demonstrates high-level Python bindings for controller connection, log-page discovery, context managers, recursive discovery, and exception handling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/discover-loop.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/display-columnar.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/display-columnar.c

This C example scans NVMe topology and prints hosts/subsystems/controllers/namespaces in columnar format.

Core behavior:
- Creates a global context and scans topology.
- Prints subsystem name, subsystem NQN, and controller list.
- Prints controller details including serial, model, firmware, transport, address, subsystem, and namespaces.
- Prints namespace details including name, NSID, LBA count, LBA size, and controllers.
- Traverses hosts, subsystems, controllers, namespaces, and paths via libnvme iterator macros.

Integration role:
- Demonstrates libnvme topology traversal and getter APIs in a compact report-style output.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/display-columnar.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/display-tree.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/display-tree.c

This C example scans NVMe topology and prints it as an ASCII tree.

Core behavior:
- Creates a global context and scans topology.
- Iterates hosts, subsystems, subsystem namespaces, controllers, controller namespaces, and controller paths.
- Prints selected attributes: subsystem NQN, namespace LBA size/count, controller transport/address/state, and path ANA state.
- Uses `_safe` iterator variants where next pointers are needed for tree branch formatting.

Integration role:
- Demonstrates topology walking and tree-style presentation with libnvme.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/display-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/meson.build

This Meson file defines libnvme example executables.

Always built examples:
- `telemetry-listen`
- `display-columnar`
- `display-tree`

Conditional examples:
- If `want_fabrics`: `discover-loop`
- If `want_mi`: `mi-mctp`, `mi-mctp-csi-test`, `mi-mctp-ae`
- If `want_mi` and D-Bus dependency is found: `mi-conf`

Dependencies:
- Common examples use `config_dep`, `ccan_dep`, and `libnvme_dep`.
- `mi-mctp-csi-test` also uses `threads_dep`.
- `mi-conf` also uses `libdbus_dep`.

Integration role:
- Keeps example build selection aligned with optional library features.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-conf.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-conf.c

This C example queries an NVMe-MI MCTP endpoint for optimal MTU and applies it locally through D-Bus and remotely through NVMe-MI config commands.

Core behavior:
- Parses endpoint strings of the form `mctp:<net>,<eid>`.
- Opens an MCTP endpoint with `libnvme_mi_open_mctp`.
- Finds an SMBus port by reading subsystem and port info.
- Reads current MCTP MTU via NVMe-MI.
- Sets device MCTP MTU through `libnvme_mi_mi_config_set_mctp_mtu`.
- Calls mctpd over system D-Bus to set local route MTU, adding 4 bytes for the MCTP header.
- Reverts device MTU if local D-Bus update fails and the old MTU was known.

Integration role:
- Demonstrates coordinated host route and device NVMe-MI MCTP MTU configuration.
- Depends on D-Bus and libnvme MI support.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-conf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-ae.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-ae.c

This C example enables and processes NVMe-MI asynchronous event messages over MCTP.

Core behavior:
- Parses `<net> <eid> [AE numbers...]`.
- Opens an MCTP endpoint.
- Queries and prints previously enabled events.
- Builds `libnvme_mi_aem_config` with a handler and enabled event bitmap.
- Enables asynchronous event messages.
- Gets the AEM file descriptor and polls it alongside stdin.
- When AEM data is readable, calls `libnvme_mi_aem_process`.
- Handler drains events via `libnvme_mi_aem_get_next_event`, prints event fields, and returns ACK.
- Disables AEM and closes context on exit.

Important detail:
- Returns an explicit message for `EOPNOTSUPP`, noting that MCTP Peer-Bind is required for AEM.

Integration role:
- Demonstrates event-driven MI over MCTP with `poll()`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-ae.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-csi-test.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-csi-test.c

This C example sends two MI admin commands in parallel over MCTP using different CSI buffers.

Core behavior:
- Supports action `csi-test <controller-id> [<log-id>]`.
- Opens two MCTP endpoints to the same net/eid.
- Sets CSI 0 on one endpoint and CSI 1 on the other.
- Starts a pthread that runs `do_get_log_page()` on the second endpoint.
- Runs `do_get_log_page()` on the first endpoint in the main thread.
- Joins the thread and returns either command’s error.
- `do_get_log_page()` initializes a transport handle for the controller, builds a Get Log command, retrieves a 4096-byte log page, and hexdumps it.

Integration role:
- Tests independent concurrent MCTP endpoint usage and CSI separation.
- Depends on pthreads and MI support.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-csi-test.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp.c

This is a broad NVMe-MI over MCTP example CLI.

Supported target modes:
- Direct endpoint: `<net> <eid>`
- D-Bus scan mode: `dbus`, which discovers known MCTP endpoints and runs the selected action on each.

Supported actions:
- `info`: subsystem info, port info, and health status.
- `controllers`: controller list and per-controller metadata.
- `identify <controller-id> [--partial]`: Identify Controller over MI admin passthrough.
- `get-log-page <controller-id> [<log-id>]`: Get Log Page and hexdump data.
- `admin <controller-id> <opcode> [<cdw10> ...]`: raw MI admin request.
- `security-info <controller-id>`: Security Receive protocol list.
- `get-config [port]`: SMBus frequency and MCTP MTU.
- `set-config <port> <type> <val>`: set SMBus frequency or MCTP MTU.
- `control-primitive <abort|pause|resume|get-state|replay>`: sends MI control primitive.

Key helpers:
- Port-specific printers for PCIe and SMBus port data.
- Controller info printer with PCIe route and PCI IDs.
- Hexdump routines used by log and admin raw actions.
- Security protocol description lookup.
- SMBus frequency string/value mapping.
- Central `do_action_endpoint()` dispatcher.

Integration role:
- Demonstrates most core libnvme MI/MCTP APIs in a single sample utility.
- Useful as reference for endpoint scanning, transport handle creation, admin passthrough, MI data reads, config commands, and control primitives.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/telemetry-listen.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/examples/telemetry-listen.c

This C example listens for NVMe controller uevents and saves telemetry logs on telemetry asynchronous events.

Core behavior:
- Scans topology and counts controllers.
- Opens each controller’s sysfs `uevent` file.
- Uses `select()` to wait for readable uevent file descriptors.
- Parses lines containing `NVME_AEN=...`.
- Extracts AEN type, info, and log identifier.
- If the event is a telemetry notice, reads controller telemetry via `libnvme_get_ctrl_telemetry`.
- Saves telemetry data to `/var/log/<subsysnqn>-telemetry-<epoch>`.

Important detail:
- The `select()` call uses `nr` as the first argument, but `select()` expects max fd + 1; this example may not be robust if fd values exceed controller count.
- Opens files read-only and writes output with owner/group read permissions.

Integration role:
- Demonstrates sysfs uevent monitoring plus telemetry log retrieval.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/examples/telemetry-listen.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme.spec.in -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme.spec.in

This RPM spec template packages libnvme.

Package structure:
- Main package: runtime library.
- `devel` subpackage: headers, libraries, pkg-config files, and man2 pages.

Build/install:
- `%build` runs Meson with `-Ddocs=man`, `-Ddocs-build=true`, and `-Ddefault_library=both`.
- `%install` runs `meson install --destdir`.
- Template placeholders include version, license, URL, and prefix.

Integration role:
- Used by the Makefile `rpm` target after Meson config generates `libnvme.spec`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme.spec.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/__init__.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/__init__.py

This Python package initializer exposes generated version strings.

Content:
- `__version__ = @LIBNVME_VERSION@`
- `__git_version__ = @GIT_VERSION@`

Integration role:
- Processed through Meson `configure_file`.
- Installed with the SWIG-generated Python bindings.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/_exceptions.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/_exceptions.py

This Python file defines libnvme exception classes.

Classes:
- `NvmeError`: base exception storing `errno` and `message`, with formatted exception text.
- `ConnectError`
- `DisconnectError`
- `DiscoverError`
- `NotConnectedError`, defaulting to errno 0 and message `Not connected`.

Integration role:
- Used by Python bindings to expose typed errors for connection, disconnection, discovery, and disconnected-state failures.
- Tested by `test-objects.py`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/_exceptions.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/fctx_field_tables.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/fctx_field_tables.h

This generated header maps Python/user-facing fabrics config keys to offsets inside `struct libnvme_fabrics_config`.

Data structures:
- `struct fctx_field { const char *key; size_t off; }`
- Integer fields: queue sizing, reconnect and timeout fields, ToS.
- Long fields: keyring and TLS key IDs.
- Boolean fields: duplicate connect, SQ flow disable, header/data digest, TLS, concat.
- `libnvme_fabrics_config_keys[]`: full key list for validation/introspection.

Integration role:
- Used by Python binding support code to validate and populate fabrics controller dictionaries.
- Generated from `private.h` and updated via Meson `update-accessors`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/fctx_field_tables.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/meson.build

This Meson file builds and tests the Python bindings when `want_python` is enabled.

Core behavior:
- Checks whether Python has `Py_NewRef`; warns if compatibility shim is needed.
- Detects SWIG version and uses `-py3` only for older SWIG.
- Generates `nvme.py` and `nvme_wrap.c` from `nvme.i`.
- Builds `_nvme` Python extension module.
- Declares `python3_libnvme_dep` with `nvme_py_path` for parent Meson fallback use.
- Copies/configures `__init__.py` and `_exceptions.py` into the build/install package directory.
- Sets test environment with `PYTHONPATH`, `MALLOC_PERTURB_`, and `PYTHONMALLOC=malloc`.
- Registers import and Python unit tests.

Tests registered:
- `create-ctrl-object`
- `sigsegv-during-gc`
- `read-nbft-file`
- `object-properties-and-errors`
- `setattr-guards`

Integration role:
- Owns SWIG-based Python module generation, installation, and binding tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/create-ctrl-obj.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/create-ctrl-obj.py

This small Python test creates a libnvme controller object.

Core behavior:
- Imports `libnvme.nvme`.
- Creates `GlobalCtx` and sets log level to debug.
- Creates a discovery controller over loop transport with address `127.0.0.1` and service `8009`.

Integration role:
- Smoke test for Python controller object construction with a dictionary of fabrics parameters.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/create-ctrl-obj.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/gc.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/gc.py

This Python test exercises garbage collection and object lifetime ordering.

Core behavior:
- Creates global context, host, and ten loop discovery controller objects.
- Iterates host subsystems and namespaces.
- Clears `ctx` and `host` before controller/subsystem objects.
- Forces `gc.collect()`.
- Then clears controller and remaining object references.

Purpose:
- Guards against segmentation faults when Python/SWIG objects are destroyed in an order where child objects outlive parent wrappers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/gc.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-nbft.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-nbft.py

This Python unittest verifies NBFT binary parsing through the Python bindings.

Core behavior:
- Defines an expected NBFT dictionary with discovery, HFI, host, and subsystem entries.
- Creates `GlobalCtx`, sets debug log level, and calls `nvme.nbft_get(ctx, args.filename)`.
- Asserts exact equality with expected data.
- Uses argparse to accept `--filename`, preserving unittest args.

Integration role:
- Tests libnvme NBFT parser output shape and Python conversion behavior.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-nbft.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-objects.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-objects.py

This Python unittest suite covers hardware-free object creation, properties, constants, exceptions, and helper functions.

Coverage:
- Constants: discovery subsystem name and discovery log LID.
- `GlobalCtx`: construction, context manager, hosts iterator, topology refresh, log-level values.
- `Host`: construction with hostnqn, hostid, hostsymname; writable `hostsymname`; default DHCHAP host key; subsystem iteration; string representation; context manager.
- `Ctrl`: loop and tcp construction, property access, connected/name defaults, context manager, namespaces iterator, discovery/persistent/unique flags, multiple controllers in one context.
- Exceptions: importability, inheritance, errno/message behavior, `NotConnectedError` defaults.
- Error handling: disconnect/discover on unconnected controller raises `NotConnectedError`.
- Helper functions: `read_hostnqn()` and `read_hostid()` return string or None.

Integration role:
- Main regression suite for Python binding object semantics without requiring real NVMe hardware.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-objects.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-setattr.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-setattr.py

This Python unittest suite validates attribute and constructor dictionary guards on SWIG-generated classes.

Coverage:
- Valid writable property assignment works (`discovery_ctrl`).
- Misspelled property assignment raises `AttributeError`.
- Read-only property assignment raises `AttributeError`.
- Unknown attribute assignment raises `AttributeError`.
- Unknown controller constructor dictionary key raises `KeyError`.
- Missing required controller dictionary keys (`subsysnqn` or `transport`) raise `KeyError`.

Integration role:
- Prevents silent bugs from typos in Python binding property names and fabrics config dictionaries.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/libnvme/tests/test-setattr.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/meson.build

This is the libnvme root Meson entry for building the bundled library or finding an installed one.

Core behavior when `want_libnvme`:
- Optionally checks OpenSSL HKDF behavior by running `test/hkdf_add1.c`.
- Generates `libnvme.spec` from the template.
- Enters generator, `src`, Python bindings, tests, examples, and docs subdirectories based on options.

Fallback behavior:
- If not building bundled libnvme, finds installed libnvme through pkg-config for standard prefixes or compiler library lookup for non-standard prefixes.

Integration role:
- Top-level build orchestrator for libnvme inside nvme-cli.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/collect-sysfs.sh -->
# File Research: sources/virtualization/nvme-cli/libnvme/scripts/collect-sysfs.sh

This Bash helper archives NVMe-related sysfs directories for debugging.

Core behavior:
- Builds filename `nvme-sysfs-<hostname>-<kernel>.tar.xz`.
- Collects fixed sysfs paths for nvme classes and PCI slots.
- Adds real paths for entries under each directory via `readlink -f`.
- Creates a compressed tar archive, preserving permissions, suppressing stderr.

Integration role:
- Diagnostic data collection script for topology/sysfs issues.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/collect-sysfs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc -->
# File Research: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc

This Perl script is a kernel-doc extractor adapted for libnvme documentation generation.

Supported output modes:
- `-man`: troff manual pages.
- `-rst`: reStructuredText, default in this copy.
- `-none`: validation/warnings only.

Supported selection modes:
- All symbols.
- Included `-function NAME` or DOC sections.
- Exported symbols via `EXPORT_SYMBOL`.
- Internal non-exported symbols.
- Exclusions via `-nosymbol`.
- Extra export scan inputs via `-export-file`.

Parser model:
- Scans C comments beginning with `/**`.
- Recognizes function, struct, union, enum, typedef, and `DOC:` blocks.
- Uses state constants for normal code, name, body, prototype, docblock, and inline member docs.
- Parses section names such as Description, Context, Return/Returns, Notes, and Examples.
- Supports inline member documentation inside declarations.
- Parses prototypes, syscall macros, tracepoint macros, structs/unions, enums, typedefs, function pointers, arrays, bitfields, anonymous structs/unions, and common kernel declaration macros.
- Warns about missing/excess parameter documentation and, in verbose mode, missing return documentation.

Output behavior:
- Man output emits `.TH`, `.SH`, `.IP`, and formatted prototypes.
- RST output emits Sphinx C-domain directives, adapting for Sphinx major version before/after 3.
- `-enable-lineno` can emit `#define LINENO` markers in RST mode.
- Highlighting converts kernel-doc syntax for functions, constants, params, structs, enums, typedefs, unions, and members.

Integration role:
- Used by documentation build scripts and `kernel-doc-check`.
- Essential for converting libnvme C API comments into man/RST docs and for CI-style comment validation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc-check -->
# File Research: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc-check

This Bash script validates kernel-doc comments without producing docs.

Core behavior:
- Locates sibling `kernel-doc`.
- Runs `kernel-doc -none "$@"`.
- Greps output for `warning` or `error`.
- Exits successfully only when kernel-doc exits 0 and grep finds no warnings/errors.

Integration role:
- CI/developer check wrapper for libnvme API documentation comments.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc-check -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/list-man-pages.sh -->
# File Research: sources/virtualization/nvme-cli/libnvme/scripts/list-man-pages.sh

This Bash helper extracts documented symbol names from a source file.

Core behavior:
- Reads the file passed as `$1`.
- Uses sed patterns to find kernel-doc comments for functions, structs, and enums.
- Prints each matched symbol name.

Integration role:
- Likely used by documentation tooling to enumerate generated man page targets.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/list-man-pages.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/list-pre-compiled.sh -->
# File Research: sources/virtualization/nvme-cli/libnvme/scripts/list-pre-compiled.sh

This shell helper lists precompiled man pages.

Core behavior:
- Iterates `man/*.2`.
- Echoes each path.

Integration role:
- Simple documentation build helper for existing man2 files.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/scripts/list-pre-compiled.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/libnvme-mi.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/libnvme-mi.h

This public aggregate header exposes libnvme MI APIs.

Content:
- C++ guards with `extern "C"`.
- Includes:
  - `nvme/lib.h`
  - `nvme/mi.h`
  - `nvme/nvme-types.h`
  - `nvme/nvme-cmds.h`

Integration role:
- Installed when MI support is enabled.
- Used by MI examples such as `mi-mctp.c`, `mi-conf.c`, and `mi-mctp-ae.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/libnvme-mi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/libnvme.h.in -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/libnvme.h.in

This template generates the public aggregate `libnvme.h`.

Content:
- C++ guards with `extern "C"`.
- Includes common libnvme headers for accessors, filters, ioctl, lib types, linux helpers, memory, commands, types, tree, and utilities.
- Contains `@FABRICS_INCLUDE@`, filled by Meson to include fabrics/NBFT/accessors-fabrics headers only when fabrics support is enabled.

Integration role:
- Produces installed top-level public libnvme header.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/libnvme.h.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/meson.build

This Meson file defines the libnvme C library sources, headers, link scripts, dependencies, and installed headers.

Core source selection:
- Always includes core accessors, base64, crc32, ioctl, log, command, and util sources.
- On Windows, uses Windows ioctl/memory/no-crypto sources.
- Otherwise includes crypto, filters, Linux ioctl/lib/sysfs/tree/memory support.
- If `want_fabrics`, adds fabrics, NBFT, tree-fabrics, util-fabrics, and accessors-fabrics sources/headers.
- If no fabrics, adds `no-fabrics.c`.
- If `want_mi`, adds MI and MCTP sources/headers; otherwise `no-mi.c`.
- If liburing is available, adds `uring.c`; otherwise `no-uring.c`.
- If json-c and fabrics are available, adds `json.c`; otherwise `no-json.c`.

Build outputs:
- Configures `libnvme.h` from `libnvme.h.in`, including fabrics headers conditionally.
- Builds shared library with hidden visibility and version scripts.
- Generates pkg-config metadata.
- Declares `libnvme_dep`.
- Builds `libnvme-test` without version scripts for MI unit tests.
- Installs headers under `nvme`, plus `libnvme-mi.h` when MI is enabled.

Integration role:
- Central source and ABI definition for the libnvme library.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.c

This generated C file provides public accessor functions for fabrics-related libnvme structures.

Accessor groups:
- `struct libnvmf_context`
  - Getters for connection strings: transport, traddr, host_traddr, host_iface, trsvcid, subsysnqn.
  - Setters/getters for queue size, IO/write/poll queue counts, reconnect delay, controller loss timeout, fast I/O fail timeout, keep-alive timeout, ToS.
  - Setters/getters for keyring ID, TLS key ID, configured TLS key ID.
  - Setters/getters for duplicate connect, disable SQ flow, header digest, data digest, TLS, and concat.
  - Setters/getters for default discovery retries and keep-alive timeout.
  - Getters for device, hostnqn, hostid, hostkey, ctrlkey, keyring, TLS key, and TLS key identity.
  - Setter/getter for persistent flag.

- `struct libnvmf_discovery_args`
  - Allocation/free helpers.
  - Default initializer sets max retries to 6 and LSP to `NVMF_LOG_DISC_LSP_NONE`.
  - Setters/getters for max retries and LSP.

- `struct libnvmf_uri`
  - Setters/getters for scheme, protocol, userinfo, host, port, path segments, query, and fragment.
  - String setters free existing values and duplicate new strings.
  - Path segment setter deep-copies a NULL-terminated string array and frees the old array.

Integration role:
- Public ABI layer for generated fabrics accessors.
- Used by C consumers and SWIG/Python binding support.
- Generated from internal structure definitions; comments identify Meson `update-accessors` as regeneration path.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.c -->
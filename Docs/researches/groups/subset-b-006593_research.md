# subset-b-006593 Research

Grouped research for `subset-b-006593`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdrgen -->
# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdrgen

Purpose: Provides the command-line front end for the kernel XDR generator. It translates an XDR specification into Linux-kernel-oriented generated artifacts by dispatching to specialized subcommand modules.

Important APIs and state: `main()` builds an `argparse.ArgumentParser`, registers `definitions`, `declarations`, `lint`, and `source` subcommands, then calls the selected module's `subcmd(args)`. Shared options include `--annotate`, `--language`, `--peer`, and a positional XDR filename; `source` additionally exposes `--no-enum-validation`. The module-level `__version__` is used for `--version`.

Control flow: Startup resolves the script directory, prepends it to `sys.path` so sibling `subcmds` imports work, then also inserts the configured `@pythondir@` path. Runtime is a simple parse-and-dispatch path; `KeyboardInterrupt` and `BrokenPipeError` terminate with status 1.

Dependencies and integration: Depends on `subcmds.definitions`, `subcmds.declarations`, `subcmds.lint`, and `subcmds.source`. It is intended to be installed or configured by build tooling that substitutes `@pythondir@`.

State and persistence: No persistent state is written. The only state is parser configuration, import path mutation, and generated output produced by delegated subcommands.

Risks: The `--language` arguments use `action="store_true"` with default `"C"`, so passing the option stores boolean `True` rather than a language string unless subcommands account for that. Runtime depends on correct install-time substitution of `@pythondir@`. Import path insertion can mask similarly named modules.

Test signals: Exercise `--version`, each subcommand with a minimal XDR spec, missing filename handling, broken pipe behavior, both `--peer` values, annotated output, and `source --no-enum-validation`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdrgen -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/Makefile -->
# sources/distributed-fs/ceph-client/tools/net/ynl/Makefile

Purpose: Top-level build, install, test, lint, and cleanup coordinator for the YNL tooling tree.

Important targets and variables: Includes `../../scripts/Makefile.arch` to derive `LP64`, selects `lib` versus `lib64`, and defines `prefix`, `libdir`, `includedir`, and `SPECDIR`. `SUBDIRS` covers `lib`, `generated`, `ynltool`, and `tests`. `all` builds subdirectories and `libynl.a`; `libynl.a` archives `lib/ynl.o` plus generated user objects.

Control flow: Subdirectory targets recurse only when a local Makefile exists. `tests`, `ynltool`, and `libynl.a` use order-only prerequisites to ensure library and generated code are built first. `install` installs the static archive, public headers under `include/ynl`, the Python package via `pip install --prefix`, and generated/ynltool assets. `schema_check` iterates every YAML netlink spec and validates it through `pyynl/cli.py`.

Dependencies and integration: Integrates the C library, generated protocol bindings, Python `pyynl` package, `ynltool`, test suite, `yamllint`, and documentation netlink specs under `Documentation/netlink/specs`.

State and persistence: Produces local archives, object files, generated artifacts, Python build metadata/cache directories, and installed files under `DESTDIR`.

Risks: `pip install --prefix=$(DESTDIR)$(prefix) .` can interact poorly with distribution packaging or virtualenv policy. The archive depends on generated `*-user.o` files being present. `schema_check` continues through all specs but only reports TAP-like output, so callers must inspect failures unless make exit behavior is added.

Test signals: Run `make`, `make run_tests`, `make schema_check`, `make lint`, `make clean`, `make distclean`, and staged `make DESTDIR=... install` on both LP64 and non-LP64 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/generated/Makefile -->
# sources/distributed-fs/ceph-client/tools/net/ynl/generated/Makefile

Purpose: Generates, compiles, archives, documents, cleans, regenerates, and installs user-space C bindings and RST documentation from YAML netlink specs.

Important targets and variables: `TOOL` points to `../pyynl/ynl_gen_c.py`, `TOOL_RST` to `../pyynl/ynl_gen_rst.py`, and `SPECS_DIR` to `Documentation/netlink/specs`. `GENS` derives from all YAML specs except unsupported `conntrack` and `nftables`; generated outputs include `%-user.h`, `%-user.c`, `%-user.o`, `protos.a`, and `%.rst`. `YNL_GEN_ARG_ethtool` supplies ethtool-specific generation arguments.

Control flow: Pattern rules generate headers and sources from specs, compile source objects with `$(COMPILE.c)`, archive objects into `protos.a`, and generate RST docs. `regen` delegates to `../ynl-regen.sh`. Install targets separately install headers, RSTs, and spec YAML files, with `install` aggregating them.

Dependencies and integration: Includes `../Makefile.deps`, depends on UAPI headers via `-idirafter $(UAPI_PATH)`, and is consumed by the top-level YNL Makefile when building `libynl.a`.

State and persistence: Produces generated `.c`, `.h`, `.o`, `.a`, and `.rst` files, plus installed headers/docs/specs. `distclean` removes generated artifacts while `clean` only removes objects.

Risks: The duplicate `SPECS_PATHS` assignment is harmless but easy to drift. Unsupported specs are hard-coded. `install-specs` copies `Documentation/netlink/*.yaml` as well as specs, so path mistakes affect package contents. Generated code quality depends on the Python generators and current spec schema.

Test signals: Build all generated artifacts, verify ethtool exclusion args, compile with `DEBUG=1`, run `make regen`, run `distclean` followed by `all`, and test staged installs of headers, RSTs, and specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/generated/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/Makefile -->
# sources/distributed-fs/ceph-client/tools/net/ynl/lib/Makefile

Purpose: Builds the reusable C YNL runtime library objects into `ynl.a`.

Important targets and variables: `SRCS` is all local `*.c`, `OBJS` maps those to object files, and generated dependency files `*.d` are included when present. `CFLAGS` select GNU11, optimization, warnings, and optional AddressSanitizer/LeakSanitizer when `DEBUG=1`.

Control flow: The default `all` target builds `ynl.a` from all objects. The `%.o: %.c` rule compiles with `-MMD` so dependency files are emitted next to objects. `clean` removes objects, dependency files, and editor backups; `distclean` additionally removes the archive.

Dependencies and integration: The top-level YNL Makefile consumes `lib/ynl.o` directly for `libynl.a`, while this local archive is useful for standalone consumers and subdirectory builds.

State and persistence: Produces object files, dependency files, and `ynl.a`; no runtime state.

Risks: `SRCS=$(wildcard *.c)` means any new C file is automatically linked into the archive. Sanitizer flags add `-static-libasan`, which can fail on toolchains lacking the static ASan runtime. There is no explicit header install here; header installation is handled by the parent Makefile.

Test signals: Build with default flags and `DEBUG=1`, touch headers to confirm `.d` dependencies rebuild, run `clean` and `distclean`, and verify top-level `libynl.a` still picks up `ynl.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl-priv.h -->
# sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl-priv.h

Purpose: Defines the private C runtime ABI used by generated YNL C bindings and `ynl.c`: policy metadata, parse callbacks, request/dump state, notification metadata, message construction helpers, dump-list traversal internals, and netlink attribute helpers.

Important APIs and types: Core types include `enum ynl_policy_type`, `enum ynl_parse_result`, `struct ynl_policy_attr`, `struct ynl_policy_nest`, `struct ynl_parse_arg`, `struct ynl_req_state`, `struct ynl_dump_state`, and `struct ynl_ntf_info`. It declares `ynl_exec()`, `ynl_exec_dump()`, `ynl_msg_start_req()`, `ynl_msg_start_dump()`, generic-netlink start helpers, parse error helpers, and `__ynl_attr_validate()`.

Control flow: Generated code uses start helpers to build requests, inline `ynl_attr_put_*()` helpers to append attributes, validation helpers while parsing responses, and `ynl_exec()` or `ynl_exec_dump()` to send and receive. Dump results are represented as a linked list whose data payload can be iterated with public macros from `ynl.h`.

State and persistence: `YNL_SOCKET_BUFFER_SIZE` fixes the internal tx/rx buffer size. During construction, `nlmsg_pid` is temporarily repurposed to store the output buffer size or overflow sentinel until `ynl_msg_end()` clears it.

Dependencies and integration: Pulls Linux netlink types through `linux/types.h`; generated family-specific code supplies policy tables and parse callbacks conforming to these structures.

Risks: The inline attribute writers rely on caller discipline around `ynl_msg_end()`. `ynl_attr_get_*()` casts unaligned payloads for small scalars, while 64-bit getters use `memcpy`; portability depends on target alignment behavior. `YNL_ARRAY_SIZE` handles zero-sized arrays defensively but remains macro-sensitive. Overflow signaling through `nlmsg_pid` is a local convention that must not leak to kernel send paths.

Test signals: Attribute put overflow, nested attribute start/end, scalar and string get/put, malformed attribute iteration, dump list empty/nonempty iteration, validation failures for every policy type, and generated-code request/dump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.c

Purpose: Implements the C YNL runtime: socket lifecycle, generic/classic netlink request execution, response and dump parsing, extended ACK annotation, attribute validation, multicast subscription, notification queuing, and dump-list assembly.

Important APIs and state: Public entry points include `ynl_sock_create()`, `ynl_sock_destroy()`, `ynl_subscribe()`, `ynl_socket_get_fd()`, `ynl_ntf_check()`, `ynl_ntf_dequeue()`, and `ynl_ntf_free()`. Generated code uses `ynl_exec()`, `ynl_exec_dump()`, `ynl_gemsg_start_req()`, `ynl_gemsg_start_dump()`, and validation/error helpers. `struct ynl_sock` owns the raw socket, sequence, portid, family id, multicast group cache, tx/rx buffers, and queued parsed notifications.

Control flow: Socket creation allocates one object plus two fixed buffers, opens a netlink socket, enables CAP_ACK and EXT_ACK, binds, records portid and random sequence, then either uses a classic family id or queries generic-netlink family metadata. Request execution finalizes the message, sends it, receives messages until ACK or completion, routes alien async messages to notification parsing, and invokes generated parse callbacks for matching replies. Dump execution allocates one list node per decoded object and terminates the list with `YNL_LIST_END`.

Dependencies and integration: Depends on Linux netlink/genetlink headers, generated family descriptors and parse callbacks, generated policy tables, and kernel generic-netlink controller replies for dynamic families.

State and persistence: Runtime state is in memory only. Multicast groups are cached in `ys->mcast_groups`, notifications are queued as parsed allocations, and error details are reset on each new message. No disk persistence occurs.

Risks: `ynl_get_family_info_cb()` initializes `found_id` to true, so missing family ID may not be reported as intended. `ynl_ntf_parse()` does not check `calloc()` failure before dereferencing the response object. Notification parse failure calls the generated free callback, so generated free functions must tolerate partially initialized objects. Extack path reconstruction depends on request policy and offsets remaining consistent with kernel reports.

Test signals: Socket creation failure paths, missing generic family, multicast group enumeration/subscription, ACK-only requests, kernel extack with bad and missing attributes, malformed replies, interrupted dumps, alien notifications during requests, empty and multi-object dumps, notification dequeue/free, and allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.h -->
# sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.h

Purpose: Public C header for consumers of generated YNL bindings and the C runtime.

Important APIs and types: Defines `enum ynl_error_code`, `struct ynl_error`, opaque-ish generated family metadata `struct ynl_family`, socket wrapper `struct ynl_sock`, and array string helper `struct ynl_string`. Exposes `ynl_sock_create()`, `ynl_sock_destroy()`, `ynl_subscribe()`, `ynl_socket_get_fd()`, `ynl_ntf_check()`, `ynl_ntf_dequeue()`, and `ynl_ntf_free()`. `ynl_dump_foreach()` and `ynl_dump_empty()` support generated dump result traversal.

Control flow: Applications create a socket with a generated `struct ynl_family`, call generated operation wrappers that use the private runtime, inspect `ys->err` on failures, iterate dump lists with `ynl_dump_foreach()`, optionally subscribe/check/dequeue notifications, and destroy the socket to close and free runtime state.

Dependencies and integration: Includes Linux generic netlink and type headers and the private header because generated code needs inline/private definitions. Generated family-specific headers expose typed request/reply structures that embed this runtime ABI.

State and persistence: `struct ynl_sock` stores runtime state including error text, file descriptor, sequence, family id, multicast group table, notification queue, and internal tx/rx buffers. All state is process-local.

Risks: The public header exposes many private fields through `struct ynl_sock`, so source compatibility is weaker than a fully opaque handle. Users must free generated dump responses and notifications according to generated APIs. `ynl_dump_empty()` relies on the sentinel pointer value from `ynl.c`.

Test signals: Compile generated users against installed headers, create/destroy sockets, inspect error propagation from `ynl_sock_create()`, iterate empty and nonempty dumps, use notification subscription/dequeue APIs, and verify ABI assumptions under both static archive and installed-header builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/lib/ynl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyproject.toml -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyproject.toml

Purpose: Defines Python packaging metadata for the `pyynl` package and console scripts.

Important configuration: Uses `setuptools.build_meta` with `setuptools>=61.0`. Project metadata names the package `pyynl`, version `0.0.1`, requires Python `>=3.9`, and depends on `pyyaml==6.*` and `jsonschema==4.*`. Package discovery includes `pyynl` and `pyynl.lib`. Console entry points expose `ynl = pyynl.cli:main` and `ynl-ethtool = pyynl.ethtool:main`.

Control flow: Build frontends read this file to build/install the package. The top-level Makefile invokes `pip install --prefix=... .`, which installs importable modules and script entry points.

Dependencies and integration: Ties the CLI and library to Python package tooling and the YNL Makefile install path. Runtime schema validation depends on the pinned major versions of PyYAML and jsonschema.

State and persistence: Produces build artifacts, package metadata, and installed scripts/modules when invoked by pip; no runtime state.

Risks: `ynl-ethtool` references `pyynl.ethtool`, which must exist in the package tree for installed entry points to work. Exact major-version dependency pins may conflict with system package policies. Package discovery omits deeper package names unless setuptools treats them as included through parent package discovery.

Test signals: `python -m build`, `pip install --prefix`, import `pyynl.lib`, run installed `ynl --help`, run `ynl-ethtool --help` if the module is present, and test with Python 3.9 plus newer supported interpreters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/__init__.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/__init__.py

Purpose: Marks `pyynl` as a Python package.

Important APIs and state: The file is intentionally empty and exports no names. Public imports are provided through `pyynl.lib` and console entry points rather than the package root.

Control flow: Python package import machinery executes this file when `import pyynl` runs; because it is empty, it has no side effects.

Dependencies and integration: Used by setuptools package discovery and by installed console scripts that import modules under `pyynl`.

State and persistence: No runtime state and no persistence.

Risks: Root-level `import pyynl` provides no convenience exports, so users must import from `pyynl.lib` or submodules. This is low risk but should be intentional for API stability.

Test signals: Package discovery includes `pyynl`, `import pyynl` succeeds from an installed wheel or prefix install, and import has no side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/cli.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/cli.py

Purpose: Implements the `ynl` command-line utility for listing specs, validating YAML netlink specs, documenting operations, executing do/dump/multi netlink operations, querying kernel policy, and polling notifications.

Important APIs and state: `main()` owns argument parsing and execution. Helpers include `schema_dir()`, `spec_dir()`, `YnlEncoder`, `print_attr_list()`, `print_mode_attrs()`, and `do_doc()`. CLI groups cover family/spec selection, operations, JSON input/output, notification subscription, extra netlink flags, schema options, and debug controls.

Control flow: The CLI resolves either an installed family spec or explicit spec path, optionally validates through `SpecFamily`, constructs `YnlFamily`, optionally enables small receive debug mode, performs policy queries or listing commands, executes `do`, `dump`, or repeated `--multi` requests, and finally drains notifications when subscribed. Errors from kernel netlink operations are printed and returned as exit status 1.

Dependencies and integration: Imports `YnlFamily`, `Netlink`, `NlError`, `SpecFamily`, `SpecException`, and `YnlException` from `pyynl.lib`. It prefers in-tree schema/spec paths relative to the script and falls back to `/usr/share/ynl`.

State and persistence: No persistent state. Runtime state consists of parsed JSON attributes, an open YNL socket, optional notification subscription, and console output formatting.

Risks: `--policy` can clear `args.do`/`args.dump` after printing policy, so combined options rely on this ordering. Installed specs disable schema validation by default, changing behavior from in-tree specs. `print_attr_list()` recursively expands nests and can produce large output or repeat structures. `--process-unknown` defaults differ between installed family selection and explicit specs.

Test signals: `--list-families`, `--validate`, missing spec error, `--list-ops`, `--list-msgs`, `--list-attrs`, JSON do/dump execution, `--output-json`, repeated `--multi`, all extra netlink flags, policy query mode, notification subscription with finite duration, and `--dbg-small-recv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/__init__.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/__init__.py

Purpose: Public Python library aggregator for YNL spec parsing, runtime netlink access, and documentation generation.

Important APIs and state: Re-exports `SpecAttr`, `SpecAttrSet`, `SpecEnumEntry`, `SpecEnumSet`, `SpecFamily`, `SpecOperation`, `SpecSubMessage`, `SpecSubMessageFormat`, `SpecException`, `YnlFamily`, `Netlink`, `NlError`, `NlPolicy`, `YnlException`, and `YnlDocGenerator`. `__all__` explicitly defines the supported import surface.

Control flow: Importing `pyynl.lib` imports the spec parser, runtime implementation, and doc generator modules, then binds their selected symbols into the package namespace.

Dependencies and integration: Used by `pyynl/cli.py`, likely by generators and external Python consumers that want a stable `from pyynl.lib import ...` entry point.

State and persistence: No direct runtime state. Importing this package may load dependencies such as `yaml`, `socket`, and runtime classes from child modules.

Risks: Because imports are eager, consumers needing only spec parsing still import runtime/socket-related code and doc generator dependencies. Changes to `__all__` are user-visible API changes.

Test signals: `from pyynl.lib import *`, direct import of each listed symbol, package import from installed environment, and static checks that `__all__` matches available names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/doc_generator.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/doc_generator.py

Purpose: Converts Linux netlink YAML specs into generated RST documentation with line-number comments, references, operation sections, definition sections, attribute set sections, multicast groups, and sub-message descriptions.

Important APIs and state: `NumberedSafeLoader` extends PyYAML safe loading by adding `__lineno__` to mappings. `RstFormatters` provides formatting helpers for fields, definitions, bullets, sections, labels, refs, titles, and line-number comments. `YnlDocGenerator` exposes `parse_yaml_file()` and parsing helpers for multicast groups, do/dump blocks, operation attributes, operations, definitions, attribute sets, sub-messages, and whole YAML documents.

Control flow: `parse_yaml_file()` loads YAML with line numbers, then `parse_yaml()` emits a document header, label, title, contents directive, optional summary, operations, multicast groups, definitions, attribute sets, and sub-messages. Nested helpers skip preprocessed/internal keys and convert recognized references to RST `:ref:` links.

Dependencies and integration: Depends on PyYAML and the netlink spec schema conventions. It is likely invoked by `ynl_gen_rst.py` and the generated Makefile's `%.rst` rule.

State and persistence: No persistent state. Output is a generated RST string; writing is handled by callers.

Risks: Formatting assumes many YAML keys exist, such as operation docs and attribute list names. `rst_ref()` uses fixed prefix mappings, so new spec sections need updates for correct cross-linking. The line-number loader mutates every mapping with `__lineno__`, requiring all parsers to skip that key consistently.

Test signals: Generate RST for specs with operations, do/dump replies, events, multicast groups, enums, structs, nested attribute sets, sub-messages, missing optional docs, multi-line docs, and check Sphinx reference validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/doc_generator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/nlspec.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/nlspec.py

Purpose: Provides the Python object model and resolver for YAML netlink specifications used by YNL generators, CLI validation, and the Python runtime.

Important APIs and types: Core classes include `SpecElement`, `SpecEnumEntry`, `SpecEnumSet`, `SpecAttr`, `SpecAttrSet`, `SpecStructMember`, `SpecStruct`, `SpecSubMessage`, `SpecSubMessageFormat`, `SpecOperation`, `SpecMcastGroup`, and `SpecFamily`. `SpecFamily` exposes parsed dictionaries for `attr_sets`, `sub_msgs`, `msgs`, `req_by_value`, `rsp_by_value`, `ops`, `ntfs`, `consts`, `mcast_groups`, and `kernel_family`.

Control flow: `SpecFamily` reads and validates the SPDX-tagged YAML spec, optionally validates it against a schema, initializes collections, and then resolves elements through an iterative `_resolution_list`. `resolve()` constructs constants, attribute sets, sub-messages, operations under either unified or directional enum models, request/response lookup maps, async notification maps, and multicast groups. `SpecOperation.resolve()` derives its attribute set directly or through a referenced notification target.

Dependencies and integration: Depends on PyYAML and lazily imports `jsonschema` only when schema validation is enabled. It is subclassed by `YnlFamily` in `ynl.py` and consumed by code/doc generators.

State and persistence: All state is in-memory representation of a spec. It does not write files or keep external handles open.

Risks: Resolution retries catch `KeyError` and `AttributeError`; a real bug can look like an unresolved dependency until no progress is made. Directional operation ID handling is subtle, especially notifications/events and request/reply value overrides. Attribute-set subsets merge dictionaries with `real_attr.yaml | elem`, so override precedence must remain intentional.

Test signals: Specs with and without schema validation, missing SPDX tag, unified and directional enum models, explicit operation values, excluded ops regexes, subset attribute sets, structs, flags/enums, sub-message selectors, notifications referencing other messages, multicast groups, and unresolved-reference failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/nlspec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/ynl.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/ynl.py

Purpose: Implements the Python YNL runtime for generic and raw netlink: message encoding/decoding from YAML specs, socket setup, policy introspection, do/dump/multi operation execution, extack annotation, multicast subscription, and notification polling.

Important APIs and state: Public classes include `YnlFamily`, `Netlink`, `NlError`, `NlPolicy`, `YnlException`, and `ConfigError`. Message helpers include `NlAttr`, `NlAttrs`, `NlMsg`, `NlMsgs`, `GenlMsg`, `NetlinkProtocol`, `GenlProtocol`, and `SpaceAttrs`. `YnlFamily` subclasses `SpecFamily`, binds operation names as methods, owns a netlink socket, tracks async response ids, and queues decoded notifications.

Control flow: Initialization parses the spec, resolves protocol ids through generic-netlink controller or raw protocol config, creates a netlink socket, enables CAP_ACK, EXT_ACK, and strict checking, and binds convenience operation methods. `_encode_message()` builds netlink/genetlink headers, optional fixed headers, and attributes. `_ops()` batches one or more requests, sends them, receives replies until all sequences complete, decodes matching responses, queues async notifications, raises `NlError` on kernel errors, and returns normalized single/dump/multi results.

Dependencies and integration: Depends on Python `socket`, `struct`, `selectors`, `queue`, `ipaddress`, `uuid`, the spec model from `nlspec.py`, and kernel netlink/generic-netlink controller support.

State and persistence: Maintains a live socket, receive size/debug flags, async message id set, and `Queue` of decoded notifications. No disk persistence occurs.

Risks: Attribute encoding/decoding covers many spec forms, making selector scope and sub-message resolution high-risk areas. `_encode_struct()` mutates the `vals` dictionary via `pop()`, which can surprise callers when fixed headers are used. `NlMsgs` advances by `nl_len` without explicit alignment, so malformed multi-message buffers can desynchronize parsing. Receive buffer truncation is user-controllable through debug options but guarded to at least about one page.

Test signals: Generic and raw family initialization, do/dump/multi operations, fixed headers, nested attributes, indexed arrays, multi-attrs, enums/flags including unknowns, auto scalars, bitfield32, display hints for MAC/IP/hex/UUID, sub-messages, extack bad-attribute paths, policy queries, notification subscribe/check/poll, small receive debug mode, kernel errors, and malformed attribute buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/ynl.py -->

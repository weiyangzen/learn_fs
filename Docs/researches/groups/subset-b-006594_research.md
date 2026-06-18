# Research: subset-b-006594

Grouped research for YNL generator, YNL tests, YNL utility, and objtool build files. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_c.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_c.py

Purpose: this is the main YAML Netlink (YNL) to C generator. It emits userspace bindings, kernel policy/operation tables, and UAPI headers from `tools/net/ynl` YAML specs. It extends parser classes from `pyynl/lib` (`SpecFamily`, `SpecAttrSet`, `SpecAttr`, `SpecOperation`, `SpecEnumSet`, `SpecEnumEntry`, `SpecSubMessage`) with C naming, validation, layout, and rendering behavior.

Important APIs and types: helper functions `c_upper()`, `c_lower()`, and `limit_to_number()` normalize names and validation constants. The `Type` hierarchy models attribute encoders/decoders and policies: scalar, flag, string, binary, binary struct, scalar arrays, bitfield32, nest, multi-attr, indexed-array, nest-type-value, and sub-message. `Struct` models generated C structures and nested attribute sets. `EnumSet` and `EnumEntry` render enum names/ranges. `Family` resolves the whole spec, discovers root/nested sets, selector passing, notification relationships, hooks, and kernel policy mode. `RenderInfo` carries per-operation context. `CodeWriter` owns indentation, temporary output files, compare-output avoidance, function prototypes, structs, and preprocessor blocks.

Control flow: `main()` parses `--mode {user,kernel,uapi}`, `--spec`, `--header/--source`, optional excluded ops, extra user headers, and function prefix. It builds a `Family`, verifies the license, emits the generated-file banner, includes, scoped constants, then dispatches by mode. UAPI mode calls `render_uapi()`. Kernel header/source mode emits netlink policies, range/sparse validators, operation tables, multicast groups, and `genl_family` definitions. User header/source mode emits public request/reply structs, setters, free helpers, parsers, put functions, dump/list wrappers, notification wrappers, enum string maps, typol policy tables, and the `ynl_<family>_family` descriptor.

State and persistence: generator state is mostly in-memory spec-derived objects. `CodeWriter` writes to stdout or to a temporary file and only replaces the destination when content differs under `--cmp-out`; this reduces rebuild churn. Generated userspace code persists heap-allocated strings, binary blobs, arrays, nested structures, dump lists, and notifications, so the generated free paths are a core correctness surface. `Family.resolve()` mutates YAML-derived operation entries by mocking events as do replies and annotating request/reply use.

Dependencies and integration: depends on PyYAML, `pyynl/lib`, Linux netlink headers, generated YNL runtime APIs (`ynl_*`, `ynl_attr_*`, `ynl_exec*`), kernel generic-netlink structs, and the source tree layout detected by `find_kernel_root()`. It integrates with `ynl-regen.sh` through `/* YNL-GEN ... */` and `/* YNL-ARG ... */` markers.

Risks: many branches raise generic exceptions for unsupported schema combinations, so schema evolution can fail late during generation. Memory ownership is hand-emitted C; missing allocation checks, duplicated multi-attrs, recursive nests, selector forwarding, and list frees are high-risk areas. Policy generation has mode-specific differences (`global`, `per-op`, `split`) that can diverge from kernel expectations. Test signals include rebuilding generated headers/sources, `--cmp-out` idempotence, YNL C selftests, and compiling generated kernel/user outputs with sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_c.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_rst.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_rst.py

Purpose: command-line generator for RST documentation from YNL YAML specs. It is intentionally thin: validate arguments, invoke `YnlDocGenerator`, and write the generated text.

Important APIs/functions: `parse_arguments()` handles `--verbose`, `--output`, and mutually exclusive `--input`; it rejects missing output and non-file input. `write_to_rstfile()` writes UTF-8 content. `main()` constructs `YnlDocGenerator`, calls `parse_yaml_file()` for the input spec, catches broad parser failures, logs warnings, and exits with `-1`.

Control flow and state: no persistent state beyond the output file. Existing output is overwritten after a debug log. Verbose mode configures root logging to `DEBUG`.

Dependencies and integration: imports `YnlDocGenerator` from the sibling `pyynl/lib` package and depends on filesystem paths supplied by callers. It is part of the Linux YNL documentation toolchain and should be run from scripts or docs builds that provide a YAML spec and destination RST.

Risks and tests: the CLI currently defines only an input/output path, not an index mode despite a comment mentioning index/input. It catches all exceptions, which keeps CLI output simple but can hide exact stack traces unless verbose logging is used. Test signals are successful RST generation for representative YAML specs, missing-output rejection, invalid input rejection, and UTF-8 write verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_rst.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/Makefile -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/Makefile

Purpose: builds and installs YNL selftests and helper demos. It compiles C tests against `../lib/ynl.a` and `../generated/protos.a`, exposes shell wrappers as `TEST_PROGS`, and installs into the kselftest layout.

Important build variables: `CFLAGS` enables GNU11, warnings, shadow checks, YNL/lib/generated include paths, selftest headers, and UAPI include fallback. Unless `NDEBUG=1`, address and leak sanitizers plus debug info are enabled. `LDLIBS` links the generated protocol archive and YNL runtime.

Control flow: `all` builds `TEST_GEN_PROGS` (`netdev`, `ovs`, `rt-link`, `tc`) and `TEST_GEN_FILES` (`devlink`, `ethtool`, `rt-addr`, `rt-route`). Pattern rules compile each `%.c` to `%.o` then link. `run_tests` executes shell tests. `install` copies binaries, helper Python/shell files, rewrites wrapper paths for installed tools, and emits `kselftest-list.txt`.

Dependencies/integration: includes `../Makefile.deps`, depends on generated protocol headers, kselftest `ktap_helpers.sh`, and target kernel features described by `tests/config`.

Risks/test signals: sanitizer/static-libasan may fail on hosts without the runtime. Generated header drift breaks compile quickly. Install path rewriting must stay aligned with wrapper variable names. The primary signal is `make -C tools/net/ynl/tests run_tests` or kselftest execution under a kernel with required networking modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/config -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/config

Purpose: kselftest kernel configuration fragment for YNL networking tests. It records the minimum modules/features expected by shell wrappers and C tests.

Important entries: enables network namespaces, IPv6, netdevsim, veth, netkit, Open vSwitch, dummy, routing/diagnostic support, and traffic-control qdisc/classifier/action modules such as ingress, fq_codel, flower, vlan action, and generic classifier/action support.

Control flow/state: declarative only; no runtime behavior. Its state affects whether test environments can load modules and create links/qdiscs/routes required by the wrappers.

Dependencies/integration: consumed by the kernel selftest config machinery and mirrors assumptions in `ynl_nsim_lib.sh`, `test_ynl_cli.sh`, `test_ynl_ethtool.sh`, `tc.c`, `rt-link.c`, and route/address tests.

Risks/test signals: missing `CONFIG_NETDEVSIM`, `CONFIG_NET_NS`, or `CONFIG_VETH` causes broad skips/failures. Missing TC modules affects `tc.c`; missing Open vSwitch affects `ovs.c`; missing netkit affects `rt-link.c`. Successful module load and namespace setup are the main early signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.c

Purpose: C kselftest for generated devlink YNL bindings. It validates dump and info-get paths against available devlink devices, usually provided by the netdevsim wrapper.

Important APIs/functions: fixture `devlink` opens `ynl_sock_create(&ynl_devlink_family, NULL)` and destroys it. `TEST_F(devlink, dump)` calls `devlink_get_dump()`, iterates with `ynl_dump_foreach`, and verifies `bus_name` and `dev_name` lengths. `TEST_F(devlink, info)` allocates `devlink_info_get_req`, sets bus/dev name, calls `devlink_info_get()`, checks driver name and prints running firmware versions.

Control flow/state: tests skip if dumps are empty. Request objects and response/list objects are allocated and freed with generated helpers. The socket holds any YNL error state used in failure logs.

Dependencies/integration: includes `devlink-user.h`, `ynl.h`, and kselftest harness. Shell wrapper `devlink.sh` creates netdevsim before running this binary.

Risks/test signals: depends on at least one devlink-capable device. It checks presence metadata and nested multi-attr parsing for firmware versions. Failures usually indicate generated request setters, dump list parsing, string allocation, or devlink kernel support regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.sh

Purpose: shell wrapper for the devlink C selftest. It prepares a netdevsim device through the shared helper and then executes the local `devlink` binary.

Important flow: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, then runs `$(dirname realpath "$0")/devlink`.

State/dependencies: setup creates `/sys/bus/netdevsim/new_device`, renames the simulated netdev to `nsim0`, assigns IPv4/IPv6 addresses, and installs cleanup via trap. Requires root privileges, `netdevsim`, `ip`, `udevadm`, and the compiled test binary.

Risks/test signals: failures before binary execution are environment/setup issues, not generated devlink binding issues. A successful wrapper proves the test has a deterministic devlink device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.c

Purpose: C selftest for generated ethtool YNL dump bindings, focused on channel and ring queries.

Important APIs/functions: fixture opens `ynl_ethtool_family`. `channels` builds an empty-header dump request (`_present.header = 1`), calls `ethtool_channels_get_dump()`, verifies each entry has `header.dev_name`, and expects at least one RX/TX/combined count. `rings` similarly calls `ethtool_rings_get_dump()` and expects RX or TX ring values.

Control flow/state: empty dumps are skipped. Request structs are stack allocated because they contain only presence metadata and nested header state; returned lists are heap-owned and freed with generated list free helpers.

Dependencies/integration: uses generated `ethtool-user.h`, YNL runtime, kselftest, and wrapper `ethtool.sh` which provides netdevsim.

Risks/test signals: ethtool requires an explicit empty `header` nest, so this test is a good signal for nested presence encoding. It also checks generated dump list parsing and nested header strings. Kernel/device support may cause skips or failures independent of codegen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.py -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.py

Purpose: Python ethtool-like utility built on pyYNL. It exercises real user workflows through `YnlFamily` and serves as both a demo and a test target for `test_ynl_ethtool.sh`.

Important APIs/functions: `args_to_req()` validates CLI attr/value pairs against `operation_do_attributes()` and fills requests. `do_set()` and `do_get()` wrap YNL doit calls with ethtool `header.dev-name`. `bits_to_dict()` converts YNL bitset replies into name/value maps. `print_field()` and `print_speed()` provide human output. `main()` maps many ethtool flags to YAML operation names, including EEE, pause, coalesce, features, channels, rings, stats, timestamping, and default device info.

Control flow/state: argparse produces one mode flag plus a device and trailing attr/value args. The utility constructs `YnlFamily(spec_dir()/ethtool.yaml, schema_dir()/genetlink-legacy.yaml)`, optionally enables small receive debug mode, performs one or more YNL `do()` calls, and prints either Python pretty-printed dicts under `--json` or ethtool-like text.

Dependencies/integration: imports sibling `pyynl/cli.py` directory helpers and `YnlFamily`. It depends on kernel ethtool genetlink support and on operation/attribute names matching the YAML spec.

Risks/test signals: some set paths and bitmask parsing are TODOs. The `--show-ring` path appears to call `channels-get` while printing ring fields, a likely behavioral bug or stale operation name. Shell tests check representative show/set commands under netdevsim and veth namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.sh

Purpose: shell wrapper for the compiled ethtool C selftest. It prepares netdevsim through the shared helper and executes the `ethtool` binary in the tests directory.

Control flow/state: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, then runs the binary by absolute script-relative path. Cleanup is delegated to the helper trap.

Dependencies/integration: requires root/network privileges, `netdevsim`, `ip`, `udevadm`, and a compiled `ethtool` test. It aligns with `tests/config` entries for netdevsim, IPv6, and net namespaces.

Risks/test signals: setup failures should be interpreted separately from generated ethtool binding failures. Successful wrapper setup provides a device for `ethtool.c` dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/netdev.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/netdev.c

Purpose: C selftest for generated netdev YNL bindings, including dump, single get, and multicast notification handling.

Important APIs/functions: `netdev_print_device()` validates `ifindex`, resolves names with `if_indextoname()`, and prints XDP/XSK feature bit strings using generated enum-to-string helpers. `veth_create()` and `veth_delete()` use generated `rt-link` bindings to create/delete veth devices and optionally consume echo notifications. Fixture opens `ynl_netdev_family`; notification test also opens `ynl_rt_link_family`.

Control flow: `dump` iterates `netdev_dev_get_dump()`. `get` selects an ifindex from a dump, builds `netdev_dev_get_req`, and queries it. `ntf_check` subscribes to `mgmt`, creates a veth through rtnetlink, calls `ynl_ntf_check()`, dequeues notifications, drains leftovers, deletes the veth, and asserts one netdev notification arrived.

State/dependencies: socket notification queues, generated heap requests/responses, and kernel netdev state are central. Requires netdev family support, rtnetlink generated bindings, and permission to create links.

Risks/test signals: validates generated notification wrappers, enum string maps, dump lists, and cross-family integration. Risk areas include missed cleanup if veth creation succeeds but notification handling fails, and environment-dependent notification timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ovs.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ovs.c

Purpose: C selftest for Open vSwitch datapath generated YNL bindings, covering create, get, dump, and cleanup.

Important APIs/functions: fixture opens `ynl_ovs_datapath_family` and tracks `dp_name`. `ovs_print_datapath()` validates datapath name and header ifindex and prints pid/cache fields. `TEST_F(ovs, crud)` creates datapath `ynl-test`, gets it by name, verifies the returned name, dumps all datapaths, and confirms the new one appears.

Control flow/state: teardown deletes `self->dp_name` if set, using generated delete request helpers. Request and response objects are heap allocated through generated alloc/free APIs. Kernel OVS datapath state is persistent until teardown.

Dependencies/integration: includes `ovs_datapath-user.h`, YNL runtime, kselftest harness, and requires Open vSwitch kernel support/module with sufficient privileges.

Risks/test signals: if creation succeeds but teardown cannot allocate/delete, state may remain. Strong signals include fixed-header parsing (`dp_ifindex`), string setters, CRUD operation tables, and dump list iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ovs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.c

Purpose: rtnetlink address dump selftest for generated `rt-addr` bindings.

Important APIs/functions: `rt_addr_print()` resolves interface names, validates address length is IPv4 or IPv6, and formats addresses with `inet_ntop()`. Fixture opens `ynl_rt_addr_family`. `dump` allocates a getaddr dump request, calls `rt_addr_getaddr_dump()`, and searches for addresses configured by the wrapper: `192.168.1.1` and `2001:db8::1`.

Control flow/state: expected addresses are encoded with `inet_pton()`. The returned dump list is iterated and freed. Kernel interface address state is established outside the binary by `rt-addr.sh`/`ynl_nsim_lib.sh`.

Dependencies/integration: depends on rtnetlink address YAML-generated headers, YNL runtime, kselftest, IPv4/IPv6 support, and netdevsim setup.

Risks/test signals: tests binary blob parsing, fixed `ifaddrmsg` header fields, address length metadata, and dump completeness. Failure to find addresses may be setup, namespace, or parsing related.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.sh

Purpose: wrapper for the `rt-addr` C selftest. It creates the netdevsim device and configured addresses needed by `rt-addr.c`.

Control flow/state: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, and runs the local `rt-addr` binary. The helper installs cleanup for the netdevsim device.

Dependencies/integration: needs root privileges, netdevsim, IPv6, `iproute2`, `udevadm`, and the compiled test binary. The helper assigns exactly the IPv4/IPv6 addresses that the C test searches for.

Risks/test signals: if the wrapper succeeds but the C test misses addresses, likely signals generated rtnetlink address parsing or dump filtering problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-link.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-link.c

Purpose: rtnetlink link selftest for generated `rt-link` bindings, including dump parsing, netkit link creation, nested type-value data, and extack path rendering.

Important APIs/functions: `rt_link_print()` formats link attributes, alternate names, link kind, and nested netkit data/policy. `netkit_create()` builds a `newlink` request with `NLM_F_CREATE | NLM_F_ECHO`, kind `netkit`, and generated netkit policy setter; it consumes `RTM_NEWLINK` notification to return ifindex. `netkit_delete()` deletes by ifindex.

Control flow: `dump` allocates and performs `getlink` dump. `netkit` creates a netkit link, dumps links, finds the returned ifindex, prints it, then deletes it. `netkit_err_msg` intentionally sends invalid policy `10` and asserts the YNL error message contains the nested bad-attribute path.

State/dependencies: mutates kernel link state and uses generated request/free helpers. Requires netkit support and permissions. The error-message test depends on kernel extack wording/path stability.

Risks/test signals: strong coverage for sub-message/nested selector generation, notification wrappers, nlmsg flags setters, and bad attribute path construction. Cleanup risk exists if deletion is skipped after intermediate assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.c

Purpose: rtnetlink route dump selftest for generated `rt-route` bindings.

Important APIs/functions: `rt_route_print()` ignores local-table routes, optionally resolves output interface, formats destination and gateway binary addresses with `inet_ntop()`, and uses header fields such as family/table/dst length. Fixture opens `ynl_rt_route_family`.

Control flow/state: `dump` expects connected routes from wrapper-provided addresses: `192.168.1.0/24` and `2001:db8::/64`. It allocates `rt_route_getroute_req_dump`, performs dump, iterates all non-local routes, and sets found flags based on address length, prefix length, and `memcmp()`.

Dependencies/integration: requires route YAML-generated bindings, YNL runtime, IPv4/IPv6, kselftest, and netdevsim setup from `rt-route.sh`.

Risks/test signals: validates fixed `rtmsg` headers, binary route attributes, dump list handling, and route table filtering. Environment route noise is tolerated except local table routes. Failure can reflect missing setup addresses or generated parser regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.sh

Purpose: wrapper for route dump testing. It prepares the netdevsim interface and addresses that induce connected routes, then runs the `rt-route` binary.

Control flow/state: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, and executes the script-relative `rt-route` binary. Netdevsim cleanup is handled by the helper trap.

Dependencies/integration: requires root/network admin privileges, netdevsim, IPv6, iproute2, and compiled YNL test binary. It pairs directly with the expected route prefixes in `rt-route.c`.

Risks/test signals: wrapper success plus C failure points to route dump/parsing or kernel route behavior. Wrapper failure is usually missing module or permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/tc.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/tc.c

Purpose: traffic-control selftest for generated `tc` bindings. It validates qdisc CRUD, flower filter creation, indexed actions, nested options, and fixed-header handling.

Important APIs/functions: printing helpers decode qdisc kind/options, fq_codel stats, VLAN/gact action names, flower attributes, and filter options. `tc_clsact_add()`/`tc_clsact_del()` manage clsact qdisc. `tc_filter_add()` builds a flower filter with VLAN keys and an indexed action array, intentionally leaving index 0 unused to match TC action ordering. `tc_filter_del()` removes it.

Control flow/state: fixture unshares a new network namespace, uses loopback ifindex 1, and opens `ynl_tc_family`. `qdisc` adds `fq_codel`, dumps qdiscs, expects fq_codel data, then deletes it. `flower` adds clsact, creates a flower filter, dumps ingress filters, verifies VLAN id/priority, then deletes filter and qdisc.

Dependencies/integration: requires TC qdisc/classifier/action kernel support from `tests/config`, YNL generated `tc-user.h`, kselftest, and network namespace privileges.

Risks/test signals: complex generated-code coverage includes indexed arrays, binary structs, nested sub-options, endian fields, and action arrays. Cleanup paths matter because qdiscs/filters are namespace-local but can affect subsequent assertions. Unsupported clsact is skipped, while filter add failures are hard failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_cli.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_cli.sh

Purpose: KTAP shell selftest for the generic Python YNL CLI (`pyynl/cli.py`). It validates family listing and operations across netdev, ethtool, rtnetlink route/address/link/neigh/rule, and nlctrl.

Important functions: `cli_list_families`, `cli_netdev_ops`, `cli_ethtool_ops`, `cli_rt_route_ops`, `cli_rt_addr_ops`, `cli_rt_link_ops`, `cli_rt_neigh_ops`, `cli_rt_rule_ops`, and `cli_nlctrl_ops` each run CLI commands and assert output with grep or command exit status. `setup()` loads netdevsim, creates a temporary netns, adds a netdevsim device, renames it, brings it up, and creates a veth pair. `cleanup()` removes the device and namespace.

Control flow/state: the script checks the CLI path, traps cleanup, prints KTAP header, runs setup, sets a fixed plan, then executes all tests. It mutates netns routes, addresses, links, neighbors, and rules and performs best-effort deletion after each case.

Dependencies/integration: needs kselftest `ktap_helpers.sh`, root privileges, iproute2, netdevsim, veth, and relevant YNL YAML families.

Risks/test signals: grep-based assertions are broad but good integration smoke tests. Family availability gates skip some rtnetlink cases. Cleanup failures can leave namespace state until trap. Strong signal for JSON request parsing, create flags, dump/do modes, and installed-vs-tree CLI path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_cli.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_ethtool.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_ethtool.sh

Purpose: KTAP shell selftest for the Python `ethtool.py` YNL utility. It exercises human-facing show/set paths under a temporary namespace with netdevsim and veth devices.

Important functions: `ethtool_device_info`, `ethtool_statistics`, `ethtool_ring_params`, `ethtool_coalesce_params`, `ethtool_pause_params`, `ethtool_features_info`, `ethtool_channels_info`, and `ethtool_time_stamping` run the utility and validate output or set-command success. `setup()` mirrors the CLI test setup with netdevsim ID 1337 and a veth pair; `cleanup()` removes both.

Control flow/state: validates tool existence, traps cleanup, prints KTAP plan, sets up devices, then runs eight tests. Some tests mutate ethtool state on netdevsim (`set-ring`, `set-coalesce`, `set-pause`, `set-channels`) without restoring original values.

Dependencies/integration: requires root, netdevsim, veth, iproute2, kselftest helpers, and ethtool genetlink support exposed through pyYNL.

Risks/test signals: output matching is intentionally loose, so it is a smoke/integration test rather than exact formatting validation. Mutating settings can fail depending on driver support. It is a good signal for `ethtool.py` argument-to-request conversion and common operation names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_ethtool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/wireguard.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/wireguard.c

Purpose: small command-line demo/test for generated WireGuard YNL bindings. It dumps a WireGuard device by ifindex or ifname and prints peers and allowed IPs.

Important APIs/functions: `build_request()` parses the argument as positive integer ifindex using `strtol()` or falls back to ifname setter. `print_allowed_ip()` formats IPv4/IPv6 allowed IPs. `print_peer_header()` prints 32-byte public keys in hex. `print_peer()` prints peer counters and iterates `allowedips`.

Control flow/state: `main()` requires one argument, creates a YNL socket for `ynl_wireguard_family`, allocates a request, performs `wireguard_get_device_dump()`, iterates devices and nested peers, frees list/request/socket, and returns distinct error codes for usage, socket, and dump failures.

Dependencies/integration: includes generated `wireguard-user.h`, YNL runtime, and libc networking helpers. Requires kernel WireGuard generic netlink family and an existing device.

Risks/test signals: public key formatting is explicitly not constant-time and is only for display. It covers nested multi-attrs (`peers`, `allowedips`), binary key lengths, ifname/ifindex setters, and dump list frees. No kselftest harness or setup wrapper is provided in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/wireguard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ynl_nsim_lib.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ynl_nsim_lib.sh

Purpose: shared shell helper for YNL C test wrappers that need a deterministic netdevsim device.

Important functions/state: globals define `NSIM_ID=1337`, `NSIM_DEV`, and `KSFT_SKIP=4`. `nsim_cleanup()` writes the ID to `/sys/bus/netdevsim/del_device` and ignores failures. `nsim_setup()` loads netdevsim, verifies `/sys/bus/netdevsim/new_device`, installs cleanup trap, creates one port, waits for udev, discovers the netdev name, renames it to `nsim0`, brings it up, and assigns IPv4 `192.168.1.1/24` plus IPv6 `2001:db8::1/64 nodad`.

Dependencies/integration: sourced by `devlink.sh`, `ethtool.sh`, `rt-addr.sh`, and `rt-route.sh`. Requires root privileges, `modprobe`, `udevadm`, `ip`, netdevsim, IPv4, and IPv6.

Risks/test signals: fixed global ID can conflict with parallel tests or stale devices. Cleanup is best effort. It does not create a separate network namespace, so tests run in the caller namespace. Successful setup is a prerequisite for address/route/devlink/ethtool tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/tests/ynl_nsim_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynl-regen.sh -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynl-regen.sh

Purpose: regeneration helper for files containing YNL generation markers. It finds generated C/header/UAPI outputs and reruns `pyynl/ynl_gen_c.py` with the recorded mode, header/source kind, spec, and optional arguments.

Important flow: parses `-f` to force and `-p <path>` to search outside the kernel root. Computes `TOOL` relative to itself and `KDIR` as the kernel root. Inside the search directory, `git grep` finds files matching `/* YNL-GEN kernel|uapi|user */`; a second grep/sed extracts the spec path and generation parameters, and `YNL-ARG` lines supply extra args. Files newer than their YAML spec are skipped unless forced. Generation uses `--cmp-out` to avoid rewriting identical output.

State/dependencies: depends on git, sed, bash arrays, generated marker comments, and source tree layout. It writes generated files in place.

Risks/test signals: marker parsing assumes the expected comment shape and parameter positions. Search under a non-git or shallow tree fails. Good signals are idempotent reruns with no changed files and successful forced regeneration after spec edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynl-regen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/Makefile -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/Makefile

Purpose: builds and installs the C `ynltool` utility from all `*.c` files in the directory.

Important build variables: includes `../Makefile.deps`, uses `gcc`, `-Wall -Wextra -Werror -O2`, optional sanitizer/debug flags under `DEBUG=1`, include paths for YNL lib/generated headers and UAPI, and `SRC_VERSION` derived from the kernel Makefile. `OBJS` honors `OUTPUT`, and `YNLTOOL` is `$(OUTPUT)ynltool`.

Control flow: `all` builds `ynltool`. The link rule depends on `../libynl.a` and object files, linking with `-lm`. Pattern rule compiles with dependency output. The lib rule delegates to the parent YNL Makefile. `install` copies the binary to `$(DESTDIR)$(bindir)/$(YNLTOOL)`.

Dependencies/integration: compiles `main.c`, `page-pool.c`, `qstats.c`, and `json_writer.c` against generated `netdev-user.h` and YNL runtime.

Risks/test signals: `-Werror` makes compiler-version warnings fatal. The install destination appends `$(YNLTOOL)`, so non-empty `OUTPUT` can affect the installed filename if not normalized by callers. Successful `make` and `ynltool version` are basic signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.c

Purpose: simple streaming JSON writer used by `ynltool` for machine-readable output. It handles separators, nesting depth, optional pretty indentation, string escaping, and primitive values.

Important APIs/functions: `jsonw_new()` allocates state with output file, depth, pretty flag, and separator. `jsonw_destroy()` asserts all collections are closed, writes a newline, flushes, frees, and nulls the caller pointer. `jsonw_begin()`/`jsonw_end()` back arrays/objects. `jsonw_name()` writes object property names. Primitive emitters include string, bool, null, float, uint, unsigned short, unsigned long long, and int variants; field helpers combine name and value.

Control flow/state: state is per-writer and tracks only current depth and whether a comma is due. Pretty mode controls newlines/indentation. Strings escape common JSON control characters, backslash, and quote.

Dependencies/integration: used through global `json_wtr` in `ynltool/main.c`, `page-pool.c`, and `qstats.c`.

Risks/test signals: callers must balance start/end calls or assertions fire. `jsonw_printf()` can emit raw invalid JSON if callers pass non-JSON text. String escaping does not handle all control characters or UTF-8 validation. Signals are valid JSON output from all `--json` subcommands and assertion-free shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.h -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.h

Purpose: public header for the `ynltool` streaming JSON writer. It exposes an opaque `json_writer_t` and the functions implemented in `json_writer.c`.

Important APIs/types: declares lifecycle (`jsonw_new`, `jsonw_destroy`), formatting (`jsonw_pretty`, `jsonw_reset`), object names (`jsonw_name`), primitive emitters, field helpers, and collection delimiters. `format(printf)` attributes are applied to printf-style functions to catch format mismatches at compile time.

State/dependencies: no state in the header beyond the opaque typedef. Includes standard bool, integer, varargs, and stdio headers. A `jsonw_err_handler_fn` typedef is declared but not used by the implementation in this subset.

Integration: included by `main.h`, which makes JSON writer globals available to ynltool subcommands.

Risks/test signals: header and implementation must remain synchronized; missing prototypes would be caught by `-Wmissing-prototypes`/`-Werror` build settings. JSON validity is tested through consumers of the API rather than the header itself.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.c

Purpose: top-level CLI dispatcher and global output/error handling for `ynltool`.

Important APIs/functions: globals track `bin_name`, last command context for `usage()`, JSON writer, and output flags. `clean_and_exit()` closes JSON output before exiting. `do_help()` and `do_version()` support root commands. `cmd_select()` dispatches by prefix across `struct cmd` tables. `is_prefix()` and `detect_common_prefix()` implement abbreviated command matching and ambiguity reporting. `p_err()` and `p_info()` route errors/info to JSON or stderr.

Control flow: `main()` parses `--json`, `--pretty`, `--help`, and `--version` via `getopt_long`, initializes JSON output lazily, adjusts argc/argv, then calls `do_version()` or `cmd_select()` over root commands (`help`, `page-pool`, `qstats`, `version`). JSON writer is destroyed before return.

State/dependencies: global JSON mode affects all subcommands. Last-command globals let `usage()` call the current subcommand help. Depends on `json_writer`, `page-pool`, and `qstats` modules.

Risks/test signals: prefix matching can select the first matching command unless subcommands call ambiguity checks. `p_err()` can emit multiple JSON objects if multiple errors occur. Signals are `ynltool help`, `version`, JSON/pretty output, invalid option handling, and subcommand dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.h -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.h

Purpose: shared header for `ynltool` modules. It defines command parsing macros, shared globals, diagnostics, and subcommand entry points.

Important APIs/macros: `NEXT_ARG`, `NEXT_ARGP`, `GET_ARG`, `BAD_ARG`, and `REQ_ARGS` mutate argc/argv and call `usage()` or `p_err()` on bad input. `HELP_SPEC_OPTIONS` documents JSON flags. `struct cmd` is the dispatch table shape used by `cmd_select()`. It declares `p_err`, `p_info`, `is_prefix`, `detect_common_prefix`, `usage`, `do_page_pool`, and `do_qstats`.

State/dependencies: exposes global `bin_name`, `json_wtr`, `json_output`, and `pretty_output` for subcommands. Includes `json_writer.h` and standard headers, and defines `_GNU_SOURCE` if absent.

Integration: included by `main.c`, `page-pool.c`, and `qstats.c`.

Risks/test signals: argument macros have side effects and assume local variables named `argc`/`argv`; misuse can skip arguments or call global usage. Build warnings and command parsing tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/page-pool.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/page-pool.c

Purpose: `ynltool page-pool` subcommand implementation. It dumps netdev page-pool state and statistics, either grouped by device or listed per page pool, with optional JSON output.

Important APIs/types: `struct pp_stat` aggregates live/zombie counts, refs, bytes, and recycling counters. `struct pp_stats_array` stores dynamic per-ifindex aggregates. `find_ifc()`, `count_pool()`, `aggregate_device_stats()`, and `find_pool_stat_in_list()` build summaries. Print functions emit JSON/plain recycling, aggregate stats, and individual pool lists. `do_stats()` parses `group-by` and `zombies`, opens `ynl_netdev_family`, calls `netdev_page_pool_get_dump()` and `netdev_page_pool_stats_get_dump()`, prints, frees, and closes.

Control flow/state: default grouping is by device. `zombies` implies per-pool output and filters to detached pools. Dynamic aggregation starts with 64 slots and doubles with `reallocarray()`.

Dependencies/integration: depends on generated `netdev-user.h`, YNL runtime, global JSON writer from `main.c`, `if_indextoname()`, and command dispatch from `main.h`.

Risks/test signals: `find_ifc()` increments before resize and does not check `reallocarray()` failure, so allocation failure can corrupt state. Aggregation reads `pp->info.ifindex` in stats entries and assumes info is present. Signals include `ynltool page-pool stats`, `group-by page-pool`, `zombies`, and `--json` validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/page-pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/qstats.c -->
# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/qstats.c

Purpose: `ynltool qstats` subcommand implementation. It displays netdev queue statistics, queue-balance analysis, and HW GRO savings in plain or JSON forms.

Important APIs/functions: `print_json_qstats()` and `print_plain_qstats()` render raw device or per-queue stats. `qstats_dump()` opens `ynl_netdev_family`, optionally sets `scope`, calls `netdev_qstats_get_dump()`, and returns the list. `do_show()` parses `scope/group-by`. `compute_stats()`, `print_balance_stats()`, and JSON variant calculate mean, sample standard deviation, coefficient of variation, and normalized spread. `do_balance()` sorts queue stats by ifindex/type/id and analyzes RX/TX packet/byte distribution. `do_hw_gro()` estimates packet savings from HW GRO counters.

Control flow/state: global `scope` defaults to device aggregation. The command table maps `show`, `balance`, `hw-gro`, and `help`; default `qstats` selects `show` because it is first. `do_balance()` builds a sorted pointer array and temporary per-counter arrays per device/type group.

Dependencies/integration: generated `netdev-user.h`, YNL runtime, math library (`sqrt`, linked with `-lm`), JSON globals, and ifindex-to-name resolution.

Risks/test signals: static global scope can persist within one process between invocations if command paths were ever reused internally. `cmp_ifindex_type()` subtracts unsigned fields into int. Balance skips a device/type group when the first queue has no counters, which may miss later active queues. Signals are plain/JSON qstats output, per-queue scope, balance math, and HW GRO output on devices exposing counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/qstats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/Makefile -->
# sources/distributed-fs/ceph-client/tools/objtool/Makefile

Purpose: host-build Makefile for Linux `objtool`. It configures architecture capabilities, optional ORC/KLP/disassembler support, libsubcmd dependency builds, and final host linking.

Important variables/control flow: includes shared make helpers and arch detection. x86 enables ORC and livepatch capability; loongarch enables ORC. If livepatch is supported, it probes `libxxhash` by compiling a small program and enables `BUILD_KLP` plus flags/libs on success. It computes `srctree`, `LIBSUBCMD_OUTPUT`, `OBJTOOL`, `OBJTOOL_IN`, libelf flags/libs, warning flags, include paths, and host overrides. It probes old libelf `elf_getshdr` needs, libopcodes link combinations, and styled disassembler support.

Build targets: `all` builds `$(OBJTOOL)`. `$(OBJTOOL_IN)` depends on `fixdep`, `libsubcmd`, and `FORCE`, runs `sync-check.sh`, and delegates object build through `tools/build/Makefile.include`. The final link uses `HOSTCC`. `$(LIBSUBCMD)` builds and installs libsubcmd headers into its output. `clean` removes object/dependency/cmd files plus generated arch/helper files; `mrproper` also removes the binary.

State/dependencies: persists build artifacts under `OUTPUT` or current directory, exports feature variables to sub-makes, and depends on host pkg-config, libelf, optional xxhash/libopcodes/binutils headers.

Risks/test signals: feature probes are host-environment sensitive. Static libopcodes dependency order can fail on uncommon distros. Clean uses `find $(OUTPUT)` and can behave poorly if `OUTPUT` is empty or unexpected. Signals include successful host build across supported arches and correct `BUILD_ORC`, `BUILD_KLP`, and `BUILD_DISAS` exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/objtool/Makefile -->

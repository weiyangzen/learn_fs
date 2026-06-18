# subset-b-009354 research

Grouped research report for selected strace tests under `sources/test-tools/strace/tests`. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents. The files were read as full source bodies or, for tiny variants, as complete include-wrapper bodies with their referenced base fixture behavior traced.


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_af_spec.c -->
# sources/test-tools/strace/tests/nlattr_ifla_af_spec.c

Purpose: verifies strace decoding of `IFLA_AF_SPEC` nested rtnetlink attributes for link messages across unknown address families and implemented AF_INET, AF_BRIDGE, AF_INET6, and AF_MCTP subtrees.

Important APIs/types/functions: uses `test_nlattr.h` macros, `create_nl_socket(NETLINK_ROUTE)`, `midtail_alloc`, `init_ifinfomsg`/`print_ifinfomsg` from `nlattr_ifla.h`, generated xlat tables for `rtnl_ifla_af_spec_inet_attrs` and `rtnl_ifla_af_spec_inet6_attrs`, and `check_ifla_af_inet6` from `nlattr_ifla_af_inet6.h`. Local `AF_SPEC_FUNCS` builds nested initializers/printers for AF_INET, AF_INET6, AF_MCTP, and bridge tunnel info.

Control flow: opens a route netlink socket, fills reusable pattern buffers, exhaustively probes unknown outer and inner AF attributes, then executes targeted nested checks for AF_INET config arrays, bridge flags/modes/VLAN/tunnel attributes, the shared IPv6 AF helper, and MCTP `IFLA_MCTP_NET`/`PHYS_BINDING` fields.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on Linux `if_link`, bridge, rtnetlink headers, xlat tables, loopback ifindex/proc fd availability, and the strace rtnl link decoder. It integrates with the netlink attribute test macro layer that synthesizes netlink messages and compares decoder output. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <stdio.h>; #include <stddef.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_bridge.h>; ... (16 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_AF msg_af; #define IFLA_AF_STR msg_af_str; #define IFLA_ATTR IFLA_AF_SPEC; #define AF_SPEC_FUNCS(family_)						\.

Risks: high risk of kernel UAPI drift because bridge, IPv6, and MCTP attribute tables evolve. Nested offset calculations (`nla += 1`, adjusted `NLA_HDRLEN` depths) are fragile, and endian-sensitive bridge/VLAN expectations must stay aligned with decoder behavior.

Test signals: successful execution prints decoded AF names, known/unknown xlat fallbacks, cropped hex payloads, clock/value forms, and the final exit marker; failures point to changed AF-specific decoder coverage or stale xlat constants. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_af_spec.c` has 360 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_af_spec.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_ifla_brport-Xabbrev.c

Purpose: compile-time variant wrapper for `nlattr_ifla_brport.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "nlattr_ifla_brport.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_brport.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_brport.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_brport.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_brport-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_ifla_brport-Xraw.c

Purpose: compile-time variant wrapper for `nlattr_ifla_brport.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "nlattr_ifla_brport.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_brport.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_brport.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_brport.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_brport-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_ifla_brport-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_ifla_brport.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_ifla_brport.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_brport.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_brport.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_brport.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_brport-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport.c -->
# sources/test-tools/strace/tests/nlattr_ifla_brport.c

Purpose: validates `IFLA_PROTINFO` decoding when `ifi_family` is `AF_BRIDGE`, specifically bridge-port attributes under the `IFLA_BRPORT_*` namespace.

Important APIs/types/functions: includes `nlattr_ifla.h` with `IFLA_ATTR IFLA_PROTINFO`, `IFLA_AF AF_BRIDGE`, and uses `check_u8_nlattr`, `check_u16_nlattr`, `check_x16_nlattr`, `check_u32_nlattr`, `check_clock_t_nlattr`, plus `TEST_NESTED_NLATTR_OBJECT_EX_`. It exercises `struct ifla_bridge_id` and ifindex formatting via `ifindex_lo()`.

Control flow: builds one synthetic RTM_GETLINK message, first checks undecoded/unknown bridge-port attributes, then loops over grouped u8, u16, x16, u32, clock_t, bridge-id, and ifindex attributes. It tests both raw numeric ifindex and loopback-name-aware output.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on bridge rtnetlink UAPI in `linux/if_link.h`, proc fd availability, and strace's `decode_ifla_protinfo` bridge branch. The `-X*` wrappers compile this same body under alternate xlat modes. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <inttypes.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; ... (9 total). Key defines/macros observed: #define IFLA_ATTR IFLA_PROTINFO; #define IFLA_AF AF_BRIDGE; #define IFLA_AF_STR "AF_BRIDGE".

Risks: bridge-port attribute churn can make known/unknown lists stale. Timer formatting depends on strace's clock_t decoder, and ifindex output depends on loopback discovery and `-y`/xlat mode expectations.

Test signals: broad coverage across scalar widths, bridge IDs, timers, and loopback ifindex output gives good regression signals for bridge-port nlattr decoding. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_brport.c` has 214 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c -->
# sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c

Purpose: stress-tests decoding of nested `IFLA_LINKINFO` attributes, including `IFLA_INFO_KIND`, `DATA`, `XSTATS`, `SLAVE_KIND`, and `SLAVE_DATA` for many link kinds and bridge/tun/can-specific payloads.

Important APIs/types/functions: defines macro helpers `TEST_UNKNOWN_TUNNELS`, `TEST_LINKINFO_`, `TEST_LINKINFO`, and `TEST_NESTED_LINKINFO` to synthesize kind strings and nested attributes. Uses route netlink helpers from `nlattr_ifla.h`, `xmalloc`, link xlat tables, `clock_t_str`, `ifindex_lo`, and Linux bridge/tun/can structs such as `br_boolopt_multi` and CAN stats.

Control flow: begins with unknown `IFLA_INFO_*` cases, iterates unsupported and supported tunnel kind strings, then performs deep bridge data checks for clock, scalar, ethernet protocol, bridge IDs, boolean options, multicast querier state, tun owner/group/type/queue fields, CAN xstats, and bridge slave-data/brport fields.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_bridge.h`, `linux/if_link.h`, rtnetlink xlat tables, and strace's linkinfo decoders selected by kind string. It integrates multiple nested attribute levels and validates fallback behavior for unsupported kinds. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <math.h>; #include <stdio.h>; #include <stddef.h>; #include <unistd.h>; #include <arpa/inet.h>; #include "test_nlattr.h"; ... (17 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_ATTR IFLA_LINKINFO; #define COMMA ,; #define TEST_UNKNOWN_TUNNELS(fd_, nlh0_, kindtype_, objtype_, objtype_str_, \; #define TEST_LINKINFO_(fd_, nlh0_, kindtype_, nla_type_, nla_type_str_,	\; #define TEST_LINKINFO(fd_, nlh0_, kindtype_, nla_type_, tuntype_,	\; #define TEST_NESTED_LINKINFO(fd_, nlh0_, kindtype_,			\; #define QSTATE_NLA(type_, type_str_, field_, crop_str_, str_, ...)	\.

Risks: this fixture is sensitive to kind-string dispatch changes, nesting length/alignment, endian formatting, and UAPI additions. A new supported kind can intentionally break 'unknown tunnel' expectations, which is a useful but noisy signal.

Test signals: strong coverage of full, cropped, and overlong payloads; nested arrays; xlat known/unknown output; ifindex names; clock strings; and bridge/tun/can decoder paths. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c` has 1115 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_port.c -->
# sources/test-tools/strace/tests/nlattr_ifla_port.c

Purpose: checks `IFLA_PORT_SELF` nested port attributes in RTM_GETLINK messages, especially VF and VSI payload printing.

Important APIs/types/functions: uses `nlattr_ifla.h` with `IFLA_ATTR IFLA_PORT_SELF`, `TEST_NESTED_NLATTR_OBJECT`, and `struct ifla_port_vsi`. Fields are printed with `PRINT_FIELD_U` and quoted byte strings.

Control flow: creates a route netlink socket, allocates a message buffer, tests numeric `IFLA_PORT_VF`, then tests two `IFLA_PORT_VSI_TYPE` structures: one printable ASCII VSI type ID and one binary ID/pad case.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_link.h` port attribute definitions and the strace rtnl link port decoder. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; #include "nlattr_ifla.h". Key defines/macros observed: #define IFLA_ATTR IFLA_PORT_SELF.

Risks: struct layout or padding changes can affect expected byte output. Binary string escaping must match strace's current quoting policy.

Test signals: validates both scalar VF output and structured VSI field decoding, including optional pad bytes. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_port.c` has 72 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_port.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xabbrev.c

Purpose: compile-time variant wrapper for `nlattr_ifla_protinfo.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "nlattr_ifla_protinfo.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_protinfo.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_protinfo.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_protinfo.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xraw.c

Purpose: compile-time variant wrapper for `nlattr_ifla_protinfo.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "nlattr_ifla_protinfo.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_protinfo.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_protinfo.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_protinfo.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_ifla_protinfo.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_ifla_protinfo.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_protinfo.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_protinfo.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_protinfo.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo.c -->
# sources/test-tools/strace/tests/nlattr_ifla_protinfo.c

Purpose: validates generic `IFLA_PROTINFO` behavior across address families: unknown families should remain hex payloads, AF_BRIDGE is delegated to `nlattr_ifla_brport`, and AF_INET6 is decoded through the shared IPv6 helper.

Important APIs/types/functions: local `init_ifinfomsg`, `init_ifinfomsg_protinfo`, `print_ifinfomsg`, and `print_ifinfomsg_protinfo`; uses `addrfams` xlat, `check_ifla_af_inet6`, and route netlink helpers.

Control flow: iterates all 256 possible `ifi_family` values except AF_BRIDGE and AF_INET6, expecting undecoded hex payloads for `IFLA_PROTINFO`; then sets AF_INET6 and runs `check_ifla_af_inet6` inside one nested `IFLA_PROTINFO` level.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on rtnetlink, ARP/link headers, xlat address families, loopback ifindex, and the strace link decoder's family-specific protinfo dispatch. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <netinet/in.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; #include <stdio.h>; #include "test_nlattr.h"; ... (11 total).

Risks: newly supported address-family protinfo decoders can change the expected unknown fallback. The skip list must remain sorted/accurate so bridge and IPv6 coverage stays in their specialized fixtures.

Test signals: exhaustive family iteration is a strong negative-coverage signal; IPv6 positive coverage verifies nested AF-specific decoding through a shared helper. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_protinfo.c` has 127 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c -->
# sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c

Purpose: tests `IFLA_PROTO_DOWN_REASON` nested attributes, distinguishing undecoded reason attributes from known mask/value u32 attributes.

Important APIs/types/functions: includes `rtnl_ifla_proto_down_reason_attrs` xlat in macro-only mode, `nlattr_ifla.h` with `IFLA_ATTR IFLA_PROTO_DOWN_REASON`, and `TEST_NESTED_NLATTR_OBJECT_EX_`.

Control flow: sends invalid or unspecified reason attributes and expects quoted bytes, then sends `IFLA_PROTO_DOWN_REASON_MASK` and `VALUE` and expects hexadecimal u32 output.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on route link decoder support for protocol-down reason subattributes and Linux if_link definitions. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; # include "xlat/rtnl_ifla_proto_down_reason_attrs.h"; ... (9 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_ATTR IFLA_PROTO_DOWN_REASON.

Risks: UAPI additions can reclassify unknown attributes; byte-order of the test union must remain compatible with expected escaped bytes.

Test signals: checks both fallback and semantic u32 paths for proto-down reason decoding. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c` has 76 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xabbrev.c

Purpose: compile-time variant wrapper for `nlattr_ifla_vfinfo.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "nlattr_ifla_vfinfo.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_vfinfo.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_vfinfo.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_vfinfo.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xraw.c

Purpose: compile-time variant wrapper for `nlattr_ifla_vfinfo.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "nlattr_ifla_vfinfo.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_vfinfo.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_vfinfo.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_vfinfo.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_ifla_vfinfo.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_ifla_vfinfo.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_vfinfo.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_vfinfo.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_vfinfo.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c -->
# sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c

Purpose: validates nested `IFLA_VFINFO_LIST` decoding for virtual-function info, stats, VLAN lists, MAC/broadcast addresses, link states, trust/guid/rate fields, and ethernet protocol names.

Important APIs/types/functions: defines nested initializers/printers for `IFLA_VF_INFO`, `IFLA_VF_STATS`, and `IFLA_VF_VLAN_LIST`; uses many `struct ifla_vf_*` payloads, `check_u64_nlattr`, `TEST_NESTED_NLATTR_OBJECT_EX_`, `htons`, and xlat-aware MAC printing.

Control flow: probes unknown list and VF attributes, then exercises each structured VF payload (`MAC`, `VLAN`, `TX_RATE`, `SPOOFCHK`, `LINK_STATE`, `RATE`, `RSS_QUERY_EN`, stats, `TRUST`, GUIDs, VLAN info list, broadcast). Nested depth increases from top-level VF list to VF info to stats/VLAN subtrees.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_link.h`, route netlink helpers, ethernet protocol xlat tables, and strace's `IFLA_VFINFO_LIST` decoder. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <stddef.h>; #include <stdio.h>; #include <arpa/inet.h>; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; ... (12 total). Key defines/macros observed: #define IFLA_ATTR IFLA_VFINFO_LIST.

Risks: VF UAPI evolves frequently; known/unknown attribute lists and struct field coverage can become stale. MAC string formatting changes under xlat mode are covered by wrappers but remain a maintenance point.

Test signals: strong positive coverage for every major VF payload family and negative coverage for unknown attrs at each nesting level. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c` has 403 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_xdp-y.c -->
# sources/test-tools/strace/tests/nlattr_ifla_xdp-y.c

Purpose: compile-time variant wrapper for `nlattr_ifla_xdp.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`PRINT_SOCK=1, FD9_PATH="</dev/full>"`) followed by `#include "nlattr_ifla_xdp.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifla_xdp.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifla_xdp.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifla_xdp.c". Key defines/macros observed: #define PRINT_SOCK 1; #define FD9_PATH "</dev/full>".

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_xdp-y.c` has 3 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_xdp-y.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_xdp.c -->
# sources/test-tools/strace/tests/nlattr_ifla_xdp.c

Purpose: checks nested `IFLA_XDP` decoding for XDP program fd, attach state, flags, program IDs, and expected fd fields.

Important APIs/types/functions: includes `rtnl_ifla_xdp_attrs` xlat, `nlattr_ifla.h` with `IFLA_ATTR IFLA_XDP`, and uses `TEST_NESTED_NLATTR_OBJECT(_EX)` with int32/u32/u8 payloads. `FD9_PATH` is optionally appended by the `-y` wrapper.

Control flow: sends `IFLA_XDP_FD`, multiple `IFLA_XDP_ATTACHED` enum values including unknown fallbacks, `IFLA_XDP_FLAGS`, program ID attributes, and two `IFLA_XDP_EXPECTED_FD` cases including fd 9 path-aware output.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on link/XDP UAPI, xlat mode, `/proc/self/fd` for fd path rendering, and strace's link XDP decoder. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; # include "xlat/rtnl_ifla_xdp_attrs.h"; ... (9 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_ATTR IFLA_XDP; # define FD9_PATH "".

Risks: new XDP attach states or flags can alter expected symbolic names. The path-aware variant depends on `/dev/full` and proc fd availability.

Test signals: validates scalar, enum, bitmask, fd, and fd-path rendering for XDP attributes. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_xdp.c` has 98 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_xdp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_ifstats-Xabbrev.c

Purpose: compile-time variant wrapper for `nlattr_ifstats.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "nlattr_ifstats.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifstats.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifstats.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifstats.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifstats-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_ifstats-Xraw.c

Purpose: compile-time variant wrapper for `nlattr_ifstats.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "nlattr_ifstats.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifstats.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifstats.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifstats.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifstats-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_ifstats-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_ifstats.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_ifstats.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_ifstats.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_ifstats.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_ifstats.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifstats-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats.c -->
# sources/test-tools/strace/tests/nlattr_ifstats.c

Purpose: exercises RTM_GETSTATS `struct if_stats_msg` attribute decoding, including link stats64, bridge/bond extended stats, offload stats, and AF_MPLS stats under `IFLA_STATS_AF_SPEC`.

Important APIs/types/functions: local `init_ifstats`, nested-function macro `DEF_NLATTR_FUNCS_NESTED`, helpers `print_stats_64`, `check_stats_64`, `fmt_str`, `print_mcast_stats`, `check_xstats`, `check_stats_offload`, `check_stats_af_generic`, and `check_stats_af_mpls`. Uses `rtnl_link_stats64`, bridge VLAN/mcast/STP xstats, bond 802.3ad counters, `mpls_link_stats`, and multiple xlat tables.

Control flow: checks unknown top-level stats attrs, decodes `IFLA_STATS_LINK_64`, runs bridge and bond xstats for both normal and slave top-level attrs, checks offload CPU-hit stats, generically probes AF-specific unknown families, then decodes MPLS link stats.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_link.h`, bonding, bridge, MPLS headers, address-family/xstats xlat tables, and strace's RTM_GETSTATS decoder. Source includes observed: #include "tests.h"; #include <arpa/inet.h>; #include <inttypes.h>; #include <linux/ip.h>; #include <netinet/in.h>; #include <stdbool.h>; #include <stdint.h>; #include <stdio.h>; ... (26 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define DEF_NLATTR_FUNCS_NESTED(sfx_, attr_var_, attr_str_var_,		\; #define PR_FIELD_(pfx_, field_) \; #define FIELD_STR_(field_) \.

Risks: this is broad and sensitive to struct growth (`rx_nohandler`, `rx_otherhost_dropped`), nested xlat additions, and UAPI additions to stats families. Global l1/l2/l3 attr variables make ordering and nested printer setup important.

Test signals: very high-value regression coverage for nested stats decoders, cropped-vs-full struct lengths, unknown fallback, and xlat/raw/verbose mode differences. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifstats.c` has 789 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_inet_diag_msg.c -->
# sources/test-tools/strace/tests/nlattr_inet_diag_msg.c

Purpose: validates strace decoding of INET_DIAG response attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `inet_diag_msg`, TCP meminfo/vegas/dctcp/bbr, skmem arrays, shutdown bits, congestion strings, u8/u32/u64 attrs, MD5 signatures, ULP TLS/MPTCP/BPF storage, sockopt bitfields, locals/peers sockaddr arrays. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <string.h>; #include <arpa/inet.h>; #include <linux/atalk.h>; #include <linux/mptcp.h>; #include <linux/tls.h>; #include <net/if.h>; ... (13 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_inet_diag_msg.c` has 884 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_inet_diag_msg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_inet_diag_req_compat.c -->
# sources/test-tools/strace/tests/nlattr_inet_diag_req_compat.c

Purpose: validates strace decoding of legacy `inet_diag_req` request attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `TCPDIAG_GETSOCK`, `struct inet_diag_req`, one unknown post-`INET_DIAG_REQ_PROTOCOL` attr fallback. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <string.h>; #include <sys/socket.h>; #include <arpa/inet.h>; #include <net/if.h>; #include <netinet/tcp.h>; #include "test_nlattr.h"; ... (11 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_inet_diag_req_compat.c` has 85 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_inet_diag_req_compat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_inet_diag_req_v2.c -->
# sources/test-tools/strace/tests/nlattr_inet_diag_req_v2.c

Purpose: validates strace decoding of `inet_diag_req_v2` request attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers bytecode ops/host conditions for IPv4/IPv6/dev/mark, protocol attrs including SMC/MPTCP, and unknown request attrs. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <string.h>; #include <sys/socket.h>; #include <arpa/inet.h>; #include <net/if.h>; #include <netinet/tcp.h>; #include "test_nlattr.h"; ... (11 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_inet_diag_req_v2.c` has 456 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_inet_diag_req_v2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_mdba_mdb_entry.c -->
# sources/test-tools/strace/tests/nlattr_mdba_mdb_entry.c

Purpose: validates strace decoding of bridge MDB entry attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `br_port_msg`, nested `MDBA_MDB`/`MDBA_MDB_ENTRY`, `br_mdb_entry`, entry extension attr timer. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <arpa/inet.h>; #include <linux/if_bridge.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_mdba_mdb_entry.c` has 135 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_mdba_mdb_entry.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_mdba_router_port.c -->
# sources/test-tools/strace/tests/nlattr_mdba_router_port.c

Purpose: validates strace decoding of bridge MDB router-port attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `MDBA_ROUTER`, `MDBA_ROUTER_PORT`, router port type and timer attrs with clock tick comments. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <math.h>; #include <stdio.h>; #include <unistd.h>; #include "test_nlattr.h"; #include <linux/if_bridge.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_mdba_router_port.c` has 134 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_mdba_router_port.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ndmsg.c -->
# sources/test-tools/strace/tests/nlattr_ndmsg.c

Purpose: validates strace decoding of neighbour attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `ndmsg`, `NDA_CACHEINFO`, port, lladdr, u32 attrs, `NDA_FDB_EXT_ATTRS`, `NDA_FLAGS_EXT`, NUD/NTF masks. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <netinet/in.h>; #include <arpa/inet.h>; #include "test_nlattr.h"; #include <linux/neighbour.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_ndmsg.c` has 237 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ndmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ndtmsg.c -->
# sources/test-tools/strace/tests/nlattr_ndtmsg.c

Purpose: validates strace decoding of neighbour-table attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `ndtmsg`, `ndt_config`, `NDTA_PARMS` nested attr, `ndt_stats`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/neighbour.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_ndtmsg.c` has 148 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ndtmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_netconfmsg.c -->
# sources/test-tools/strace/tests/nlattr_netconfmsg.c

Purpose: validates strace decoding of netconf attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `netconfmsg` with unknown `NETCONFA_*` fallback. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/netconf.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_netconfmsg.c` has 64 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_netconfmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_netlink_diag_msg.c -->
# sources/test-tools/strace/tests/nlattr_netlink_diag_msg.c

Purpose: validates strace decoding of netlink socket diag attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers groups array, `netlink_diag_ring`, `NETLINK_DIAG_FLAGS`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <string.h>; #include <stdint.h>; #include "test_nlattr.h"; #include <linux/netlink_diag.h>; #include <linux/sock_diag.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_netlink_diag_msg.c` has 105 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_netlink_diag_msg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_nhmsg-Xabbrev.c

Purpose: compile-time variant wrapper for `nlattr_nhmsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "nlattr_nhmsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_nhmsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_nhmsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_nhmsg.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_nhmsg-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_nhmsg-Xraw.c

Purpose: compile-time variant wrapper for `nlattr_nhmsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "nlattr_nhmsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_nhmsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_nhmsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_nhmsg.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_nhmsg-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_nhmsg-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_nhmsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_nhmsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_nhmsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_nhmsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_nhmsg.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_nhmsg-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg.c -->
# sources/test-tools/strace/tests/nlattr_nhmsg.c

Purpose: validates strace decoding of nexthop attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `nhmsg`, NHA scalar attrs, groups, group type, ifindex, gateway by AF, encap type, resilient group/bucket nested attrs. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <arpa/inet.h>; #include <inttypes.h>; #include <linux/ip.h>; #include <linux/rtnetlink.h>; #include <linux/nexthop.h>; #include <netinet/in.h>; #include <stdint.h>; ... (15 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define DEF_NLATTR_NHMSG_FUNCS(sfx_, af_)				\; #define DEF_NLATTR_NHMSG_NESTED_FUNCS(sfx_, attr_)			\.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_nhmsg.c` has 412 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nhmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nlmsgerr.c -->
# sources/test-tools/strace/tests/nlattr_nlmsgerr.c

Purpose: validates strace decoding of netlink error attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `nlmsgerr` with `NLMSG_ERROR`, capped request, `NLMSGERR_ATTR_COOKIE` byte array. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <stdint.h>; #include "test_nlattr.h". Key defines/macros observed: #define NLMSGERR_ATTR_COOKIE 3.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_nlmsgerr.c` has 68 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_nlmsgerr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_packet_diag_msg.c -->
# sources/test-tools/strace/tests/nlattr_packet_diag_msg.c

Purpose: validates strace decoding of packet socket diag attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `packet_diag_msg`, `packet_diag_info`, multicast list, packet ring, BPF filter array. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <string.h>; #include <stdint.h>; #include <net/if.h>; #include "test_nlattr.h"; #include <sys/socket.h>; #include <linux/filter.h>; ... (11 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_packet_diag_msg.c` has 171 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_packet_diag_msg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_rtgenmsg.c -->
# sources/test-tools/strace/tests/nlattr_rtgenmsg.c

Purpose: validates strace decoding of rtgen attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `rtgenmsg` for `RTM_GETNSID` and unknown `NETNSA_*` attr. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "netlink.h"; #include <linux/rtnetlink.h>; #include "test_nlattr.h".

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_rtgenmsg.c` has 63 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_rtgenmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_rtmsg.c -->
# sources/test-tools/strace/tests/nlattr_rtmsg.c

Purpose: validates strace decoding of route message attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `rtmsg`, address attrs by AF, OIF/table, metrics, multipath with nested attrs, cacheinfo, mfc stats, via, encap type. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <netinet/in.h>; #include <arpa/inet.h>; #include "test_nlattr.h"; #include <linux/ip.h>; #include <linux/rtnetlink.h>. Key defines/macros observed: # define mempcpy strace_mempcpy; #define LWTUNNEL_ENCAP_NONE 0; #define DEF_NLATTR_RTMSG_FUNCS(sfx_, af_)				\; #define MAX_ADDR_SZ 35.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_rtmsg.c` has 359 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_rtmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_smc_diag_msg.c -->
# sources/test-tools/strace/tests/nlattr_smc_diag_msg.c

Purpose: validates strace decoding of SMC socket diag attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `smc_diag_msg`, shutdown bits, conninfo cursors, link group info, DMB info, fallback diagnostics. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <sys/socket.h>; #include <stdio.h>; #include <string.h>; #include <stdint.h>; #include <arpa/inet.h>; #include "test_nlattr.h"; #include <linux/rtnetlink.h>; ... (10 total). Key defines/macros observed: # define AF_SMC 43; # define SMC_CLNT 0; # define SMC_ACTIVE 1; #define PRINT_FIELD_SMC_DIAG_CURSOR(where_, field_)		\.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_smc_diag_msg.c` has 256 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_smc_diag_msg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tc_stats.c -->
# sources/test-tools/strace/tests/nlattr_tc_stats.c

Purpose: validates strace decoding of traffic-control stats2 attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `tcmsg`, `gnet_stats_basic`, rate estimates, queue stats, pkt64. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <stddef.h>; #include "test_nlattr.h"; #include <linux/gen_stats.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_tc_stats.c` has 133 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tc_stats.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tca_stab.c -->
# sources/test-tools/strace/tests/nlattr_tca_stab.c

Purpose: validates strace decoding of traffic-control size table attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `tc_sizespec` base and `TCA_STAB_DATA` uint16 array. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/pkt_sched.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_tca_stab.c` has 107 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tca_stab.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xabbrev.c -->
# sources/test-tools/strace/tests/nlattr_tcamsg-Xabbrev.c

Purpose: compile-time variant wrapper for `nlattr_tcamsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "nlattr_tcamsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_tcamsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_tcamsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_tcamsg.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_tcamsg-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xraw.c -->
# sources/test-tools/strace/tests/nlattr_tcamsg-Xraw.c

Purpose: compile-time variant wrapper for `nlattr_tcamsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "nlattr_tcamsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_tcamsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_tcamsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_tcamsg.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_tcamsg-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_tcamsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_tcamsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_tcamsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_tcamsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_tcamsg.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg.c -->
# sources/test-tools/strace/tests/nlattr_tcamsg.c

Purpose: validates strace decoding of traffic-control action attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `tcamsg`, root attrs, action table nesting, kind/index/flags/hw stats/count/time delta/warn msg. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/pkt_cls.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_tcamsg.c` has 318 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcmsg.c -->
# sources/test-tools/strace/tests/nlattr_tcmsg.c

Purpose: validates strace decoding of traffic-control top-level attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `tc_stats` and `tc_estimator` under `TCA_STATS`/`TCA_RATE` plus unknown `TCA_*`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <stddef.h>; #include "test_nlattr.h"; #include <linux/pkt_sched.h>; #include <linux/rtnetlink.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_tcmsg.c` has 114 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcmsg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_unix_diag_msg.c -->
# sources/test-tools/strace/tests/nlattr_unix_diag_msg.c

Purpose: validates strace decoding of Unix socket diag attrs using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `unix_diag_msg`, VFS dev/ino, rq length, icon inode array. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <string.h>; #include <stdint.h>; #include <sys/sysmacros.h>; #include <netinet/tcp.h>; #include "test_nlattr.h"; #include <linux/sock_diag.h>; ... (9 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nlattr_unix_diag_msg.c` has 102 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_unix_diag_msg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls-d.c -->
# sources/test-tools/strace/tests/nsyscalls-d.c

Purpose: compile-time variant wrapper for `nsyscalls.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`DEBUG_PRINT=1`) followed by `#include "nsyscalls.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nsyscalls.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nsyscalls.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nsyscalls.c". Key defines/macros observed: #define DEBUG_PRINT 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nsyscalls-d.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls-d.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls.c -->
# sources/test-tools/strace/tests/nsyscalls.c

Purpose: validates strace decoding of out-of-range syscall decoding using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `test_syscall`, `invoke_syscall`, `syscallent` size, socket/ipc subcall probes, optional debug logging. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "nsyscalls.h". Key defines/macros observed: # define DEBUG_PRINT 0.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nsyscalls.c` has 89 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls.h -->
# sources/test-tools/strace/tests/nsyscalls.h

Purpose: validates strace decoding of helper header for nsyscalls using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `syscallent` table inclusion, `out_of_range_syscall_args`, `invoke_syscall` wrapper with `SYSCALL_BIT`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "sysent.h"; #include "scno.h"; #include <errno.h>; #include <stdio.h>; #include <stdlib.h>; #include <unistd.h>; #include "sysent_shorthand_defs.h"; ... (10 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/nsyscalls.h` has 46 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nsyscalls.h -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-P.c -->
# sources/test-tools/strace/tests/old_mmap-P.c

Purpose: compile-time variant wrapper for `old_mmap.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`TEST_FD=9, PATH_TRACING`) followed by `#include "old_mmap.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `old_mmap.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `old_mmap.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "old_mmap.c". Key defines/macros observed: #define TEST_FD 9; #define PATH_TRACING.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/old_mmap-P.c` has 3 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-P.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-Xabbrev.c -->
# sources/test-tools/strace/tests/old_mmap-Xabbrev.c

Purpose: compile-time variant wrapper for `old_mmap.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`no extra macro definitions`) followed by `#include "old_mmap.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `old_mmap.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `old_mmap.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "old_mmap.c".

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/old_mmap-Xabbrev.c` has 1 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-Xraw.c -->
# sources/test-tools/strace/tests/old_mmap-Xraw.c

Purpose: compile-time variant wrapper for `old_mmap.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "old_mmap.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `old_mmap.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `old_mmap.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "old_mmap.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/old_mmap-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-Xverbose.c -->
# sources/test-tools/strace/tests/old_mmap-Xverbose.c

Purpose: compile-time variant wrapper for `old_mmap.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "old_mmap.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `old_mmap.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `old_mmap.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "old_mmap.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/old_mmap-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-v-none.c -->
# sources/test-tools/strace/tests/old_mmap-v-none.c

Purpose: compile-time variant wrapper for `old_mmap.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`no extra macro definitions`) followed by `#include "old_mmap.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `old_mmap.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `old_mmap.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "old_mmap.c".

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/old_mmap-v-none.c` has 1 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap-v-none.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap.c -->
# sources/test-tools/strace/tests/old_mmap.c

Purpose: validates strace decoding of old mmap syscall decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers architecture-gated `__NR_mmap`, pointer-to-six-arg array ABI, xlat raw/verbose/abbrev modes, optional path tracing. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include <errno.h>; # include <stdio.h>; # include <string.h>; # include <sys/mman.h>; # include <unistd.h>; # include "xmalloc.h".

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/old_mmap.c` has 125 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/old_mmap.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldfstat.c -->
# sources/test-tools/strace/tests/oldfstat.c

Purpose: validates strace decoding of oldfstat decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers configures `fstatx.c` for `__NR_oldfstat` and old kernel stat layout. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include "fstatx.c". Key defines/macros observed: # define OLD_STAT 1; # define TEST_SYSCALL_NR __NR_oldfstat; # define TEST_SYSCALL_STR "oldfstat"; # define STRUCT_STAT struct __old_kernel_stat; # define STRUCT_STAT_STR "struct __old_kernel_stat"; # define STRUCT_STAT_IS_STAT64 0; # define SAMPLE_SIZE ((libc_off_t) (kernel_ulong_t) 23147718418U).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/oldfstat.c` has 30 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldfstat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldlstat.c -->
# sources/test-tools/strace/tests/oldlstat.c

Purpose: validates strace decoding of oldlstat decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers configures `lstatx.c` for `__NR_oldlstat` and old kernel stat layout. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include "lstatx.c". Key defines/macros observed: # define OLD_STAT 1; # define TEST_SYSCALL_NR __NR_oldlstat; # define TEST_SYSCALL_STR "oldlstat"; # define STRUCT_STAT struct __old_kernel_stat; # define STRUCT_STAT_STR "struct __old_kernel_stat"; # define STRUCT_STAT_IS_STAT64 0; # define SAMPLE_SIZE ((libc_off_t) (kernel_ulong_t) 23147718418U).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/oldlstat.c` has 30 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldlstat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect-P.c -->
# sources/test-tools/strace/tests/oldselect-P.c

Purpose: compile-time variant wrapper for `oldselect.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`PATH_TRACING_FD=9`) followed by `#include "oldselect.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `oldselect.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `oldselect.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "oldselect.c". Key defines/macros observed: #define PATH_TRACING_FD 9.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/oldselect-P.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect-P.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect-efault-P.c -->
# sources/test-tools/strace/tests/oldselect-efault-P.c

Purpose: compile-time variant wrapper for `oldselect-efault.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`PATH_TRACING_FD=9`) followed by `#include "oldselect-efault.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `oldselect-efault.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `oldselect-efault.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "oldselect-efault.c". Key defines/macros observed: #define PATH_TRACING_FD 9.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/oldselect-efault-P.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect-efault-P.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect-efault.c -->
# sources/test-tools/strace/tests/oldselect-efault.c

Purpose: validates strace decoding of old select EFAULT decoding using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers old `select` pointer-argument ABI, NULL/pointer cases with dummy args and optional path tracing suppression. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include <stdint.h>; # include <stdio.h>; # include <string.h>; # include <unistd.h>; # include <sys/select.h>.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/oldselect-efault.c` has 59 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect-efault.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect.c -->
# sources/test-tools/strace/tests/oldselect.c

Purpose: validates strace decoding of old select decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers includes `xselect.c`, packs five uint32 args, calls legacy `__NR_select` when distinct from `_newselect`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include "xselect.c". Key defines/macros observed: # define TEST_SYSCALL_NR __NR_select; # define TEST_SYSCALL_STR "select"; # define xselect xselect.

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/oldselect.c` has 48 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldselect.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/oldstat.c -->
# sources/test-tools/strace/tests/oldstat.c

Purpose: validates strace decoding of oldstat decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers configures `lstatx.c` for `__NR_oldstat` and `struct __old_kernel_stat`. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include "lstatx.c". Key defines/macros observed: # define OLD_STAT 1; # define TEST_SYSCALL_NR __NR_oldstat; # define TEST_SYSCALL_STR "oldstat"; # define STRUCT_STAT struct __old_kernel_stat; # define STRUCT_STAT_STR "struct __old_kernel_stat"; # define STRUCT_STAT_IS_STAT64 0; # define SAMPLE_SIZE ((libc_off_t) (kernel_ulong_t) 131478418U).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/oldstat.c` has 30 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/oldstat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/open.c -->
# sources/test-tools/strace/tests/open.c

Purpose: validates strace decoding of open syscall decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `__NR_open`, O_* flags/modes, temporary subdir, SELinux context helpers. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include <asm/fcntl.h>; # include <stdio.h>; # include <unistd.h>; # include "secontext.h".

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/open.c` has 68 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/open.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree-P.c -->
# sources/test-tools/strace/tests/open_tree-P.c

Purpose: compile-time variant wrapper for `open_tree.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`PATH_TRACING`) followed by `#include "open_tree.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `open_tree.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `open_tree.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "open_tree.c". Key defines/macros observed: #define PATH_TRACING.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/open_tree-P.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree-P.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree.c -->
# sources/test-tools/strace/tests/open_tree.c

Purpose: validates strace decoding of open_tree syscall decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers raw syscall wrapper with filled high bits, path/efault/empty strings, OPEN_TREE/AT flags, fd path rendering. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; #include <fcntl.h>; #include <limits.h>; #include <stdio.h>; #include <stdint.h>; #include <unistd.h>; #include "kernel_fcntl.h".

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/open_tree.c` has 104 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree_attr-P.c -->
# sources/test-tools/strace/tests/open_tree_attr-P.c

Purpose: compile-time variant wrapper for `open_tree_attr.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`PATH_TRACING`) followed by `#include "open_tree_attr.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `open_tree_attr.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `open_tree_attr.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "open_tree_attr.c". Key defines/macros observed: #define PATH_TRACING.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/open_tree_attr-P.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree_attr-P.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree_attr.c -->
# sources/test-tools/strace/tests/open_tree_attr.c

Purpose: validates strace decoding of open_tree_attr syscall decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers mount_attr pointer/size decoding, flag masks, extra bytes/unknown tail handling, userns fd path rendering. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; #include <limits.h>; #include <stdio.h>; #include <stdint.h>; #include <string.h>; #include <unistd.h>; #include "kernel_fcntl.h"; ... (10 total).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/open_tree_attr.c` has 178 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/open_tree_attr.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat.c -->
# sources/test-tools/strace/tests/openat.c

Purpose: validates strace decoding of openat syscall decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers mode/flag matrix, AT_FDCWD, real dirfd, O_TMPFILE handling, SELinux context helpers. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; # include <asm/fcntl.h>; # include <stdio.h>; # include <unistd.h>; # include "secontext.h".

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/openat.c` has 174 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-Xabbrev.c -->
# sources/test-tools/strace/tests/openat2-Xabbrev.c

Purpose: compile-time variant wrapper for `openat2.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "openat2.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-Xraw.c -->
# sources/test-tools/strace/tests/openat2-Xraw.c

Purpose: compile-time variant wrapper for `openat2.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "openat2.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-Xverbose.c -->
# sources/test-tools/strace/tests/openat2-Xverbose.c

Purpose: compile-time variant wrapper for `openat2.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "openat2.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y-Xabbrev.c -->
# sources/test-tools/strace/tests/openat2-v-y-Xabbrev.c

Purpose: compile-time variant wrapper for `openat2-v-y.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_ABBREV=1`) followed by `#include "openat2-v-y.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2-v-y.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2-v-y.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2-v-y.c". Key defines/macros observed: #define XLAT_ABBREV 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-v-y-Xabbrev.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y-Xabbrev.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y-Xraw.c -->
# sources/test-tools/strace/tests/openat2-v-y-Xraw.c

Purpose: compile-time variant wrapper for `openat2-v-y.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_RAW=1`) followed by `#include "openat2-v-y.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2-v-y.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2-v-y.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2-v-y.c". Key defines/macros observed: #define XLAT_RAW 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-v-y-Xraw.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y-Xraw.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y-Xverbose.c -->
# sources/test-tools/strace/tests/openat2-v-y-Xverbose.c

Purpose: compile-time variant wrapper for `openat2-v-y.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "openat2-v-y.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2-v-y.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2-v-y.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2-v-y.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-v-y-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y-Xverbose.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y.c -->
# sources/test-tools/strace/tests/openat2-v-y.c

Purpose: compile-time variant wrapper for `openat2-v.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`FD0_PATH="</dev/full>", SKIP_IF_PROC_IS_UNAVAILABLE`) followed by `#include "openat2-v.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2-v.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2-v.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2-v.c". Key defines/macros observed: #define FD0_PATH "</dev/full>"; #define SKIP_IF_PROC_IS_UNAVAILABLE skip_if_unavailable("/proc/self/fd/").

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-v-y.c` has 4 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v-y.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v.c -->
# sources/test-tools/strace/tests/openat2-v.c

Purpose: compile-time variant wrapper for `openat2.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`VERBOSE=1`) followed by `#include "openat2.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2.c". Key defines/macros observed: #define VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-v.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-v.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-y.c -->
# sources/test-tools/strace/tests/openat2-y.c

Purpose: compile-time variant wrapper for `openat2.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`FD0_PATH="</dev/full>", SKIP_IF_PROC_IS_UNAVAILABLE`) followed by `#include "openat2.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `openat2.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `openat2.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "openat2.c". Key defines/macros observed: #define FD0_PATH "</dev/full>"; #define SKIP_IF_PROC_IS_UNAVAILABLE skip_if_unavailable("/proc/self/fd/").

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/openat2-y.c` has 4 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2-y.c -->


<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/openat2.c -->
# sources/test-tools/strace/tests/openat2.c

Purpose: validates strace decoding of openat2 syscall decoder using synthetic syscall or netlink inputs with deterministic expected output.

Important APIs/types/functions: covers `struct open_how`, flags/mode/resolve combinations, size mismatch/extra bytes, optional verbose and fd-path modes. The fixture uses strace test helpers such as `tests.h`, `test_nlattr.h`, `scno.h`, `sprintrc`, allocation helpers, xlat macros, and Linux UAPI structs/constants relevant to this decoder surface.

Control flow: initializes a representative message or syscall argument block, fills deterministic byte patterns, executes positive semantic decode cases and unknown/fallback cases, prints the exact expected strace output, and exits with the standard success marker.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on architecture/kernel feature guards, relevant Linux UAPI headers, proc fd availability for fd/path-aware cases, and the strace decoder selected by syscall number, netlink family, message type, and nested attribute type. Source includes observed: #include "tests.h"; #include "scno.h"; #include <errno.h>; #include <stdint.h>; #include <inttypes.h>; #include <stdio.h>; #include <string.h>; #include <unistd.h>; ... (9 total). Key defines/macros observed: # define VERBOSE 0; # define FD0_PATH ""; # define YFLAG; # define SKIP_IF_PROC_IS_UNAVAILABLE; # define AT_FDCWD_FMT "<%s>"; # define AT_FDCWD_ARG(arg) arg,; # define AT_FDCWD_FMT; # define AT_FDCWD_ARG(arg).

Risks: UAPI growth can turn unknown cases into known symbolic output; struct-size changes can affect cropped/full payload behavior; endian and xlat mode differences can change expected text. Feature-gated legacy syscalls may skip on unsupported architectures.

Test signals: useful signals include successful compilation under the target guard, expected known/unknown xlat names, stable escaped byte output for truncated payloads, correct ifindex/fd/path annotation, and final `+++ exited with 0 +++`. Source-read signal: `sources/test-tools/strace/tests/openat2.c` has 148 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/openat2.c -->

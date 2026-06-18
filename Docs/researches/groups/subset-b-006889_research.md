# Research: subset-b-006889

Grouped research for tc-testing JSON manifests under `sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/matchall.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/matchall.json

Purpose: Defines 22 tc-testing cases for the `matchall` classifier on ingress (`parent ffff:`) and egress (`parent 1:`). The suite validates successful add/get/delete operations, protocol selection (`ip`, `ipv6`, `all`), gact actions (`pass`, `drop`, `continue`, `reclassify`), classid handling, `skip_hw`/`skip_sw` flag validation, chain deletion, and the `filter get` path.

Important APIs/types/functions: This is data consumed by the tc-testing runner. Each object uses the runner schema fields `id`, `name`, `category`, `plugins`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`. The executable surface is `$TC filter add|get|show|del`, `$TC qdisc add|del`, and `$TC actions add|flush|del` for police action objects.

Control flow: Most cases create ingress or egress qdisc state in `setup`, run one `cmdUnderTest`, verify by `tc filter get/show`, match output with regex/count, then remove qdiscs/actions in `teardown`. Delete tests preinstall multiple filters and assert absence or surviving chain/filter entries. Expected exits are mixed: 16 success cases, one invalid-classid parser failure, three flag/action incompatibility failures, and two priority-overflow failures.

State and persistence: State is kernel qdisc/filter/action state on the namespace-local dummy device from `nsPlugin`. Teardown normally deletes ingress or root qdisc state, but the police-action tests also flush/delete action index `199`, making action reference cleanup part of correctness.

Dependencies and integration points: Requires tc matchall, gact, police, ingress/root qdiscs, and the tc-testing namespace plugin. It integrates with shared action infrastructure through `action police index 199` and with chain-aware classifier deletion.

Risks: Regexes are sensitive to iproute2 output spelling (`not_in_hw`, `gact action pass`, `ref 1 bind 1`). Hardware-offload flag semantics can differ by kernel/configuration. Delete-all and multi-filter cases depend on setup ordering and unique handles/priorities.

Test signals: Positive tests expect one matching filter line. Invalid priority/classid/flag cases expect nonzero exit and zero matches. Chain deletion expects chain 1 to remain while chain 2 is deleted. The final get test confirms a newly added handle `0x1234` is retrievable by `tc filter get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/matchall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/route.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/route.json

Purpose: Defines 9 route-filter tests covering `from`, `to`, `fromif`, classid selection, gact actions, multi-action chains, listing, deletion, and class-reference protection after filter replacement.

Important APIs/types/functions: Uses tc-testing JSON fields around `$TC filter add|show|ls|del`, `$TC qdisc add|del`, and `$TC class add|delete|show`. The cases exercise the route classifier grammar under `parent ffff:` and DRR classes for reference-lifetime checks.

Control flow: Setup usually creates ingress/qdisc context, the command under test installs or deletes a route filter, and verification lists filters under `parent ffff:`. The final case installs a DRR class and a route filter, replaces the filter path, then verifies that deleting the referenced class fails with exit `2`.

State and persistence: The state is kernel route-filter state bound to `$DEV1` and class references under DRR handle `10:`. Teardown removes root qdiscs or ingress state so references do not leak into later tests.

Dependencies and integration points: Requires `nsPlugin`, route classifier support, gact/skbedit actions, ingress qdisc, and DRR classful qdisc support. It integrates classifier references with class deletion rules.

Risks: The route classifier is legacy and output formatting may vary. The test named "form tag" appears to mean "from tag" in the command; consumers should rely on `cmdUnderTest`. Multi-action matching is regex-order-sensitive because it expects skbedit mark then gact drop.

Test signals: Eight tests expect successful command exit and one regex match. The reference-protection test expects class deletion to fail and class `drr 10:1` to remain visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/route.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/u32.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/u32.json

Purpose: Defines 15 tests for the `u32` classifier, including source-IP matching, invalid `indev`, custom hash-table creation, invalid handles/hash IDs, linked hash tables, `sample` bucket calculation, class-reference protection, hash-table deletion protection, recursive deletion of a small hashtable tree, and an IDR leak stress loop.

Important APIs/types/functions: Exercises `$TC filter add|replace|delete|show`, `$TC qdisc add|del`, `$TC class add|delete|show`, and tc batch mode (`$TC -b -`). Schema fields are standard tc-testing case fields plus regex/count checks. The tc grammar under test includes `u32 match`, `flowid`, `indev`, `divisor`, `handle`, `ht`, `link`, `hashkey`, `sample`, and `classid`.

Control flow: Setup creates ingress or DRR root state and, for reference tests, preloads classes/tables/filters. The command under test mutates u32 state. Verification checks expanded kernel handles (`fh 800:`, `ht divisor`, bucket IDs) or ensures invalid replace operations did not alter existing state. The stress case loops 2048 delete/add operations through batch input.

State and persistence: Kernel classifier hashtable state is central. Several cases intentionally keep referenced classes or hashtables alive after failed deletion attempts. Teardown deletes the parent qdisc, which should recursively remove classifier state.

Dependencies and integration points: Requires `nsPlugin`, u32 classifier support, DRR, gact actions, and tc batch support. It integrates u32 ID/handle allocation with kernel IDR lifetime and class reference tracking.

Risks: Regexes intentionally accept multiple output forms for u32 handles, but are still tied to iproute2 formatting. The IDR stress test can expose leaks only if the environment allows 2048 rapid filter operations. Invalid-handle exit code expectations depend on parser/kernel validation ordering.

Test signals: Seven tests expect success and eight expect exit `2`. Sample tests assert seven and five bucket matches respectively. Tree deletion expects no `protocol ip pref 2 u32` output. IDR stress expects remaining pref `3` u32 output count of three, indicating stable table/header/filter state after repeated allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/u32.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/actions.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/actions.json

Purpose: Defines 19 infrastructure tests proving that pre-created tc action objects can be referenced by a matchall filter. It covers pedit, mpls, bpf, connmark, csum, ct, ctinfo, gact, gate, ife, mirred, nat, police, sample, skbedit, skbmod, tunnel_key, vlan, plus one large-command echo test.

Important APIs/types/functions: Uses `$TC actions add|flush`, `$TC filter add|get`, and matchall classifier syntax `action <kind> index <n>`. Categories encode the action kind. The runner fields drive setup, command, expected exit, regex, and teardown.

Control flow: Each action-reference case creates an ingress qdisc and an indexed action object, adds a matchall filter referencing that action by index, verifies the filter handle exists, and deletes the qdisc/action state. The large-command test checks the runner/iproute2 path can echo or process a long filter command without truncation.

State and persistence: Persistent kernel state is action objects keyed by action kind and index plus the matchall filter binding. Since all 19 commands expect success, cleanup correctness matters to avoid index collision in following cases.

Dependencies and integration points: Requires `nsPlugin`, matchall, and all listed action modules. The bpf case depends on the test environment's ability to construct a valid bpf action object. The file is a broad integration point between action creation and filter binding rather than per-action behavior validation.

Risks: Missing optional action modules can cause environment failures unrelated to matchall. Regexes only assert the filter exists, not deep action-specific behavior. Shared action indices can collide if teardown fails or if tests run without isolated namespaces.

Test signals: All tests expect exit `0`. The primary signal is `tc filter get` output matching `parent ffff: protocol ip pref 1 matchall handle 0x1`; absence indicates either action reference failure or filter install failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/actions.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/filter.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/filter.json

Purpose: Defines 3 negative infrastructure tests around filter chains and shared-block restrictions. It checks a prio-0 chain deletion path tied to a soft-lockup regression and validates that empty `fw` and `flow` filters on shared blocks are rejected at configuration time.

Important APIs/types/functions: Uses `$TC filter add|delete|show`, `$TC qdisc add|del`, and shared block syntax. The tc-testing fields are the standard command/expected-exit/regex contract.

Control flow: Each case sets up the minimal qdisc or block context, runs a filter command expected to fail with exit `2`, and verifies either residual chain state or absence of invalid filter installation. The soft-lockup case verifies `chain parent 1: chain 0` remains visible after deleting a prio-0 filter.

State and persistence: State is temporary filter-chain metadata and shared-block classifier configuration. No long-lived state should remain after qdisc teardown.

Dependencies and integration points: Requires `nsPlugin`, chain-aware filter operations, `fw` and `flow` classifiers, and shared block support. It integrates parser/config validation with kernel chain cleanup paths.

Risks: Negative tests can be sensitive to whether validation happens in iproute2 or kernel code. The soft-lockup regression cannot be fully proven by output matching; a hang or kernel warning is the implicit failure mode.

Test signals: All three commands expect exit `2`. The soft-lockup case still expects one chain regex match, while shared-block cases expect zero matches for `fw` or `flow`, proving invalid empty filters were not installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/filter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/qdiscs.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/qdiscs.json

Purpose: Defines 41 qdisc infrastructure/regression tests spanning class delete notifications, backlog/qlen accounting, reentrant enqueue/dequeue behavior, invalid child attachment, parent/leaf interactions, and known underflow/use-after-free/divide-by-zero cases across DRR, ETS, HFSC, HTB, TBF, QFQ, CAKE, RED, SFB, CBS, dualpi2, fq/fq_codel/fq_pie, PIE, CODEL, HHF, SKBPRIO, ingress, clsact, blackhole, and netem.

Important APIs/types/functions: Uses `$TC qdisc|class|filter`, `$IP link|addr`, `ping`, optional scapy injection, and `matchJSON` checks for structured `tc -s -j` output. Plugins are `nsPlugin` and `scapyPlugin`. Schema adds `scapy` and `matchJSON` beyond normal regex fields.

Control flow: Tests build multi-level qdisc/class trees in `setup`, often enqueue packets with `ping` or scapy, then execute mutations such as class delete/re-add, qdisc add/delete, or traffic-triggered dequeue. Verification uses text regexes, structured JSON counters, or expected failure exits. Twenty-eight cases expect success, eight expect exit `1`, and five expect exit `2`.

State and persistence: Heavy kernel scheduling state is created under dummy/veth devices: class trees, child qdiscs, backlog counters, delayed packets, `gso_skb`, and active-list membership. Teardown removes root/ingress qdiscs and IP addresses; correctness includes avoiding leaked active classes and stale child pointers.

Dependencies and integration points: Requires many qdisc modules plus namespace and scapy support. It is an integration hub for parent/child contracts between classful qdiscs and leaf qdiscs, packet enqueue/dequeue accounting, and JSON stats reporting.

Risks: This file is environment-sensitive: missing modules, timing differences in `ping`/delay, and output changes in `tc -j` can affect results. The regression cases target subtle kernel bugs where the true failure may be a crash, warning, underflow, or hang rather than a simple mismatched line.

Test signals: `matchJSON` asserts exact packet/byte/backlog counters for reentrant enqueue/dequeue and underflow cases. Scapy cases inject Ethernet/IP/TCP or ICMP packets. Negative attachment tests assert failure when adding leaf qdiscs under incompatible parents such as HHF, DRR, ingress, clsact, or nonexistent HFSC classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/qdiscs.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake.json

Purpose: Defines 21 CAKE qdisc tests for creation, option parsing, deletion, replacement, change, and class display. It covers bandwidth, autorate ingress, RTT, diffserv modes, flow isolation, NAT, wash, split-GSO, ACK filtering, memlimit, PTM/ATM, fwmark, overhead, MPU, conservative mode, and ingress mode.

Important APIs/types/functions: Uses `$TC qdisc add|del|replace|change|show` and `$TC class show` on `$DUMMY`, with `nsPlugin`. Regexes validate normalized `tc qdisc show` output for CAKE defaults and option-specific rendering.

Control flow: Cases install root CAKE with one option set, verify `qdisc cake 1: root` output, and delete it. Replace/change cases first install CAKE then mutate `mpu`. The class case verifies CAKE class reporting behavior.

State and persistence: State is a root CAKE qdisc on the dummy interface. Teardown deletes the root qdisc after each case, keeping option-state isolated.

Dependencies and integration points: Requires sch_cake and iproute2 CAKE option support. It integrates parser options with kernel netlink attributes and output formatting.

Risks: CAKE output is verbose and regexes depend on normalized terms such as `diffserv3`, `triple-isolate`, `nonat`, `nowash`, `split-gso`, `rtt 100ms`, and overhead mode. Units such as `1Kbit`, `200us`, and memory limits may be formatted differently across iproute2 versions.

Test signals: All 21 tests expect exit `0`. Matching qdisc output is the main signal; delete expects absence, replace/change expect updated `mpu`, and class display expects the class command to run without exposing unsupported classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake_mq.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake_mq.json

Purpose: Defines 25 tests for multi-queue CAKE (`cake_mq`) on a four-queue device. It mirrors most CAKE option coverage and adds multi-queue-specific mutation and rejection cases.

Important APIs/types/functions: Uses `$TC qdisc add|del|replace|change|show`, `$TC class show`, and queue-aware setup via `nsPlugin`. The qdisc grammar under test includes `cake_mq`, per-queue sub-qdisc handling, bandwidth changes, and rejection of unsupported settings.

Control flow: The first 21 cases create, verify, delete, replace, change, or show CAKE_MQ under a four-queue device. Four negative cases expect exit `2`: `autorate-ingress` is rejected, direct change/replace of a sub-qdisc is rejected, and install on a single-queue device is rejected.

State and persistence: State includes the root `cake_mq` qdisc plus generated per-queue child CAKE instances. Teardown removes the root qdisc, which should remove all children.

Dependencies and integration points: Requires multi-queue test-device support, sch_cake, sch_mq/cake_mq integration, and iproute2 support for displaying generated children. It integrates root qdisc validation with real device queue count.

Risks: Results depend on the test environment actually exposing four queues for positive cases and one queue for the single-queue negative case. Sub-qdisc handle layout/output can be version-sensitive. CAKE_MQ support may not be present in all kernels.

Test signals: Twenty-one cases expect success, four expect exit `2`. Regexes assert `cake_mq` root state and option propagation. Negative tests expect no accepted qdisc mutation for autorate ingress, sub-qdisc direct edits, or single-queue installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cake_mq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cbs.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cbs.json

Purpose: Defines 10 CBS qdisc tests for default creation, individual credit/slope parameters, combined settings, replace, change, delete, and class display.

Important APIs/types/functions: Exercises `$TC qdisc add|replace|change|del|show` and `$TC class show`. The qdisc options under test are `hicredit`, `locredit`, `sendslope`, and `idleslope`.

Control flow: Each positive case installs root CBS on `$DUMMY`, verifies printed parameters, and tears down. Replace/change cases first create CBS then mutate one parameter. Delete verifies the qdisc is gone; class display checks class command handling.

State and persistence: State is one root CBS qdisc. The scheduler's shaping parameters persist until deletion and are confirmed by output.

Dependencies and integration points: Requires sch_cbs and namespace dummy device setup. Integrates tc parser units/integers with kernel CBS netlink attributes.

Risks: CBS may require kernel config support and can have hardware-offload-related behavior in other contexts, though this file uses software root qdisc tests. Unit/parameter formatting may vary.

Test signals: All 10 tests expect exit `0`. Regexes confirm option values for creation and mutation; delete expects no CBS qdisc; class show expects no unexpected class output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cbs.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/choke.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/choke.json

Purpose: Defines 8 CHOKE qdisc tests covering default creation, `min`, `max`, `ecn`, `burst`, delete, replace, and change operations.

Important APIs/types/functions: Uses `$TC qdisc add|del|replace|change|show` on `$DUMMY`, with regex checks for `qdisc choke` output and configured queue thresholds.

Control flow: Add cases install CHOKE with one option and verify. Replace/change cases install first and then mutate `min` or `limit`. Delete removes by handle and verifies absence.

State and persistence: State is a root CHOKE queue discipline with probabilistic drop/ECN settings. Teardown deletes the root qdisc.

Dependencies and integration points: Requires sch_choke and iproute2 CHOKE grammar. Integrates parser options into kernel scheduler parameters.

Risks: CHOKE is less commonly enabled than FIFO/FQ qdiscs. Output wording for packet/byte thresholds and ECN can change across iproute2 versions.

Test signals: All 8 tests expect exit `0`; regex count one for configured qdisc presence and zero after deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/choke.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/codel.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/codel.json

Purpose: Defines 10 CODEL qdisc tests for default creation, limit, target, interval, ECN, CE threshold, delete, replace, change, and queue-limit trimming under packet injection.

Important APIs/types/functions: Uses `$TC qdisc add|del|replace|change|show`, `nsPlugin`, and `scapyPlugin` for the trimming test. Options include `limit`, `target`, `interval`, `ecn`, and `ce_threshold`.

Control flow: Normal cases install root CODEL and verify formatted output. Replace/change mutate `limit`. The trimming test sends ten scapy TCP packets, then changes limit to `1` and verifies the qdisc shows `limit 1p`.

State and persistence: State is CODEL qdisc configuration plus queued packet state during the scapy test. Teardown removes root qdisc and queued traffic.

Dependencies and integration points: Requires sch_codel, scapy support for packet injection, and namespace devices. Integrates qdisc parameter parsing with runtime queue trimming behavior.

Risks: Packet injection and queue occupancy can be timing-sensitive. CE threshold formatting (`1.02s`-style conversions in related qdiscs) can vary by iproute2. The trimming test assumes injected packets reach the qdisc before the limit change.

Test signals: All 10 tests expect exit `0`. Regexes validate qdisc option rendering and the trimming case specifically confirms post-change limit output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/codel.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/drr.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/drr.json

Purpose: Defines 4 DRR tests for root qdisc creation, deletion, class display, and rejection of a class with classid `TC_H_ROOT`.

Important APIs/types/functions: Uses `$TC qdisc add|del|show` and `$TC class add|show`. The critical grammar is classful `drr` and classid validation.

Control flow: The positive creation and class-show cases install root DRR and verify qdisc/class output. Delete removes the qdisc and expects no remaining output. The negative classid case attempts to add a class using the root classid and expects exit `2`.

State and persistence: State is a root DRR scheduler and optional class nodes. Teardown deletes the qdisc.

Dependencies and integration points: Requires sch_drr and namespace setup. Integrates classid validation with classful scheduler lifecycle.

Risks: DRR class output can be minimal and version-sensitive. The root-classid rejection depends on kernel-side validation staying strict.

Test signals: Three cases expect success and one expects exit `2`. Class display should expose a DRR class for valid roots and reject `TC_H_ROOT` class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/drr.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/dualpi2.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/dualpi2.json

Purpose: Defines 12 DualPI2 qdisc creation tests for default settings and option parsing: `memlimit`, `typical_rtt`, `max_rtt`, `any_ect`, `overflow`, `drop_enqueue`, `no_split_gso`, packet `step_thresh`, packet `min_qlen_step`, packet `coupling_factor`, and packet `classic_protection`.

Important APIs/types/functions: Uses `$TC qdisc add|show` with root `dualpi2`. The runner checks output regexes and expected successful exits.

Control flow: Each test installs a root DualPI2 qdisc with one option set and verifies the qdisc show output. There are no negative cases in this file.

State and persistence: State is a root DualPI2 AQM qdisc on `$DUMMY`, removed by teardown.

Dependencies and integration points: Requires sch_dualpi2 and iproute2 support for all listed options. Integrates parser options into netlink attributes and display.

Risks: DualPI2 is newer than many qdiscs and may be absent in older kernels. Option names and output formatting are likely to be more version-sensitive than long-established qdiscs.

Test signals: All 12 cases expect exit `0` and one regex match showing the configured DualPI2 option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/dualpi2.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/etf.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/etf.json

Purpose: Defines 5 ETF qdisc tests covering default creation, `delta` nanoseconds, `deadline_mode`, `skip_sock_check`, and deletion.

Important APIs/types/functions: Uses `$TC qdisc add|del|show` with root `etf`. ETF options under test are time scheduling configuration fields that tc sends to the kernel.

Control flow: Creation cases install ETF with required clock/options and verify qdisc output. Delete removes handle `1:` and verifies absence.

State and persistence: State is the root ETF qdisc configuration. No packet scheduling workload is injected in this file.

Dependencies and integration points: Requires sch_etf and whatever clock/default parameters the test setup uses. Integrates tc parser and kernel ETF option display.

Risks: ETF can depend on clockid and socket-check semantics, and kernel support may vary. Without packet traffic, these tests validate configuration acceptance and display rather than runtime scheduling.

Test signals: All 5 cases expect exit `0`; option cases expect one matching `qdisc etf` line, and delete expects zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/etf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ets.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ets.json

Purpose: Defines 49 ETS qdisc tests for bands, quanta, strict bands, priomap validation/defaulting, class display, class change, invalid argument boundaries, and offload arithmetic wrap handling.

Important APIs/types/functions: Uses `$TC qdisc add|show` and `$TC class show|change` with `ets`. Options under test include `bands`, `quanta`, `strict`, `priomap`, and per-class `quantum`.

Control flow: Positive add cases test valid combinations of bands/quanta/strict/priomap, then verify normalized qdisc output. Negative cases deliberately exceed limits (17 bands/strict/quanta, too many priomap elements, priomap values above configured bands, missing values, zero quanta) and expect nonzero exits. Class cases show classes `:1`, `:2`, `:3`, strict classes, and mutate band quantum.

State and persistence: State is the ETS qdisc's band table, strict/quanta arrays, priority map, and class attributes. Teardown removes the root qdisc after each case.

Dependencies and integration points: Requires sch_ets and namespace setup; the offload wrap case uses `$ETH`, integrating with a non-dummy device path where offload accounting is relevant.

Risks: This is the densest option parser file in the subset. Boundaries such as 16 vs 17 bands, unset-priority defaulting, and u32 quanta sum wrap are sensitive to both parser and kernel validation. `$ETH` availability/offload behavior can differ from dummy device tests.

Test signals: Exit distribution is 29 success, 16 exit `1`, 3 exit `2`, and 1 exit `255`. Regexes verify exact priomap defaulting, class quantum changes, strict-band rejection, and the offload wrap qdisc line with quanta `4294967294 1 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ets.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fifo.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fifo.json

Purpose: Defines 16 FIFO-family qdisc tests for `bfifo`, `pfifo`, invalid handles/arguments, replace operations, duplicate/delete error paths, invalid handle syntax, and `pfifo_head_drop` enqueue behavior at limit zero.

Important APIs/types/functions: Uses `$TC qdisc add|replace|del|show`, `ping`, and output regexes for byte/packet limits and drop counters. Qdiscs under test are `bfifo`, `pfifo`, and `pfifo_head_drop`.

Control flow: Positive add/replace tests install FIFO qdiscs and verify `limit` output. Negative cases attempt invalid handles (`10000:`, `123^`), unsupported arguments, invalid limit format, duplicate root add, nonexistent delete, and double delete. The head-drop test configures limit zero, sends two pings, and verifies dropped packet count.

State and persistence: State is root FIFO qdisc configuration plus packet/drop counters in the head-drop case. Teardown removes qdisc state.

Dependencies and integration points: Requires base FIFO qdiscs, namespace dummy device, and ping. It integrates tc parser validation with kernel enqueue/drop accounting.

Risks: Expected exit codes span `0`, `1`, `2`, and `255`, so parser-vs-kernel validation order matters. Drop-counter tests can be timing-sensitive if packets do not traverse as expected.

Test signals: Seven cases expect success; the rest are negative. Regexes assert byte vs packet limit units (`b` vs `p`), absence after delete/failure, and `dropped 2` for `pfifo_head_drop` limit-zero behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fifo.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq.json

Purpose: Defines 19 FQ qdisc tests for default creation, limits, flow limits, quantum, initial quantum, maxrate, pacing, refill delay, low-rate threshold, orphan mask, timer slack, CE threshold, horizon options, delete, replace/change, and limit trimming with injected traffic.

Important APIs/types/functions: Uses `$TC qdisc add|del|replace|change|show`, `nsPlugin`, and `scapyPlugin` for the trimming test. Options include `limit`, `flow_limit`, `quantum`, `initial_quantum`, `maxrate`, `nopacing`, `refill_delay`, `low_rate_threshold`, `orphan_mask`, `timer_slack`, `ce_threshold`, `horizon`, and `horizon_cap`.

Control flow: Most cases install root FQ with a single option and verify normalized output. One invalid `initial_quantum 0x80000000` case expects exit `2`. Replace/change mutate limit. The scapy test queues packets, changes limit to one packet, and verifies trimmed qdisc output.

State and persistence: State is the root FQ scheduler, per-flow limits, pacing parameters, and queued packet state for trimming.

Dependencies and integration points: Requires sch_fq, namespace devices, and scapy. It integrates parser unit conversion with kernel FQ pacing/limit display.

Risks: Output includes many defaults and unit conversions (`100Kbit`, `100ms`, `100ns`, `100us`). The trimming test is traffic/timing-sensitive. CE threshold is only indirectly checked because the regex focuses on qdisc presence/defaults.

Test signals: Eighteen cases expect success and one expects exit `2`. Regexes confirm option rendering, delete absence, replacement/change output, and `limit 1p` after trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_codel.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_codel.json

Purpose: Defines 15 FQ_CODEL tests for default creation, limit, memory limit, target, interval, quantum, ECN/noecn, CE threshold, drop batch, combined settings, replace/change/delete, class display, and limit trimming.

Important APIs/types/functions: Uses `$TC qdisc add|replace|change|del|show`, `$TC class show`, `nsPlugin`, and `scapyPlugin`. Options include `limit`, `flows`, `memory_limit`, `target`, `interval`, `quantum`, `noecn`, `ce_threshold`, and `drop_batch`.

Control flow: Creation cases install root FQ_CODEL and verify full default/option output. Replace switches to `noecn`; change updates `limit`. Delete verifies absence. Class show checks class reporting. The scapy trimming test queues traffic then changes limit to one packet.

State and persistence: State includes FQ_CODEL qdisc parameters, flow table sizing, ECN/drop behavior flags, and runtime queued packets during trimming.

Dependencies and integration points: Requires sch_fq_codel, namespace devices, and scapy. Integrates class reporting with qdisc configuration.

Risks: Regexes are long and depend on default values (`limit 10240p`, `flows 1024`, `target 5ms`, `memory_limit 32Mb`, `drop_batch 64`). The class-show test expects zero class matches, which could shift if class reporting changes.

Test signals: All 15 cases expect exit `0`. Regexes validate option rendering, absence after delete, no class output, and `limit 1p` after queue trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_codel.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_pie.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_pie.json

Purpose: Defines 2 FQ_PIE tests: one for creating FQ-PIE with a large `flows 65536` value and one for limit trimming after packet injection.

Important APIs/types/functions: Uses `$TC qdisc add|change|show`, `nsPlugin`, and `scapyPlugin`. The primary qdisc grammar is `fq_pie flows` and `limit`.

Control flow: The first test installs root FQ_PIE with `flows 65536` and verifies qdisc output. The second queues ten scapy TCP packets, changes limit to `1`, and verifies the updated limit.

State and persistence: State is root FQ_PIE configuration and queued packets for trimming. Teardown deletes the root qdisc.

Dependencies and integration points: Requires sch_fq_pie, namespace devices, and scapy. Integrates large flow-table parsing with runtime queue trimming.

Risks: The test name says "invalid number of flows", but the expected exit is `0` and the regex expects `flows 65536`; this likely documents a regression/compatibility behavior rather than rejection. Scapy timing can affect trimming validation.

Test signals: Both cases expect success. Regexes verify `flows 65536` and `limit 1p` after change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_pie.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/gred.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/gred.json

Purpose: Defines 7 GRED tests for default setup, `grio`, `limit`, `ecn`, `harddrop`, parameter change, and class display.

Important APIs/types/functions: Uses `$TC qdisc add|change|show` and `$TC class show`. Options under test include `setup vqs`, `default`, `grio`, `limit`, `ecn`, `harddrop`, and virtual queue parameters (`DP`, probability, min/max, burst, avpkt, bandwidth).

Control flow: Creation tests install root GRED with setup/default options and verify output. The change case mutates VQ 1 RED parameters. Class display verifies class command behavior.

State and persistence: State includes GRED virtual queue configuration and changed RED thresholds. Teardown removes root qdisc.

Dependencies and integration points: Requires sch_gred and namespace dummy device. Integrates setup-time VQ allocation with later `change` operations.

Risks: GRED output contains nested VQ details and unit conversions (`60Kb`, `15Kb`, `25Kb`), making regexes version-sensitive. Class show expects no class output.

Test signals: All 7 tests expect exit `0`. Regexes confirm root GRED setup, option flags, changed VQ parameters, and zero class matches for class display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/gred.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hfsc.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hfsc.json

Purpose: Defines 8 HFSC tests for default qdisc creation, service-curve class creation (`sc`, `rt`, `ls`, `ul`), umax/dmax conversion, delete, class display, and upgrading an inner realtime class to service-curve state.

Important APIs/types/functions: Uses `$TC qdisc add|del|show` and `$TC class add|show`. The class grammar under test includes `hfsc sc`, `rt`, `ls`, `ul`, `rate`, `umax`, and `dmax`.

Control flow: Root HFSC is installed, classes are added with specific service-curve parameters, and `tc class show` output is matched for converted m1/d/m2 values. Delete removes the qdisc. The inner-class test adds nested HFSC classes and verifies upgraded `sc` and `rt` output.

State and persistence: State is an HFSC class tree with service-curve parameters. Teardown deletes the root qdisc and nested classes.

Dependencies and integration points: Requires sch_hfsc. Integrates tc service-curve parsing with kernel curve calculations and display.

Risks: Rate/unit conversion is exact in regexes (`2464Kbit`, `5ms`, `8bit`), which can be sensitive to formatting changes. Nested-class upgrade behavior targets a subtle class-state transition.

Test signals: All 8 cases expect exit `0`. Regexes verify qdisc existence, class service-curve output, delete absence, root class display, and inner class upgrade.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hfsc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hhf.json -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hhf.json

Purpose: Defines 10 HHF tests for default creation, limit, quantum, reset timeout, admit bytes, evict timeout, non-heavy-hitter weight, change, class display, and limit trimming.

Important APIs/types/functions: Uses `$TC qdisc add|change|show`, `$TC class show`, `nsPlugin`, and `scapyPlugin` for trimming. Options under test include `limit`, `quantum`, `reset_timeout`, `admit_bytes`, `evict_timeout`, and `non_hh_weight`.

Control flow: Creation cases install root HHF with one option and verify default plus option output. Change mutates `limit`. Class show checks no class output. The scapy test sends ten TCP packets, changes limit to `1`, and verifies the qdisc output.

State and persistence: State is HHF scheduler configuration, heavy-hitter tracking parameters, and queued packets during trimming. Teardown removes the root qdisc.

Dependencies and integration points: Requires sch_hhf, namespace devices, and scapy. Integrates heavy-hitter parameter parsing with runtime queue limit behavior.

Risks: Regexes depend on defaults (`hh_limit 2048`, `reset_timeout 40ms`, `admit_bytes 128Kb`, `evict_timeout 1s`, `non_hh_weight 2`) and unit rendering. Scapy timing may affect the trimming case.

Test signals: All 10 tests expect exit `0`. Regexes validate each option, class-show absence, and `limit 1p` after trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hhf.json -->

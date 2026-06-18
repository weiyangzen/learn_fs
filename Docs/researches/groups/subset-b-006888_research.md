<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/tunnel_key.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/tunnel_key.json

## Purpose
This JSON file is a TDC selftest fixture for the Linux `tc` tunnel_key action. It contains 39 cases in the `actions/tunnel_key` category and is meant to validate both parser behavior and kernel action persistence for `tc actions add`, `replace`, `list`, `get`, `flush`, and `del` against tunnel metadata operations. The fixture covers the main `set` and `unset` modes, IPv4 endpoint arguments, tunnel key IDs, destination UDP ports, checksum flags, fragmentation flags, Geneve option encoding, control opcodes, cookies, batching-visible listing, and delete/flush lifecycle paths.

## Important APIs, Types, And Functions
The executable API is the TDC JSON schema plus the `tc` CLI. Each case uses fields such as `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`. The required plugin is `nsPlugin`, so the harness runs the cases in a network namespace with test devices and the `$TC` command variable available. The tested action API is `tc actions ... action tunnel_key`, especially `set src_ip ... dst_ip ... id ...`, `unset`, optional `dst_port`, `csum`/`nocsum`, `nofrag`, `no_percpu`, `cookie`, `index`, and control actions such as `pipe`, `continue`, `pass`, `reclassify`, `jump`, and `goto chain`.

## Control Flow
Most tests begin by flushing existing tunnel_key actions, run a single `cmdUnderTest`, then verify with either `tc actions list action tunnel_key` or `tc actions get action tunnel_key index N`. Positive cases expect exactly one regex match against the persisted action. Negative parser or range tests expect no persisted match and an error exit such as `1` or `255`. Replacement cases seed index `1` or `90` in setup, run `tc actions replace`, and verify that the previous object is overwritten only on valid input. List and flush tests create multiple indexed tunnel_key actions in setup, then check ordering or absence after flush. Delete tests seed a valid action and distinguish successful removal from an invalid-index delete that must leave the original action intact.

## State And Persistence Behavior
State is stored in the kernel action table keyed by `index`. The fixture explicitly tests persistence boundaries: successful `add` and `replace` commands must materialize visible action state, invalid arguments must not create state, invalid replace with `goto chain 42` must preserve the old action at index `90`, flush must remove all actions, and delete must only remove the addressed valid index. Index and ID bounds are important persistence gates: `4294967295` is accepted for action index and tunnel key ID, while larger values are rejected. `dst_port` is similarly tested at `65535` and beyond. `cookie` state is expected to survive and display in action dumps when valid.

## Dependencies And Integration Points
The fixture integrates with the tc-testing harness, network namespace plugin, kernel tunnel_key action implementation, iproute2 tunnel_key parser/printer, and regex-based result matching. Geneve option cases depend on iproute2 accepting `geneve_opts CLASS:TYPE:DATA` values and normalizing output as `geneve_opt` or `geneve_opts`. The list tests depend on stable enough dump formatting for multiple actions in one regex. No Ceph-specific code is involved despite the repository path; this is vendored Linux client selftest data.

## Risks
The tests are formatting-sensitive because assertions parse human-readable `tc` output. Small iproute2 wording changes, for example `key_id` versus `id` or singular versus plural Geneve option labels, can break matches even when kernel behavior is correct. Some negative cases expect different nonzero exits (`1` for address parse failures, `255` for missing or out-of-range action parameters), so harness or iproute2 changes to errno-to-exit mapping can create false failures. The multi-action list regex is broad and order-sensitive enough to catch regressions, but it can be brittle if dump ordering changes.

## Test Signals
Strong signals include valid mandatory set, missing `src_ip`/`dst_ip`, invalid IPv4 literals, invalid ID and port ranges, maximum accepted 32-bit and 16-bit bounds, unset mode, checksum and no-checksum persistence, valid and invalid cookies, valid and invalid Geneve option encodings, replace success and failure-preserves-old-state, all-action list, flush, delete success/failure, `no_percpu`, and `nofrag`. A passing run demonstrates both parser validation and kernel action table lifecycle behavior for tunnel_key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/tunnel_key.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/vlan.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/vlan.json

## Purpose
This fixture contains 36 `actions/vlan` TDC tests for the `tc` VLAN action. It validates the action parser and persisted action state for `pop`, `push`, and `modify`, plus replacement, deletion, flush, cookies, `no_percpu`, and batched action add/delete behavior. The cases cover valid behavior and boundary rejection for VLAN IDs, 802.1p priorities, action indices, protocols, opcodes, and goto-chain control.

## Important APIs, Types, And Functions
The JSON is consumed by the tc-testing harness and uses the standard TDC case fields: setup, command under test, expected exit code, verification command, regex match pattern, and teardown. The fixture requires `nsPlugin`. The primary command surface is `tc actions add|replace|del|flush|list|get action vlan`. Tested VLAN action forms include `vlan pop`, `vlan push id N [protocol 802.1Q|802.1AD] [priority N]`, and `vlan modify protocol ... id ... priority ...`. Control opcodes include `pipe`, `pass`, `drop`, `reclassify`, `continue`, `jump 10`, `trap`, and invalid `foo`.

## Control Flow
Most single-action tests flush all VLAN actions during setup, run an add or replace command, verify by `actions list` or `actions get action vlan index N`, and flush during teardown. Negative tests verify that invalid commands do not create matching action state. Replacement tests set up an action at the target index, replace one attribute such as ID, protocol, priority, or cookie, and verify the updated dump. Batch tests use shell loops to build 32 action specs and call `$TC actions add` or `$TC actions del` once with the accumulated arguments; verification counts index lines in the action dump.

## State And Persistence Behavior
The durable state under test is the kernel action table for VLAN actions, addressed by explicit or implicit action indices. Valid `pop` and `push` actions must persist with printed operation, control opcode, index, reference count, and optional cookie. The fixture tests maximum accepted index `4294967295` and rejection above that value. `push` defaults to protocol `802.1Q` and priority `0` when omitted. VLAN ID `4094` and priority `7` are accepted; out-of-range ID `5678` and priority `10` are rejected. Batch add/delete cases verify that multiple indexed action objects can be created and removed in a single command line.

## Dependencies And Integration Points
The file depends on the TDC harness, `nsPlugin`, iproute2 `tc` action parsing and output formatting, and the kernel VLAN action implementation. Batch cases depend on `/bin/bash`, `seq`, command substitution, and shell quoting inside `cmdUnderTest`. The fixture also relies on action dump counters and text such as `ref`, `bind`, protocol spelling, and cookie display. It integrates with shared gact-style control semantics through VLAN action opcodes and with tc action indexing infrastructure.

## Risks
Several match patterns intentionally assert printed defaults, such as protocol `802.1Q`, priority `0`, and `pipe`; these can fail if output formatting changes without semantic regression. Two `modify` cases have expected exit code `0` but `matchCount` `0`, indicating they may be documenting a parser acceptance path where the printed result does not match the optimistic pattern, or an historical expected output mismatch. Batch commands are sensitive to shell quoting and environment variables. `goto chain` rejection tests assume a specific invalid-chain policy and that the old action remains untouched.

## Test Signals
The fixture provides positive signals for every supported pop opcode, push defaults, explicit `802.1Q` and `802.1AD`, maximum VLAN ID and priority, modify mode, replacements, cookies, flush, delete, batch add/delete for push and pop, and `no_percpu`. Negative signals cover invalid opcode, invalid action mode, invalid protocol token, out-of-range ID/priority/index, and invalid goto chain replacement. Together these tests exercise both local parser validation and persistent action table lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/vlan.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/basic.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/basic.json

## Purpose
This file defines 60 tests for the `basic` classifier under `tc filter`. It focuses on ematch expression parsing and dump fidelity rather than packet forwarding. The fixture validates `cmp`, `u32`, and `canid` ematches, boolean composition with `not`, `and`, and `or`, action attachment, classid/flowid output, list/show behavior, and a set of malformed expression cases that must fail without leaving a filter behind.

## Important APIs, Types, And Functions
The JSON fixture uses the common TDC schema and requires `nsPlugin`. Its command surface is `tc filter add|get|show dev $DEV1 parent ffff: ... basic`. Each test installs an ingress qdisc on `$DEV1`, then adds or queries a basic filter under parent `ffff:`. Important filter arguments include `handle`, `protocol ip`, `prio`, `basic match '...'`, optional `classid 1:1`, and action chains such as `action pass`, `action skbedit mark 7 pipe action gact drop`, or `action gact drop`. Ematch APIs covered include `cmp(TYPE at OFFSET layer LAYER mask MASK [trans] OP VALUE)`, `u32(WIDTH VALUE MASK at OFFSET)`, and `canid(sff|eff ID[:MASK] ...)`.

## Control Flow
Every case creates ingress state in setup and deletes it during teardown. Add cases run one `tc filter add` command, then query the filter with `tc filter get` for a precise handle/prio/protocol or `tc filter show` for aggregate list cases. Positive tests assert a single match against normalized output. Negative parser tests expect exit code `1` and zero matches. The two list-oriented cases seed multiple filters in setup, then add or show additional filters and verify that dump counts match the expected number of basic classifier entries or ematch appearances.

## State And Persistence Behavior
The persisted state is a filter attached to the ingress qdisc. Handles are printed in hexadecimal, priorities are normalized as `pref`, and layer aliases are printed numerically: link as `0`, network as `1`, and transport as `2`. `cmp` tests ensure that parser choices survive dump output, including width, offset, layer, mask, comparison operator, and `trans`. `u32` tests exercise normalization of smaller widths into 32-bit value/mask display, negative offsets, and `nexthdr+` offsets. `canid` tests verify canonical uppercase hex display, mask truncation for SFF, and deterministic output ordering when SFF and EFF are mixed.

## Dependencies And Integration Points
The fixture depends on the ingress qdisc, basic classifier, ematch parser modules for `cmp`, `u32`, and `canid`, action modules such as gact and skbedit, and iproute2 output formatting. It also depends on TDC variable expansion for `$TC` and `$DEV1`. It integrates with shared classifier infrastructure through `parent ffff:`, `handle`, `protocol`, `prio`, and action chain syntax.

## Risks
The test suite is strongly coupled to printed normalization. For example, masks such as `0x00ff` may print as `0xff`, aliases print as numeric layers, and SFF CAN IDs are masked down before display. These are useful regression signals but can fail on harmless printer refactors. The negative `u32` cases mostly expect exit `1`, so changes in iproute2 parser error codes could require test updates. Because the tests attach to ingress qdisc state, teardown failures can cascade into later cases unless the harness isolates namespaces reliably.

## Test Signals
Positive signals cover `cmp` across link/network/transport layers, `trans`, u8/u16/u32 widths, single and multiple actions, boolean ematch composition, `u32` offsets including negative and `nexthdr+`, SFF/EFF CAN ID lists and masks, and list/show output. Negative signals cover over-wide `u32` values and masks, missing offsets, missing `at`, missing values, and non-numeric values or masks. A passing run shows that the basic classifier can parse, store, normalize, and dump a broad ematch surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/bpf.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/bpf.json

## Purpose
This compact fixture contains 7 tests for the `bpf` classifier. It validates classic BPF bytecode input, eBPF object-file loading, replacement, deletion, and listing under an ingress qdisc. The goal is to catch parser, verifier, loader, dump, and lifecycle regressions around `tc filter ... bpf`.

## Important APIs, Types, And Functions
The fixture uses TDC fields with `nsPlugin` and the `tc filter` API. Commands attach filters to `$DEV1` ingress under `parent ffff:` with `handle 1`, `protocol ip`, and `prio 100`. Classic BPF cases use `bpf bytecode '4,40 0 0 12,...'`; eBPF cases use `bpf object-file $EBPFDIR/action-ebpf section action-ok` or `section action-ko`. Verification uses `tc filter get ... bpf` and regexes for bytecode strings, object section names, 16-character program tags, and optional `jited` markers.

## Control Flow
Each case installs ingress qdisc state, runs the add/replace/delete/show command, verifies the resulting classifier state, then deletes the qdisc. Positive add cases assert one persisted filter. Invalid bytecode and invalid eBPF section tests expect nonzero exits and zero matches. Replacement seeds a valid cBPF filter, replaces bytecode with a different EtherType comparison, and verifies that the new bytecode is the visible state. Delete seeds a filter, deletes by handle/prio/protocol/classifier, and verifies absence. The list test seeds multiple BPF filters and counts dump entries.

## State And Persistence Behavior
Filter state is persisted under the ingress qdisc, keyed by handle, protocol, priority, and chain. Successful cBPF bytecode is dumped back exactly enough for regex comparison. Successful eBPF object loading persists a program reference whose dump includes object and section identity plus a verifier-generated tag. Invalid cBPF opcodes and invalid eBPF sections must not leave a visible filter. Replacement overwrites filter bytecode; deletion removes it from the classifier table.

## Dependencies And Integration Points
The file depends on tc-testing, `nsPlugin`, ingress qdisc support, classic BPF validation, eBPF object loading, `$EBPFDIR/action-ebpf`, kernel BPF verifier behavior, optional JIT status, and iproute2 BPF dump formatting. It integrates with kernel classifier infrastructure through the same `parent ffff:` and priority/handle model as other filter fixtures.

## Risks
The eBPF tests depend on a compiled object existing in `$EBPFDIR` with sections named `action-ok` and `action-ko`. Kernel verifier or JIT differences can alter exit codes or dump details, though the regex allows optional `jited`. Classic bytecode strings are compared literally, so printer formatting changes can break tests. Invalid bytecode expects exit `2`, while invalid object-file section expects exit `1`; those exact values can be fragile across iproute2 and kernel versions.

## Test Signals
The strongest signals are successful cBPF add, rejection of invalid cBPF instruction class, successful eBPF object/section load with a tag, rejection of invalid eBPF section, cBPF replacement, deletion, and multi-filter listing. Passing results indicate that both cBPF and eBPF paths are accepted, persisted, dumped, and removed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/bpf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/cgroup.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/cgroup.json

## Purpose
This fixture defines 56 tests for the `cgroup` classifier and its ematch support. It mirrors much of the basic classifier ematch coverage but attaches it to `tc filter ... cgroup`, validating how cgroup filters parse, store, dump, replace, and delete match expressions and action chains. Categories are mostly `filter/cgroup`, with at least one case also tagged `filter/drop`.

## Important APIs, Types, And Functions
The TDC schema fields drive `tc filter add|replace|delete|show dev $DEV1 parent ffff: ... cgroup`. The file requires `nsPlugin`. Tested command arguments include `handle`, `protocol ip`, `prio`, `cgroup match '...'`, and actions `drop`, `pass`, `pipe`, `skbedit mark 7 pipe`, and `gact drop`. The expression APIs are `cmp`, `u32`, and `canid`, with the same layer aliases, widths, masks, offsets, boolean operators, and SFF/EFF CAN ID syntax used by the basic fixture.

## Control Flow
Each test creates an ingress qdisc on `$DEV1`, executes a cgroup filter operation, verifies via `tc filter show dev $DEV1 parent ffff:`, and removes the qdisc. Positive add cases expect one match in dump output. Negative parser cases expect exit `1` and zero matches. Replacement seeds a cgroup filter, replaces its match expression, and verifies the new normalized `cmp` expression. Deletion removes the previously installed filter and verifies that the old expression is no longer present.

## State And Persistence Behavior
The persisted state is a cgroup classifier instance attached to ingress. Output includes protocol, priority, classifier name, chain number, handle, normalized ematch expressions, and attached action state. The fixture checks normalization of `cmp` layers (`link` to `0`, `network` to `1`), `trans` display, boolean operators, `u32` value/mask expansion, negative offsets, `nexthdr+` offsets, and CAN ID display. Invalid ematch syntax or out-of-range value/mask inputs must fail before state is installed.

## Dependencies And Integration Points
The file depends on cgroup classifier support, ematch modules, ingress qdisc support, gact and skbedit actions, tc-testing variable expansion, and namespace isolation. It integrates with common tc classifier mechanics (`parent ffff:`, `protocol`, `prio`, `handle`, `chain`) and with the same ematch parser used by other classifiers. Its show-based verification makes it more dependent on dump formatting than on packet-level behavior.

## Risks
One negative case named as a cgroup test uses `basic match` in `cmdUnderTest`, which likely intentionally checks that an invalid command does not produce cgroup output, but it is a maintenance trap. The fixture has many format-sensitive regexes for normalized masks, CAN ID order, and action output. Because most verification uses `show` rather than `get`, unrelated filters left behind by failed teardown could affect match counts if namespace isolation breaks. Exact parser exit code `1` is assumed across malformed `u32` cases.

## Test Signals
Signals include successful cgroup filters with `cmp` widths and layers, boolean ematch composition, `u32` across widths and offset forms, SFF/EFF CAN ID matches and masks, action attachment, replacement to a different match, and deletion. Negative signals cover over-wide values/masks, missing syntax elements, and non-numeric fields. Passing results demonstrate that cgroup classifier ematches share the expected parser and dump behavior with basic while preserving cgroup-specific classifier state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/cgroup.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flow.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flow.json

## Purpose
This fixture contains 28 tests for the legacy `flow` classifier. It validates map and hash key selection, arithmetic/logical map operations, divisor and baseclass output, optional ematch/action attachment, listing, change, replace, and delete behavior. The tests are mostly positive lifecycle and dump-fidelity cases.

## Important APIs, Types, And Functions
The JSON uses the normal TDC schema with `nsPlugin`. Commands use `tc filter add|change|replace|delete|get|show dev $DEV1 parent ffff: handle 1 prio 1 protocol ip flow`. Tested `flow` arguments include `map key KEY`, operations `and`, `or`, `xor`, `rshift`, and `addend`, `hash keys src`, `divisor 1024`, `baseclass 1:1`, ematch `match 'cmp(...)'`, and `action drop`. Map keys covered include `dst`, `src`, `proto`, `proto-src`, `proto-dst`, `iif`, `priority`, `mark`, `nfct`, `nfct-dst`, `nfct-src`, `nfct-proto-src`, `nfct-proto-dst`, `rt-classid`, `sk-uid`, `sk-gid`, `vlan-tag`, and `rxhash`.

## Control Flow
Each case installs an ingress qdisc, runs a flow filter command, verifies with `tc filter get` or `tc filter show`, and removes the qdisc. Add cases verify normalized output for the chosen key and operation. The multi-operation case combines hash key selection, divisor, baseclass, a `cmp` ematch, and a drop action in one filter. The list case seeds two flow filters and expects two `rxhash` map-key dump entries. Change and replace cases mutate an existing `rxhash` addend, then verify the new value. Delete removes the matching flow filter and verifies absence of the prior replace state.

## State And Persistence Behavior
The persisted state is a flow classifier instance attached to ingress. Map operations are normalized in dumps: for example `and 0xff` becomes `and 0x000000ff`, `or 0xff` becomes `or 0x000000ff`, and `rshift 0x1f` prints as decimal `31`. `addend` remains displayed as a hex addend. `baseclass` is present by default and can be explicitly set to `1:1`. Change and replace modify the existing filter state rather than requiring delete/add.

## Dependencies And Integration Points
The fixture depends on the flow classifier, ingress qdisc, tc-testing namespace setup, ematch support for the combined case, and gact action support. Some keys, especially netfilter connection tracking keys and socket UID/GID keys, depend on parser support even though the tests do not inject packets. The fixture integrates with common filter infrastructure through handle, prio, protocol, parent, and chain output.

## Risks
The flow classifier is older and less commonly used than flower, so kernel or iproute2 support may vary by configuration. Regexes are tightly coupled to textual normalization of integer operations. There are no negative parser tests in this file, so it mainly proves accepted syntax and lifecycle behavior, not rejection boundaries. The delete test verifies absence of a replaced state pattern; if delete matching semantics change, this could miss some unrelated residual state.

## Test Signals
The fixture signals parser support for all listed map keys, logical/arithmetic operations, hash-key mode, combined divisor/baseclass/ematch/action syntax, list counts, change, replace, and delete. A successful run means flow classifier state can be created, queried, updated, dumped, and removed through the standard tc filter lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flow.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flower.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flower.json

## Purpose
This fixture contains 12 high-scale and concurrency-focused tests for the `flower` classifier. Unlike the parser-heavy fixtures, this file stresses large rule counts, parallel `tc -b` execution, duplicate-key handling, shared action reference accounting, maximum handle display, and terse dump behavior. Categories include `filter/flower` and `filter/flower/concurrency`.

## Important APIs, Types, And Functions
The main API is `tc filter ... flower` on `$DEV2` ingress. The fixture also depends on helper scripts `tdc_multibatch.py` and `tdc_batch.py`, `$BATCH_DIR`, `$BATCH_FILE`, `find`, `xargs`, and parallel `tc -b` execution. Commands add, delete, or replace generated batches using `xargs -n 1 -P 10 $TC -b`, sometimes with `$TC -f -b` to force continuation on delete races. Single-rule cases use fields such as `handle 0xffffffff`, MAC/IP/TCP flower keys, `action ok`, and `action drop`. Terse dump uses `$TC -br filter show`.

## Control Flow
High-scale cases create `$BATCH_DIR`, install ingress on `$DEV2`, generate batch files for add/delete/replace workloads, execute those batches in parallel, and verify counts from `tc -s filter show dev $DEV2 ingress`. The first three tests add, delete, and replace 1 million filters. Two tests concurrently replace or delete the same 100k range from 10 tc instances. Two mixed tests add/delete or replace/delete from the same tcf_proto concurrently and expect half a million remaining filters. Other cases add a max-handle filter, add 1 million filters sharing one action, attempt a duplicate-key add, and verify terse dump content.

## State And Persistence Behavior
The persisted state is large flower filter tables under `$DEV2` ingress plus referenced gact action state. Count-based assertions expect exactly 1,000,000, 500,000, 100,000, zero, or one flower dump entries depending on the workload. The shared-action case verifies one gact action at index `1` with `ref 1000000 bind 1000000`, proving that many filters can bind the same action without creating separate actions. Duplicate-key handling expects the second add to fail with exit `2` and only one filter remaining. Terse dump state must show a filter handle but omit detailed keys such as `dst_mac`.

## Dependencies And Integration Points
This file depends heavily on helper scripts in the tc-testing directory, batch-file generation, shell utilities, parallel process scheduling, `$DEV2`, ingress qdisc support, flower classifier scaling, action reference counting, and iproute2 terse and statistics dump modes. It integrates with kernel classifier locking and concurrency paths more than with packet-match semantics.

## Risks
These tests are resource-intensive by design. Adding or replacing 1 million filters can consume significant CPU, memory, time, and kernel table resources, and parallel batches may expose timing-dependent failures. Count assertions are only as reliable as the generated batch files and cleanup. The expected exit `123` for forced parallel delete is from `xargs`, not directly from `tc`, so environment differences can change it. Terse dump assertions are sensitive to iproute2 output policy.

## Test Signals
Strong signals include successful million-rule add/delete/replace, safe concurrent replace/delete behavior on the same range, predictable mixed add/delete and replace/delete outcomes, maximum 32-bit flower handle display, shared gact action reference scaling to one million binds, duplicate-key rejection, and terse dump suppression of key details. Passing this fixture gives confidence in flower scalability, locking, reference accounting, and dump modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flower.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/fw.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/fw.json

## Purpose
This fixture defines 62 tests for the `fw` classifier, which classifies packets by firewall mark. It validates parser boundaries, action attachment by value and by reference, cookies, handle/mask parsing, parent and protocol requirements, classid/flowid behavior, action reference counts, police actions, deletion selectors, replacement, and class reference behavior after replacement.

## Important APIs, Types, And Functions
The TDC schema drives `tc filter add|del|replace|get|show dev $DEV1 ... fw` plus related `tc action` and `tc class` setup in some cases. The file requires `nsPlugin`. The tested syntax includes `parent ffff:` or `parent 10:`, `handle VALUE[/MASK]`, `prio`, `protocol all|ip|ipv6|arp|802_3`, `fw`, `classid`, `flowid`, and actions `ok`, `continue`, `pipe`, `drop`, `reclassify`, `jump 10`, `goto chain 5`, `gact index N`, `cookie`, and `police rate ... burst ... linklayer atm`.

## Control Flow
Most tests set up ingress and sometimes pre-create referenced gact actions, add a fw filter, verify with `tc filter get` or `show`, then delete ingress. Negative add tests assert nonzero exits and zero matches for invalid prio, invalid action, missing action, invalid handles/masks, missing parent, invalid classid, invalid protocol, and priority/protocol conflicts. Delete tests seed multiple filters, then delete by whole parent, single handle/prio/action forms, prio, chain, or invalid selectors. Replace tests seed a filter and replace action, classid, or action index. One case attempts to delete a class referenced by fw after replacement and expects the class to remain visible.

## State And Persistence Behavior
Fw filter state is keyed by parent, priority, protocol, handle, optional mask, and chain. Handles and masks are normalized to hexadecimal, with 32-bit maximum accepted and larger values rejected. Priority `65535` is accepted while `65536` is rejected. `classid` and `flowid` map to printed classid state, with later duplicate classid/flowid-style arguments taking precedence. Referenced gact actions show increased `ref` and `bind` counts. Police actions persist rate, burst, mtu, action, overhead, linklayer, index, ref, and bind output. Replacement changes existing filter state, and class deletion is prevented while the fw filter still references the class.

## Dependencies And Integration Points
The fixture depends on ingress qdisc support, fw classifier support, gact and police action modules, class/qdisc setup for class reference tests, and iproute2 parser/printer behavior. It integrates with shared tc action reference accounting, class binding semantics, protocol parsing, chain deletion, and parent selector handling. It also exercises action lookup by pre-created `gact index 1` references.

## Risks
The file is broad and output-sensitive. It assumes exact printed forms for `ok` as `gact action pass`, root classid as `root`, large classid truncation to the last 8 hex digits, and police rate formatting such as `1Kbit` and `10Kb`. Several invalid delete forms expect exit `2` while leaving state intact. The typo in names saying `maxixum` is harmless but signals old fixture text. Any changes in ref/bind accounting, class deletion policy, or protocol conflict handling can affect multiple cases.

## Test Signals
Signals include accepted and rejected priority bounds, all common gact actions by value and by reference, cookies and invalid cookies, hex and decimal handle/mask parsing, mandatory parent/handle/action enforcement, classid and flowid precedence, protocol variants and invalid protocol, duplicate priority/protocol rejection, shared action index accounting, police action variants, full and selective deletes, invalid deletes that preserve state, replacement of action/classid/index, class reference protection, and replacement with nil classid. Passing results indicate robust fw classifier parsing and lifecycle behavior across many tc subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/fw.json -->

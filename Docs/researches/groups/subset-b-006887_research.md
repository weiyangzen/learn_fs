# Grouped research report: subset-b-006887

This grouped report covers Linux `tc-testing` action manifests from `sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mirred.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mirred.json

## Purpose

`mirred.json` is a declarative tc-testing manifest for the `mirred` traffic-control action. It validates mirror and redirect behavior for ingress and egress directions, target selection by device or shared block, control-action encoding, index handling, batch add/delete behavior, and loop-prevention statistics for redirect-to-self paths. The file contains 34 test cases.

## Important APIs, Types, and Schema

The file is a JSON array of test objects consumed by the tc-testing runner. Each object uses the standard manifest fields: `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern` or `matchJSON`, `matchCount`, and `teardown`. Several blockid tests also use `dependsOn` to gate execution on `tc action mirred help` advertising `blockid`.

The tc API surface under test is `$TC actions add|replace|del|flush|list|show|get action mirred`. The command grammar exercised includes `ingress` and `egress`, `mirror` and `redirect`, `dev <ifname>`, `blockid <id>`, action `index`, `cookie`, `no_percpu`, and control actions such as `pass`, `pipe`, `continue`, `reclassify`, `drop`, and `jump <chain>`. The later filter-path tests use `$IP link`, `$IP addr`, `$TC qdisc add`, and `$TC filter add ... matchall action mirred`.

## Control Flow

Most cases flush existing `mirred` actions during setup, run a single `$TC actions ...` command, then verify with `list`, `show`, or `get`. Positive text-output tests match strings such as `Egress Mirror to device lo`, `Egress Redirect to device lo`, control action names, index values, `cookie`, and `no_percpu`. Negative parser tests expect exit code `255` and verify that the rejected action is absent.

The block-target tests add `clsact` qdiscs with `ingress_block` or `egress_block` on `$DEV1`, then add or replace `mirred` actions targeting block id 21. These tests verify structured JSON from `$TC -j actions get`, including `kind`, `mirred_action`, `direction`, `to_blockid` or `to_dev`, `control_action.type`, `index`, `ref`, `bind`, and `not_in_hw`.

The final two cases leave pure action management and install filters on `$DUMMY`. They send one ping that is expected to fail and verify action stats in JSON: `packets: 1` and `overlimits: 1`, proving redirect loop protection increments counters.

## State and Persistence Behavior

State lives in kernel tc action tables and qdisc/filter state inside the test network namespace. The manifest is careful to isolate that state with `actions flush action mirred`, `qdisc del`, and action flush teardown. Duplicate index and replace cases intentionally pre-populate state to prove collision or replacement semantics. Batch cases create 32 indexed actions with shell loops and then delete them as a group.

## Dependencies and Integration Points

All tests require `nsPlugin`, so they assume an isolated network namespace and variables such as `$TC`, `$IP`, `$DEV1`, and `$DUMMY`. Device-target tests use loopback `lo`; block tests require kernel/iproute2 support for `blockid`; loop tests require qdisc and matchall filter support. The manifest integrates with tc-testing's text regex matcher and JSON matcher.

## Risks

Text-output assertions are sensitive to iproute2 formatting changes, especially wording around `Mirror`, `Redirect`, `ref`, `no_percpu`, and control names. Blockid assertions are stricter and depend on JSON fields such as `not_in_hw`; offload-capable environments or changed JSON defaults could affect them. The pattern `[Mirror|Redirect] to device lo` is a character-class style regex rather than a true alternation, so it is less precise than intended. The ping tests use a very short timeout (`-W0.01`), which can be sensitive to ping implementation and timing.

## Test Signals

Coverage is broad: valid egress and ingress mirror/redirect, invalid direction/action/device, duplicate index, all common control actions, cookie, 32-bit maximum index, out-of-range index, delete behavior, 32-action batches, `no_percpu`, dev/block mutual exclusion, missing target rejection, dev-to-block and block-to-dev replacement, and redirect loop accounting. Expected failures consistently use `expExitCode: 255` and absence checks, while expected successes assert exactly one or 32 matching actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mirred.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mpls.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mpls.json

## Purpose

`mpls.json` defines 53 tc-testing cases for the `mpls` action. It validates parsing and rendering for `dec_ttl`, `pop`, `push`, and `mod` operations, including valid and invalid MPLS label, traffic class, TTL, BOS, protocol, cookie, replace, delete, and flush behavior.

## Important APIs, Types, and Schema

The manifest uses the standard tc-testing object schema: identity and category metadata, `nsPlugin`, setup flushes, command under test, expected exit code, verification command, regex match pattern/count, and teardown. The tc API surface is `$TC actions add|replace|del|flush|list|get action mpls`.

The command grammar under test covers `mpls dec_ttl`, `mpls pop protocol <proto>`, `mpls push [protocol mpls_uc|mpls_mc] label <label> [tc <tc>] [ttl <ttl>] [bos <0|1>]`, and `mpls mod label|tc|ttl|bos`. It also validates tc control opcodes: `pipe`, `pass`, `drop`, `reclassify`, `continue`, `jump 10`, and `trap`.

## Control Flow

Each test begins with an `mpls` action flush and then executes a single tc action command. Verification usually lists all `mpls` actions or gets a specific index and matches iproute2 output for operation name, normalized protocol, normalized numeric fields, control action, index, refcount, and cookie. Replace tests pre-create an action then call `actions replace` and assert the new rendered action. Delete and flush tests pre-populate state and then assert that matching entries disappear.

## State and Persistence Behavior

State is maintained in the kernel action table for `mpls`. Most tests use a clean table per case. Replace cases persist a known action at an index and verify replacement rather than addition. The maximum-value checks rely on parser limits rather than persistent data structures: label maximum `0xfffff` is accepted and rendered as `1048575`; `0x100000` is rejected. TTL bounds are 1 through 255, and TC bounds are 0 through 7.

## Dependencies and Integration Points

The suite requires `nsPlugin`, `$TC`, and kernel/iproute2 support for the `mpls` action. It integrates only through action management commands, not through packet datapath filters. It depends on iproute2 rendering names such as `modify` for `mod`, `protocol mpls_uc`, `protocol mpls_mc`, `protocol ip`, and textual control opcodes.

## Risks

The tests are mostly regex-based and therefore exposed to output-format changes. Protocol aliases are a risk because commands use `ipv4` while expected output may contain `ip`. Some invalid tests assert absence via broad patterns, so a future output change could hide a parser regression. The `a70a` invalid TC test looks for `tc.*4` despite issuing `tc 8`, which may make that absence check weaker than intended.

## Test Signals

The file strongly covers operation-specific parser rules: `dec_ttl` rejects label/tc/ttl/bos parameters; `pop` requires protocol and rejects label/tc/ttl/bos; `push` requires an MPLS label and rejects IPv4 protocol, out-of-range label, TC 8, and TTL 0; `mod` accepts label/TC/TTL/BOS modification but rejects out-of-range label, implicit-null label 3, TTL 0/256, BOS 2, and protocol. It also covers cookie rendering, maximum cookie length, replacing push actions, deleting one action, and flushing all actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mpls.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/nat.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/nat.json

## Purpose

`nat.json` contains 27 tc-testing cases for the `nat` action. It validates ingress and egress address translation syntax, control actions, index bounds, special address keywords, cookies, replace rejection for unsupported goto-chain control, and delete behavior.

## Important APIs, Types, and Schema

The manifest uses standard test keys for tc-testing: `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`. It requires `nsPlugin` and drives `$TC actions add|replace|del|flush|ls|get action nat`.

The command grammar under test is `nat ingress <oldaddr> <newaddr>` and `nat egress <oldaddr> <newaddr>` with optional control action, `index`, and `cookie`. Address operands include explicit IPv4 addresses and aliases `default`, `any`, and `all`, which should render as `0.0.0.0/0`.

## Control Flow

Cases flush `nat` state before setup. Positive add cases execute the command and verify text output via `ls` or `get`. The expected rendering includes direction, normalized source prefix, replacement address, control action, index, ref, and cookie when present. Negative cases expect exit code `255`, then query the would-be index and assert zero matches. Delete cases pre-create an action, delete by index, and assert absence, or attempt deletion of a non-existent index and assert the existing action remains.

## State and Persistence Behavior

State is confined to tc action entries of kind `nat`. Index tests explicitly exercise maximum 32-bit index `4294967295` and rejection of larger values. The invalid goto-chain replace test starts with an existing action at index 90 and then verifies that the invalid replacement does not overwrite the old `drop` action. Special address aliases persist in normalized CIDR form.

## Dependencies and Integration Points

The file depends on `$TC`, iproute2 support for `nat`, and a test namespace. It does not install filters or send packets, so it validates parser and action-table behavior rather than datapath translation. It integrates with tc-testing through regex assertions.

## Risks

The action is older and output has double spaces in patterns such as `action order ...:  nat`, making the tests sensitive to spacing changes. Alias rendering for `default`, `any`, and `all` is assumed to normalize to `0.0.0.0/0`; output changes there could cause false failures. Since no packets are sent, the file does not prove actual NAT rewriting, only command parsing and action representation.

## Test Signals

Coverage includes default `pass`, `pipe`, `continue`, `reclassify`, `jump`, and `drop` for ingress and egress, maximum index, invalid oversized index, invalid IPv4 address, stray argument rejection, special address aliases, cookie output for both directions, invalid goto-chain replace preservation, valid delete, and invalid delete. Successful cases expect exactly one match; rejected parse paths expect no persisted action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/nat.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/pedit.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/pedit.json

## Purpose

`pedit.json` is a large parser and rendering suite for the `pedit` action, with 69 test cases. It validates raw offset edits, layered protocol edits, masks, retain/clear/invert/preserve/add/set operations, IPv4, IPv6, Ethernet, TCP, UDP, mixed edit sequences, control actions, and rejection paths.

## Important APIs, Types, and Schema

The file uses tc-testing manifest objects with `nsPlugin`, setup flushes, command under test, expected exit status, verification command, regex pattern/count, and teardown. The tc API is `$TC actions add|replace|ls|list action pedit`; many verification commands pipe to `grep 'key '` to focus on generated pedit keys.

The command grammar under test has two major forms. Raw operations use `munge offset <n> u8|u16|u32` plus `set`, `add`, `clear`, `invert`, `preserve`, `retain`, and dynamic `at <off> <offmask> <shift>`. Layered operations use `ex munge eth|ip|ip6|tcp|udp <field> <operation>`. The assertions inspect rendered key offsets, values, and masks.

## Control Flow

Each case generally starts from an empty `pedit` table. A command builds one or more pedit keys. Verification lists the action and matches the expected normalized key sequence. Invalid cases usually use `/bin/true` as `verifyCmd` with zero expected matches, meaning the primary signal is the command exit code. The invalid goto-chain replace case pre-populates index 90 and verifies the existing action remains after rejected replacement.

## State and Persistence Behavior

The key persistent state is the pedit action entry, including number of keys, action control, index, cookie, and ordered key list. Tests rely on ordering of emitted keys for multi-key operations. Negative raw offsets and mixed raw/layered cases show that pedit stores offsets relative to different protocol bases and can create several keys from one logical field, such as MAC or IPv6 addresses.

## Dependencies and Integration Points

The tests require `nsPlugin` and `$TC` with pedit support. They integrate with iproute2's pedit parser and pretty-printer rather than packet transmission. Layered `ex` operations depend on protocol header knowledge in iproute2 and kernel pedit support for extended keys.

## Risks

This file is highly sensitive to rendered key formatting, endian presentation, and mask normalization. Many regexes assume exact key order, spacing, and base names such as `ipv4+`, `ipv6+`, `eth+`, `tcp+`, and `udp+`. Invalid tests that verify with `/bin/true` do not independently query the action table, so they rely entirely on exit code and teardown. Mixed protocol edits do not prove packet correctness, only that keys are accepted and rendered.

## Test Signals

Coverage is deep. Raw tests cover aligned and misaligned offsets, u8/u16/u32 packing, overflow offsets, retain masks, clear/invert/preserve semantics, negative offsets, and dynamic offset metadata. Ethernet tests cover source, destination, type, add, invert, and invalid MAC/type values. IPv4 tests cover src/dst, ihl, dsfield, ttl, protocol, flags/fragment fields, tos/precedence operations, duplicate fields, transport-port aliases, and invalid TTL or missing extended mode. IPv6 tests cover src/dst expansion, traffic class, flow label, payload length, next header, hop limit, and invalid retain. TCP/UDP tests cover ports and flags. The final mixed cases ensure raw and layered edits can coexist in one action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/pedit.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/police.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/police.json

## Purpose

`police.json` defines 34 tc-testing cases for the `police` action. It verifies rate and burst parsing, MTU and peakrate coupling, overhead and linklayer options, conform-exceed control pairs, standalone control actions, packets-per-second policing, cookies, maximum index, listing, getting, deleting, flushing, and skip hardware flags.

## Important APIs, Types, and Schema

The manifest uses the common tc-testing schema and requires `nsPlugin`. Commands exercise `$TC actions add|delete|flush|ls|list|get|show action police`. The police grammar under test includes `rate`, `burst`, `mtu`, `peakrate`, `overhead`, `linklayer`, `conform-exceed`, `pkts_rate`, `pkts_burst`, `index`, `cookie`, `skip_hw`, and controls such as `continue`, `drop`, `ok`, `reclassify`, and `pipe`.

## Control Flow

Cases flush police actions, optionally pre-create an entry, run the command under test, and verify with list/show/get. Regexes assert normalized rates, bursts, MTU, peakrate, overhead, linklayer, action controls, index values rendered in hexadecimal for police handles, cookies, and skip flags. Negative cases expect `255` and absence of the invalid rendering.

## State and Persistence Behavior

Police action state includes rate tables, burst/MTU, optional peakrate table, linklayer metadata, conform/exceed actions, packet-rate fields, cookie, and index. Duplicate-index and invalid replace tests intentionally preserve existing state. The maximum index test uses `4294967295`, rendered as `0xffffffff`.

## Dependencies and Integration Points

The file depends on kernel police action support and iproute2 unit parsing. It is action-table focused and does not attach filters or send traffic. It integrates with tc-testing regex matching and relies on unit normalization such as `1Kbit`, `10Kb`, `2Kb`, `1024Kb|1Mb`, and packet-rate fields.

## Risks

Unit rendering is the largest stability risk because iproute2 may normalize bits, bytes, and metric suffixes differently. Some patterns encode default MTU values (`2Kb` or very large packet MTU for pps mode) and default action `reclassify`, which can change across implementations. The tests validate parser state but not actual policing behavior under traffic load.

## Test Signals

The suite covers valid basic policing, duplicate index rejection, MTU, peakrate requiring MTU, overhead, Ethernet and ATM linklayers, conform-exceed pairs including numeric control IDs, invalid rate/burst/peakrate/MTU values, cookie, maximum index, delete, get single action, get without index rejection, list many actions, flush, individual control actions, invalid goto-chain controls, packet-per-second policing, rejection of combined bps and pps mode, and `skip_hw` rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/police.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/sample.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/sample.json

## Purpose

`sample.json` contains 29 tc-testing cases for the `sample` action. It validates mandatory `rate` and `group` parsing, optional truncation, control actions, index and field bounds, cookies, replacement of existing actions, invalid goto-chain preservation, and delete behavior.

## Important APIs, Types, and Schema

The manifest uses standard tc-testing JSON fields and requires `nsPlugin`. It drives `$TC actions add|replace|del|list|get action sample`. The action grammar under test is `sample rate <u32> group <u32> [trunc <u32>] [control] [index <u32>] [cookie <hex>]`. Controls include default `pipe`, `continue`, `drop`, `reclassify`, `pipe`, and `jump <chain>`.

## Control Flow

Each test flushes sample actions in setup. Positive add cases verify rendered text such as `sample rate 1/<rate> group <group>`, optional `trunc_size`, control action, index, refcount, and cookie. Mandatory-argument and range failures expect exit code `255` and verify absence. Replacement cases pre-create an index, replace one field, and assert the new value. Delete cases check both successful deletion and failed deletion of a missing index.

## State and Persistence Behavior

State is held in the tc sample action table. Tests verify 32-bit maximum values for `rate`, `group`, `trunc`, and index, and reject values above that range. The invalid goto-chain replace test preserves a previous action at index 90, proving rejected replacement does not corrupt existing state.

## Dependencies and Integration Points

The file depends on `$TC`, `nsPlugin`, and kernel/iproute2 support for `sample`. It does not require psample userspace listeners and does not validate sampled packet delivery; it validates action creation, representation, replacement, and deletion.

## Risks

Because no traffic is generated, runtime sampling behavior and psample netlink emission are outside coverage. Regexes are tied to the textual `rate 1/N`, `trunc_size`, and default `pipe` rendering. There are two tests with the same name and command for missing `group`, which is harmless but redundant.

## Test Signals

Signals include positive coverage for all common controls, invalid `rate 0`, invalid unknown control, missing mandatory arguments, maximum and out-of-range values for rate/group/trunc/index, cookies, replace rate/group/trunc/control at a stable index, invalid goto-chain replace preserving old state, valid delete, and invalid delete preserving existing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/sample.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/simple.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/simple.json

## Purpose

`simple.json` defines 9 tc-testing cases for the `simple` action. It validates simple string payload storage through `sdata`, change and replace behavior, duplicate index rejection, listing, deletion, flushing, and cleanup after failed batched action operations.

## Important APIs, Types, and Schema

The file follows the standard tc-testing manifest schema and uses `$TC actions add|change|replace|delete|flush|list action simple`. The primary command grammar is `simple sdata <string> [index <u32>]`, with optional invalid `goto chain` and `cookie` in the replace rejection case.

## Control Flow

Tests flush or pre-create simple actions, execute a tc action command, and verify with `actions list action simple`. Positive assertions match rendered strings such as `Simple <A triumph>` and index/ref output. Negative assertions check that duplicate add and invalid goto-chain replace do not create or overwrite the target action. The last two tests exercise batch cleanup behavior by arranging a failed batch setup and then verifying only the expected action remains.

## State and Persistence Behavior

The action table stores an indexed simple action and its string payload. `change` mutates an existing action at index 60. Delete and flush remove persisted entries. The invalid replace test verifies an existing `hello` action at index 90 remains after a rejected `goto chain` replacement.

## Dependencies and Integration Points

The manifest depends on `nsPlugin`, `$TC`, and the kernel simple action. It is integrated only through action management commands and regex matching. It provides a small sanity suite for action lifecycle behavior that is simpler than parser-heavy action types.

## Risks

The action's output format is concise, so regexes are sensitive to `Simple <...>` formatting and capitalization. The file does not test packets or action execution, only storage and management. Batch-cleanup tests depend on setup semantics in the tc-testing runner, so their meaning is partly outside the JSON object itself.

## Test Signals

Signals include successful add, successful change, duplicate index rejection, listing three preloaded actions, delete, flush, invalid goto-chain replace preserving old state, and cleanup validation for failed batch add/change scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/simple.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbedit.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbedit.json

## Purpose

`skbedit.json` contains 30 tc-testing cases for the `skbedit` action. It validates packet metadata edits for mark, mark mask, priority, queue mapping, packet type, control actions, cookies, index bounds, batch add/delete, and rejection of invalid values.

## Important APIs, Types, and Schema

The manifest uses standard tc-testing fields and requires `nsPlugin`. It drives `$TC actions add|replace|del|flush|list|get action skbedit`. The action grammar under test includes `mark <u32>[/<mask>]`, `prio|priority`, `queue_mapping <u16>`, `ptype host|otherhost`, `inheritdsfield`, control actions, index, and cookie.

## Control Flow

Tests flush `skbedit`, run an add/replace/delete/list/get operation, then assert textual output. Positive cases match normalized mark/mask, priority formatting as `priority :N`, queue mapping, ptype, control action, index, ref, cookie, and batch-created entries. Negative cases expect exit code `255` and assert the invalid value is absent.

## State and Persistence Behavior

State resides in the tc action table. Replace updates an existing mark mask at index 1. Index bounds are explicitly covered with maximum `4294967295` and rejection of `4294967297`. Batch tests create 32 actions with all parameters and cookie, then delete the same 32 indexes. Invalid goto-chain replace preserves an existing action at index 90.

## Dependencies and Integration Points

The tests require `$TC`, `nsPlugin`, and skbedit action support. They are parser/action-table tests, not datapath tests. The batch cases use shell loops in `cmdUnderTest`, so they also depend on `bash` and `seq` availability in the test environment.

## Risks

Output spacing around `skbedit  mark`, priority formatting, and mask normalization is fragile. The tests do not verify packet metadata changes on live packets, only creation and rendering. Batch command construction uses shell quoting and accumulated arguments, which can fail differently if shell behavior changes.

## Test Signals

Coverage includes valid marks, 32-bit mark maximum, out-of-range marks, valid masks including `0xffffffff`, invalid oversized and malformed masks, replace mask, valid and invalid priority, queue mapping and overflow beyond 16-bit, ptype host/otherhost and invalid ptype, controls `pipe`, `reclassify`, `pass`, `drop`, `jump`, and `continue`, cookie, list, max and oversized index, delete, flush, invalid goto-chain preservation, and 32-action batch add/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbedit.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbmod.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbmod.json

## Purpose

`skbmod.json` defines 18 tc-testing cases for the `skbmod` action. It validates Ethernet header modification syntax for destination MAC, source MAC, EtherType, MAC swapping, ECN marking, controls, cookies, listing/getting, deletion, flushing, and invalid parser paths.

## Important APIs, Types, and Schema

The file uses the standard tc-testing schema with `nsPlugin`. It exercises `$TC actions add|replace|del|flush|ls|get action skbmod`. The command grammar under test includes `set dmac <mac>`, `set smac <mac>`, `set etype <u16>`, `swap mac`, `ecn`, controls `pipe`, `reclassify`, `drop`, `continue`, and `pass`, plus `index` and `cookie`.

## Control Flow

Each case starts with clean or preloaded `skbmod` state, executes a command, then verifies with list or get. Positive tests assert normalized MAC casing, EtherType rendering, control action, index/ref, cookie, and list counts. Negative tests expect `255` and assert absence for invalid MAC length and out-of-range EtherType. Delete and flush tests assert removal of persisted actions.

## State and Persistence Behavior

State is the skbmod action entry in the kernel action table. Most adds use default index behavior unless an explicit index is supplied. Replacement with invalid goto-chain control starts from an existing pass action at index 90 and verifies the invalid replacement does not overwrite it. Delete removes a specific indexed action; flush removes all skbmod actions.

## Dependencies and Integration Points

The tests require `$TC`, `nsPlugin`, and skbmod support in kernel/iproute2. They validate action management and rendering only; no packet is sent to prove header rewriting or ECN modification on the datapath.

## Risks

Assertions are sensitive to output normalization, especially uppercase EtherType rendering (`0xFEFE`, `0xBEEF`) and lowercase MAC rendering for uppercase input. The suite does not test index bounds or batch behavior for skbmod, and it does not verify real packet mutation.

## Test Signals

Coverage includes setting destination and source MAC addresses, rejecting invalid MAC, setting valid EtherType, rejecting oversized EtherType, swapping MACs, all common controls, cookie rendering, listing five preloaded actions, getting a specific action by index, deleting an indexed action, flushing all actions, invalid goto-chain replace preservation, and adding the ECN modifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbmod.json -->

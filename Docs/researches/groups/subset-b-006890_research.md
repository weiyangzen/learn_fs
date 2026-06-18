# subset-b-006890 Research

Grouped source research for Linux kernel selftest traffic-control qdisc cases, the `tdc` traffic-control test harness, TDX guest selftests, Intel thermal notification selftests, time namespace selftests, and timers selftests. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/htb.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/htb.json

## Purpose
Defines 12 `tdc` JSON test cases for the `htb` qdisc and HTB classes. The file exercises root HTB creation, `default`, `r2q`, `direct_qlen`, class rate/burst/mpu/prio/ceil/cburst/mtu/quantum options, and deletion by handle.

## Important APIs, Types, and Functions
This is data consumed by `tdc.py`, not executable code. Important schema fields are `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern` or `matchJSON`, and `teardown`. The commands target `$TC qdisc` and `$TC class` operations against namespace-managed `$DEV0`.

## Control Flow
`tdc.py` loads the array, substitutes `NAMES` variables, lets `nsPlugin` create the test namespace/veth topology, runs setup, executes the HTB command under test, verifies `tc` output, and tears down qdiscs/classes. Class tests first install the parent HTB qdisc before adding class `1:1`.

## State and Persistence Behavior
State is transient kernel traffic-control state attached to the test device. The JSON persists no runtime state; successful runs rely on teardown deleting the qdisc so later tests do not inherit handles, defaults, or classes.

## Dependencies and Integration Points
Depends on the `sch_htb` kernel module, `/sbin/tc`, namespace support through `nsPlugin`, and TDC variable substitution. It integrates with HTB parser/kernel validation through `tc qdisc add`, `tc class add`, `tc qdisc show`, and `tc class show`.

## Risks and Edge Cases
The tests are sensitive to exact iproute2 formatting and HTB unit normalization. Some option combinations such as `quantum`, `mtu`, or `mpu` are accepted but may display rounded values. Missing `sch_htb` or namespace setup turns parser coverage into environment failure.

## Test Signals
Good signals are expected zero exit codes for valid add/delete cases, matching class/qdisc show output for configured options, and clean deletion by handle without residual HTB state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/htb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ingress.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ingress.json

## Purpose
Defines six TDC cases for the special `ingress` qdisc. It covers adding ingress, rejecting unsupported arguments, duplicate add behavior, deleting missing ingress instances, double deletion, and class display.

## Important APIs, Types, and Functions
The file uses the standard TDC JSON case schema. `cmdUnderTest` entries call `$TC qdisc add|del|show dev $DEV0 ingress` and related class show commands; expected failures are represented by nonzero `expExitCode` and matching error text.

## Control Flow
The harness prepares a network namespace device, runs each ingress operation, checks exit status, then verifies via `tc qdisc show` or class output. Negative cases intentionally execute commands on absent or duplicate ingress state to confirm kernel/iproute2 validation.

## State and Persistence Behavior
Ingress attaches to a fixed ingress hook on the device and cannot be stacked like ordinary classful qdiscs. Teardown removes it when created; missing-qdisc cases leave no intended state.

## Dependencies and Integration Points
Depends on kernel ingress qdisc support and the TDC namespace plugin. Integration points are the `tc` ingress parser, qdisc creation path, duplicate detector, delete path, and class dump path.

## Risks and Edge Cases
Because ingress is a singleton per device, ordering and teardown are critical. Error strings can vary between iproute2/kernel versions, and class show behavior for ingress may be easy to regress because it is not a normal classful scheduler.

## Test Signals
Expected signals are successful ingress creation, duplicate/missing deletes returning the configured failure code, unsupported argument rejection, and a non-empty class show for ingress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ingress.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mq.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mq.json

## Purpose
Defines eight TDC cases for the `mq` qdisc on multi-queue and single-queue devices. It verifies valid creation on four-queue and 256-queue netdevsim devices, duplicate add rejection, missing/double delete behavior, single-queue rejection, class dump, and invalid parent replacement.

## Important APIs, Types, and Functions
The JSON relies on `nsPlugin` and netdevsim-related setup commands to create devices with specific queue counts. Commands exercise `$TC qdisc add dev ... root mq`, delete, replace, and class show operations.

## Control Flow
Setup creates a device with the required queue topology, the harness installs or manipulates `mq`, then verification reads `tc` qdisc/class output. Negative tests deliberately run operations on absent qdiscs, single-queue devices, or invalid parent handles.

## State and Persistence Behavior
Runtime state is the kernel qdisc tree and per-TX-queue child qdisc structure. JSON state is static. Teardown removes qdiscs and netdevsim devices to avoid queue topology leakage into later tests.

## Dependencies and Integration Points
Depends on netdevsim, multiqueue netdevice support, `sch_mq`, `tc`, and namespace management. It integrates with qdisc grafting and class enumeration for hardware transmit queues.

## Risks and Edge Cases
Environment support is the main risk: netdevsim creation and queue counts must work. Output can vary with default child qdisc selection. The 256-queue case is useful for scaling but may expose kernel or userspace formatting limits.

## Test Signals
Signals include successful root `mq` creation on multiqueue devices, correct class list generation, explicit rejection on single-queue devices, and failure for duplicate or invalid-parent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mqprio.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mqprio.json

## Purpose
Defines five TDC tests for `mqprio`, focused on multiqueue creation, deletion edge cases, single-queue rejection, and class display.

## Important APIs, Types, and Functions
The cases use the TDC JSON schema and call `$TC qdisc add ... mqprio`, delete, and class show commands. Setup provisions multiqueue or single-queue devices through namespace/netdev helpers.

## Control Flow
For valid cases, setup creates an eight-queue device, `mqprio` is attached as root, and class output is checked. Invalid cases attempt deletion before creation, double deletion, or attachment to a single-queue device.

## State and Persistence Behavior
The kernel owns the qdisc and traffic class mapping while the test runs. Teardown must remove qdisc/device state because mqprio maps traffic classes to hardware queues.

## Dependencies and Integration Points
Depends on `sch_mqprio`, multiqueue netdevices, netdevsim or equivalent test setup, `tc`, and `nsPlugin`. It reaches both the qdisc parser and class dump paths.

## Risks and Edge Cases
Queue count and hardware-offload defaults can differ across environments. Class output can be sensitive to default mapping chosen by iproute2/kernel when optional parameters are omitted.

## Test Signals
Successful add on eight queues, expected failure on single queue or missing delete, and stable class dump output are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mqprio.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/multiq.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/multiq.json

## Purpose
Defines five TDC cases for the legacy `multiq` qdisc. It checks creation on an eight-queue device, class listing, missing/double delete behavior, and rejection on single-queue devices.

## Important APIs, Types, and Functions
The JSON uses `cmdUnderTest` entries for `$TC qdisc add ... multiq`, `$TC class show`, and delete operations. `plugins.requires` ties the tests to namespace/device setup.

## Control Flow
TDC creates the requested device, applies `multiq`, verifies the class view, and cleans up. Negative tests run operations when no qdisc exists or when the device does not expose multiple queues.

## State and Persistence Behavior
Runtime state is the classful `multiq` qdisc bound to hardware queues. No test data is persisted beyond the JSON file; cleanup should remove qdisc and device resources.

## Dependencies and Integration Points
Depends on `sch_multiq`, multiqueue device support, `tc`, and TDC plugins. It integrates with the qdisc creation, delete, and class enumeration paths.

## Risks and Edge Cases
Single-queue behavior and default child qdisc formatting can differ across kernel/iproute2 versions. Failing teardown can contaminate later qdisc tests on the same test device.

## Test Signals
Expected pass signals are successful attach and class list on a multiqueue device plus expected nonzero exits for absent qdisc and single-queue cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/multiq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/netem.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/netem.json

## Purpose
Defines 20 TDC cases for the `netem` qdisc. It covers default creation, `limit`, delay distributions, corruption, duplication, loss modes, reorder, rate and slot options, change/replace/delete paths, class display, and duplicate-netem restrictions in qdisc trees.

## Important APIs, Types, and Functions
The file drives `tc qdisc add|change|replace|del|show` with `netem` options and uses `matchPattern`/`matchJSON` verification. Several cases build nested qdisc trees to validate kernel restrictions on duplicate netem instances.

## Control Flow
Each case creates the namespace device, optionally prepares parent/child qdiscs, runs the netem command, verifies `tc` output or expected error, and deletes the qdisc tree. Tree-duplication cases test both root and non-root paths and across branches.

## State and Persistence Behavior
The kernel maintains delay/loss/corruption/reorder/rate/slot parameters while the qdisc exists. The JSON is static, and teardown must clear nested trees so later tests do not see existing handles.

## Dependencies and Integration Points
Depends on `sch_netem`, qdisc class/graft support, `tc`, and namespace plugin support. It integrates deeply with netem option parsing and kernel duplicate detection.

## Risks and Edge Cases
Netem output includes normalized units and optional fields, making regex matching fragile across versions. Distribution support may require installed distribution files or kernel support. Duplicate restriction tests are sensitive to qdisc tree setup correctness.

## Test Signals
Strong signals include correct display of configured impairment parameters, successful change/replace behavior, rejection of illegal duplicate netem placement, and clean deletion by handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/netem.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pfifo_fast.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pfifo_fast.json

## Purpose
Defines five TDC tests for `pfifo_fast`, covering default creation, statistics dump, replacement with a different handle, valid deletion, and invalid handle deletion.

## Important APIs, Types, and Functions
The data uses `tc qdisc add|replace|del|show` against `pfifo_fast`. Verification checks qdisc display and stats output through TDC match fields.

## Control Flow
TDC creates the namespace device, applies or manipulates `pfifo_fast`, runs a show/stats command for verification, then removes the qdisc where applicable. Negative deletion validates handle lookup behavior.

## State and Persistence Behavior
The only runtime state is the qdisc instance and packet counters/statistics. Teardown removes the instance so a default qdisc from the kernel does not confuse later explicit tests.

## Dependencies and Integration Points
Depends on `pfifo_fast` availability in the kernel and `tc` display paths. It integrates with simple qdisc add/replace/delete and stats dump behavior.

## Risks and Edge Cases
`pfifo_fast` may be built in, deprecated, or affected by system default qdisc configuration. Stats output can be absent or formatted differently if the qdisc is not active.

## Test Signals
Signals are visible `pfifo_fast` qdisc output, stats dump success, replacement handle change, successful valid delete, and expected invalid-handle failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pfifo_fast.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pie.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pie.json

## Purpose
Defines a single TDC case for `pie`, specifically testing qdisc limit trimming behavior.

## Important APIs, Types, and Functions
The JSON uses the standard TDC fields to create/configure a PIE qdisc and verify output. The command path targets `tc qdisc` parser support for `pie` and its `limit` handling.

## Control Flow
The harness prepares the device, runs the PIE command under test, validates the resulting qdisc output or error expectation, and deletes qdisc state during teardown.

## State and Persistence Behavior
PIE maintains active queue management parameters and queue state only while attached to the device. The test persists no data outside the static JSON definition.

## Dependencies and Integration Points
Depends on `sch_pie`, `tc`, and namespace setup. It integrates with the PIE qdisc option parser and display code.

## Risks and Edge Cases
The file provides narrow coverage. Kernel or iproute2 changes around minimum/maximum limit trimming can alter output and expected behavior without affecting basic PIE creation.

## Test Signals
The primary signal is the expected limit value after trimming, as reported by `tc qdisc show`, with clean teardown afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pie.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/plug.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/plug.json

## Purpose
Defines eight TDC cases for the `plug` qdisc. It exercises default creation, `block`, `release`, `release_indefinite`, `limit`, valid deletion, replace, and change with limit.

## Important APIs, Types, and Functions
The JSON drives `tc qdisc add|replace|change|del|show ... plug` and checks command exit status plus output matches.

## Control Flow
TDC attaches `plug` with different control options, verifies the qdisc state, and removes it. Change/replace cases install an initial qdisc before mutating its limit.

## State and Persistence Behavior
Plug qdisc state controls whether queued packets are blocked or released and stores a limit. All state is kernel-resident and should be removed by teardown.

## Dependencies and Integration Points
Depends on `sch_plug`, `tc`, and the namespace plugin. Integration points are the plug parser, qdisc change/replace operations, and output formatter.

## Risks and Edge Cases
Block/release semantics are timing-sensitive if traffic is later added to the tests. As written, the tests mostly validate parser/state display and may not catch packet-flow regressions.

## Test Signals
Successful add/change/replace/delete operations and visible `limit`, `block`, or release-related output are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/plug.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/prio.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/prio.json

## Purpose
Defines 15 TDC cases for the classful `prio` qdisc. It covers normal egress add, maximum and invalid handles, unsupported arguments, band counts, priomap validation, replacement, duplicate add, nonexistent/double delete, invalid handle formats, and class display.

## Important APIs, Types, and Functions
The cases use `tc qdisc add|replace|del|show` and `tc class show` for `prio`. Validation is expressed through expected exit codes and `matchPattern`/`matchJSON` data.

## Control Flow
For each case, TDC prepares a device, applies the `prio` operation, verifies output or expected failure, then deletes the qdisc. Priomap tests intentionally vary array length and values to exercise parser and kernel constraints.

## State and Persistence Behavior
The qdisc stores band count and priority-to-band mapping while attached. The JSON file itself is immutable test input. Teardown must remove handles so duplicate-add tests remain isolated.

## Dependencies and Integration Points
Depends on `sch_prio`, `tc`, and namespace setup. It integrates with classful qdisc creation, parser bounds checking, and class dump code.

## Risks and Edge Cases
Priomap constraints are tightly coupled to `TC_PRIO_MAX` and `TCQ_PRIO_BANDS`; kernel constant changes require test updates. Exact error text and handle formatting can vary by iproute2 version.

## Test Signals
Signals include valid prio creation, correct class output, successful replacement with eight bands, and expected rejection of invalid bands, priomap, duplicate, and handle cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/prio.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/qfq.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/qfq.json

## Purpose
Defines 12 TDC cases for `qfq` and QFQ classes. It tests default qdisc creation, class `weight` and `maxpkt`, boundary values, multiple classes, delete, class show, big/small MTU behavior, and `stab` overhead greater than max packet length.

## Important APIs, Types, and Functions
The data drives `tc qdisc add ... qfq`, `tc class add/show`, and related setup commands. Cases use standard TDC JSON fields to encode expected success and failure.

## Control Flow
The harness installs QFQ, adds one or more classes with supplied parameters, verifies class/qdisc output or failure, then deletes by handle. MTU and `stab` cases prepare device/qdisc settings that affect QFQ admission checks.

## State and Persistence Behavior
QFQ class state, weights, packet-size bounds, and qdisc handles live in the kernel only for the test. Teardown removes the qdisc hierarchy.

## Dependencies and Integration Points
Depends on `sch_qfq`, `tc`, namespace setup, and link/MTU control. It integrates with classful qdisc operations and QFQ parameter validation.

## Risks and Edge Cases
Boundary tests are sensitive to kernel constants and device MTU. `stab` overhead interactions can produce failures that look environmental if link parameters are not reset.

## Test Signals
Expected signals include correct class output for weights/maxpkt, acceptance/rejection at documented bounds, and failure when overhead exceeds feasible packet length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/qfq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/red.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/red.json

## Purpose
Defines nine TDC cases for `red`. It covers creation with no flags, `adaptive`, `ecn`, combinations with `harddrop` and `nodrop`, rejection of invalid `nodrop` alone, and class display.

## Important APIs, Types, and Functions
The cases exercise `tc qdisc add ... red` option parsing for RED thresholds/probability/flags and `tc class show` for the class view.

## Control Flow
TDC attaches RED with each flag combination, verifies the resulting display or expected parser failure, then tears down the qdisc. The invalid case expects nonzero exit rather than output match success.

## State and Persistence Behavior
RED stores queue thresholds, probability, and ECN/drop policy in kernel qdisc state. No persistent state exists outside the JSON.

## Dependencies and Integration Points
Depends on `sch_red`, `tc`, and namespace setup. It integrates with RED parser/display and class dump paths.

## Risks and Edge Cases
RED output may normalize thresholds and probabilities. Flag compatibility is semantic; parser changes around `nodrop` and `ecn` combinations can change expected failures.

## Test Signals
Signals include correct flag display for valid combinations, failure for `nodrop` without required context, and working class show.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/red.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfb.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfb.json

## Purpose
Defines 12 TDC cases for `sfb`, covering default creation and options `rehash`, `db`, `limit`, `max`, `target`, `increment`, `decrement`, `penalty_rate`, `penalty_burst`, change with `rehash`, and class display.

## Important APIs, Types, and Functions
The JSON drives `tc qdisc add|change|show ... sfb` and class show operations. It validates option parsing and output for stochastic fair blue parameters.

## Control Flow
For each parameter, the harness attaches SFB, checks qdisc output, and deletes it. The change case first creates SFB and then mutates rehash timing.

## State and Persistence Behavior
SFB keeps queue, bin, rehash, and penalty settings in kernel memory while attached. Test state is reset through teardown.

## Dependencies and Integration Points
Depends on `sch_sfb`, `tc`, and namespace support. It integrates with qdisc add/change/display and class dump paths.

## Risks and Edge Cases
Time/rate units may be printed in normalized forms. Because the tests do not inject traffic, they validate configuration more than queue behavior or flow accounting.

## Test Signals
Expected signals are successful parsing and display of each option, working `change`, and class show availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfq.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfq.json

## Purpose
Defines 15 TDC cases for `sfq`. It covers default creation, `limit`, `perturb`, `quantum`, `divisor`, `flows`, `depth`, `headdrop`, `redflowlimit`, class show, and rejection of invalid or derived limit/perturb values.

## Important APIs, Types, and Functions
The file uses TDC JSON to run `tc qdisc add ... sfq`, `tc class show`, and negative parser/kernel validation cases. Expected outcomes are encoded through exit code and match fields.

## Control Flow
Each case creates an SFQ qdisc with one parameter variation or invalid combination, verifies output or failure, and tears it down. Derived-limit cases combine `limit`, `depth`, `flows`, or `divisor` to trigger kernel validation.

## State and Persistence Behavior
SFQ stores hashing, flow, depth, perturb timer, and optional RED-flow state in the kernel. No data persists beyond qdisc lifetime.

## Dependencies and Integration Points
Depends on `sch_sfq`, `tc`, namespace support, and class display. It integrates with SFQ option parsing and validation logic.

## Risks and Edge Cases
Boundary cases are coupled to SFQ internal constraints. Perturb timer validation depends on signed/integer parsing and may produce version-specific error text.

## Test Signals
Signals include successful option display, class show success, and expected rejections for limit of one, derived limit of one, negative perturb, and too-large perturb.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfq.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/skbprio.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/skbprio.json

## Purpose
Defines four TDC cases for `skbprio`: default creation, creation with `limit`, change with `limit`, and class display.

## Important APIs, Types, and Functions
The JSON invokes `tc qdisc add|change|show ... skbprio` and `tc class show`, with expected matches on displayed parameters.

## Control Flow
TDC attaches `skbprio`, checks default or configured limit output, mutates the limit for the change case, and cleans up.

## State and Persistence Behavior
The qdisc maintains packet priority queues and a queue limit in kernel state. The JSON persists only static test definitions.

## Dependencies and Integration Points
Depends on `sch_skbprio`, `tc`, and namespace setup. It integrates with qdisc add/change and class show.

## Risks and Edge Cases
Coverage is configuration-only and does not validate actual priority dequeue behavior. Output formatting for defaults can vary with kernel/iproute2 versions.

## Test Signals
Signals are successful add/change operations, expected `limit` display, and working class show.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/skbprio.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/taprio.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/taprio.json

## Purpose
Defines 14 TDC cases for `taprio`. It tests multiqueue creation, multiple schedule entries, `txtime-delay`, valid delete, class show, single-queue rejection, too-short intervals/cycle times, invalid cycle time, child-qdisc grafting restrictions, CBS graft behavior under software/offloaded taprio, and class dump after explicit child delete.

## Important APIs, Types, and Functions
The cases drive `tc qdisc add|del|show` and child qdisc graft operations for time-aware priority scheduling. Options include traffic-class maps, queue maps, `sched-entry`, cycle timing, offload flags, and `txtime-delay`.

## Control Flow
Setup creates single- or multiqueue devices. Valid cases add taprio and verify display/class output. Negative cases attempt invalid timing or forbidden child placement. Graft cases add `cbs` beneath taprio classes and verify dump behavior before cleanup.

## State and Persistence Behavior
Taprio state includes gate schedules, traffic-class queue mapping, cycle timing, offload mode, and child qdisc references. All state is kernel-resident and must be deleted to restore the test device.

## Dependencies and Integration Points
Depends on `sch_taprio`, `sch_cbs`, multiqueue devices, optional offload-capable/netdevsim behavior, `tc`, and namespace setup. It integrates with qdisc timing validation, class grafting, and offload/software paths.

## Risks and Edge Cases
Timing thresholds and offload support are hardware/kernel dependent. Child qdisc graft behavior is subtle because offloaded and software taprio have different constraints. Exact class dump output can change with default child qdisc handling.

## Test Signals
Signals include valid taprio display for multiqueue schedules, expected rejection of invalid timing/single-queue cases, correct child graft accept/reject behavior, and stable class dumps after child deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/taprio.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/tbf.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/tbf.json

## Purpose
Defines nine TDC cases for `tbf`, covering default creation, `mtu`, `peakrate`, `latency`, `overhead`, `linklayer`, replace with `mtu`, change with latency time, and class show.

## Important APIs, Types, and Functions
The JSON invokes `tc qdisc add|replace|change|show ... tbf` and `tc class show`. It validates token bucket parser/display behavior for rate, burst, latency, and link-layer accounting options.

## Control Flow
The harness attaches TBF with one option variation, verifies qdisc/class output, and tears down. Replace/change cases start from an existing TBF qdisc.

## State and Persistence Behavior
TBF keeps token bucket rates, burst/latency/MTU, peakrate, and link-layer adjustment state in kernel memory while attached. The JSON has no runtime persistence.

## Dependencies and Integration Points
Depends on `sch_tbf`, `tc`, and namespace setup. It integrates with rate-table calculations and qdisc/class display.

## Risks and Edge Cases
Rate and time values are often normalized or rounded, so output matching can be brittle. Link-layer and overhead behavior depends on stable iproute2/kernel accounting semantics.

## Test Signals
Signals are successful add/replace/change operations, expected display of configured parameters, class show success, and clean deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/tbf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/teql.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/teql.json

## Purpose
Defines five TDC cases for `teql`. It covers default creation, use with multiple devices, valid deletion, stats display, and rejection when attempting to add TEQL as a child qdisc.

## Important APIs, Types, and Functions
The JSON drives `tc qdisc add|del|show ... teql` and stats commands. It uses namespace setup to provide one or more test devices.

## Control Flow
TDC prepares devices, attaches TEQL at root, verifies normal or stats output, and deletes state. The child-qdisc case attempts an invalid placement and expects failure.

## State and Persistence Behavior
TEQL creates kernel qdisc state and may create/coordinate with a TEQL virtual device depending on kernel support. Teardown must remove qdisc attachments from all participating devices.

## Dependencies and Integration Points
Depends on `sch_teql`, `tc`, namespace setup, and multiple devices for aggregation coverage. It integrates with qdisc creation, stats display, and parent/child placement validation.

## Risks and Edge Cases
TEQL is uncommon and may not be enabled in all kernels. Multi-device tests are sensitive to setup cleanup, and virtual-device naming can affect matching.

## Test Signals
Signals include successful root TEQL creation on one and multiple devices, stats output availability, valid deletion, and expected failure as a child qdisc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/teql.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.py

## Purpose
Implements the main Linux traffic-control unit test driver. It discovers JSON test cases, loads required plugins, substitutes configured command names, executes setup/command/verify/teardown stages, checks results with regex or JSON matching, and emits TAP or xUnit output.

## Important APIs, Types, and Functions
Important types are `PluginDependencyException`, `PluginMgrTestFail`, and `PluginMgr`. Core functions include `replace_keywords`, `exec_cmd`, `prepare_env`, `verify_by_json`, `find_in_json*`, `run_one_test`, `prepare_run`, `test_runner`, `mp_bins`, `test_runner_mp`, `test_runner_serial`, `load_from_file`, `set_args`, `check_default_settings`, `generate_case_ids`, `filter_tests_by_id`, `filter_tests_by_category`, `get_test_cases`, `set_operation_mode`, and `main`.

## Control Flow
`main()` enforces Python 3.8, raises `RLIMIT_NOFILE`, builds the parser, loads plugins, parses arguments, checks configured tool paths, and calls `set_operation_mode()`. Test discovery loads JSON from `tc-tests` or user-provided files/directories, filters by category or ID, generates IDs if requested, then executes serially or in batches. `run_one_test()` mutates per-test `NAMES`, calls plugin hooks, runs setup, command under test, verify command, and teardown, then restores names. Multiprocess mode splits namespace-safe tests from serial tests and caps workers at four.

## State and Persistence Behavior
Global `NAMES` and `ENVIR` come from `tdc_config.py` plus local overrides. Per-test state is temporarily written into `NAMES` (`TESTID`, randomized namespace/device suffixes). Result state accumulates in `TestSuiteReport` and may be persisted to `test-results.tap`, `test-results.xml`, or `--outfile`. `generate_case_ids()` edits JSON files when blank IDs exist and `--id` is requested.

## Dependencies and Integration Points
Depends on `TdcPlugin`, `TdcResults`, `tdc_config`, `tdc_helper`, plugin directories `plugin-lib` and `plugin-lib-custom`, Python `subprocess`, `multiprocessing.Pool`, and external tools such as `tc`, `ip`, and `ethtool`. It integrates with kernel selftest result conventions through exit codes 0/1/4 and TAP/xUnit formatters.

## Risks and Edge Cases
Commands run with `shell=True`, so test JSON must be trusted. Plugin discovery has a suspicious `plugin_instances` initialization path in `__init__` that treats a list-like object as a dict, while normal required-plugin loading appends tuples. JSON matching has typo paths (`outputJSON`/`matchJSON` and `rest`) that can raise if type mismatches hit those branches. Timeout handling sets return code 255 but does not kill the child explicitly. Multiprocess execution shares plugin manager and args through globals and relies on pickling result data only.

## Test Signals
Useful signals are duplicate ID detection, category and ID filtering, plugin dependency loading, namespace tests in serial and multiprocess mode, JSON and regex verification failures, setup/teardown failure handling, output file ownership under sudo, and proper skip behavior for device-dependent flower tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.sh

## Purpose
Shell wrapper that attempts to load traffic-control action, classifier, ematch, and qdisc modules before running `./tdc.py` in parallel with `-J$(nproc)`.

## Important APIs, Types, and Functions
Defines `try_modprobe()`, which checks `modprobe -q -R` for module availability before calling `modprobe`. The module list includes netdevsim, many `act_*`, `cls_*`, `em_*`, and `sch_*` modules such as `sch_htb`, `sch_teql`, and `sch_dualpi2`.

## Control Flow
The script sequentially calls `try_modprobe` for each module. Missing modules print a skip-style message but do not abort. After loading attempts, it executes `tdc.py` with worker count equal to `nproc`.

## State and Persistence Behavior
It changes kernel module load state. It does not persist files directly, but `tdc.py` may create result outputs and manipulate namespaces/devices.

## Dependencies and Integration Points
Depends on `/bin/sh`, `modprobe`, module alias resolution, `nproc`, and the local `tdc.py`. It integrates with kselftest execution as the convenient top-level TDC runner.

## Risks and Edge Cases
The script does not stop if a required module is missing; failures surface later as individual TDC failures. It assumes it runs from the tc-testing directory. Loading many modules can require privileges and may be inappropriate on minimal systems.

## Test Signals
Signals include module load messages, successful startup of `tdc.py`, and TDC test output showing which cases passed or failed after module preparation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_batch.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_batch.py

## Purpose
Generates a `tc -batch` style file containing many flower filter commands for performance and scaling tests.

## Important APIs, Types, and Functions
Arguments include `device`, output `file`, `--number`, `--handle_start`, `--skip_sw`, `--share_action`, `--prio`, `--operation`, and `--mac_prefix`. Formatter functions are `format_add_filter`, `format_rep_filter`, and `format_del_filter`.

## Control Flow
After parsing arguments, it selects skip mode (`skip_hw` by default or `skip_sw`), action sharing, priority behavior, and operation formatter. It iterates three bytes of source/destination MAC suffix space, writes one command per handle, and exits after the requested line count.

## State and Persistence Behavior
The script writes the requested batch file and no other persistent state. Handles and MAC addresses are deterministic from `handle_start`, `number`, and `mac_prefix`.

## Dependencies and Integration Points
Depends on Python argparse and the file system. Generated commands target `tc filter add|replace|del ... flower ... action drop` and integrate with TDC batch/offload tests.

## Risks and Edge Cases
The output file is opened without context-manager cleanup except explicit close on normal completion. `--prio` caps `number` to `0x4000`; without it, very large counts can generate huge files. Delete formatter ignores MAC/action parameters, which is intentional but easy to misread.

## Test Signals
Signals are deterministic line count, correct handle range, expected skip mode, unique MAC generation, and valid `tc` batch syntax for add/replace/delete operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_batch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config.py

## Purpose
Provides default TDC command substitution values and environment settings, with optional local override support.

## Important APIs, Types, and Functions
Exports `NAMES`, containing paths and symbolic names such as `TC`, `IP`, `DEV0`, `DEV1`, `DEV2`, `DUMMY`, `ETHTOOL`, `ETH`, `BATCH_FILE`, `BATCH_DIR`, `TIMEOUT`, `NS`, and `EBPFDIR`. Exports `ENVIR`, initially empty unless overridden. It imports `tdc_config_local` if present and merges `EXTRA_NAMES` if defined.

## Control Flow
Import-time code defines defaults, tries to import local overrides, then updates `NAMES` with `EXTRA_NAMES` when available. `tdc.py` imports these globals and later mutates selected names per test.

## State and Persistence Behavior
State is in-process Python module state. There is no file write. Local overrides are intentionally outside this file in `tdc_config_local.py`.

## Dependencies and Integration Points
Integrated directly by `tdc.py`, all JSON command substitutions, and plugin argument checks. It assumes default tool paths such as `/sbin/tc`, `/sbin/ip`, and `/usr/sbin/ethtool`.

## Risks and Edge Cases
Default `ENVIR = {}` means subprocesses may run with a stripped environment unless a local config copies `os.environ`. Hard-coded tool paths can fail on distributions where tools live elsewhere. Missing local overrides are silently ignored.

## Test Signals
Signals include `tdc.py` path validation for `TC` and optional `ETHTOOL`, successful variable substitution in commands, and local override behavior through `EXTRA_NAMES` and `ENVIR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config_local_template.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config_local_template.py

## Purpose
Template for user- or plugin-specific TDC local configuration. It demonstrates how to preserve the process environment and add custom substitution names or environment variables without editing `tdc_config.py`.

## Important APIs, Types, and Functions
Defines `ENVIR = os.environ.copy()`, reads `LD_LIBRARY_PATH` and `OTHER_LIB`, populates `EXTRA_NAMES` with `SOME_BIN`, and adds Valgrind-related entries to `ENVIR`.

## Control Flow
If copied to `tdc_config_local.py`, it runs at import time from `tdc_config.py`. The base config then merges `EXTRA_NAMES` into `NAMES`.

## State and Persistence Behavior
No runtime persistence. The template itself is a static example; copied local configs can affect every TDC subprocess environment.

## Dependencies and Integration Points
Depends on Python `os`. Integrates with `tdc_config.py` import hooks and all TDC subprocess execution through `ENVIR`.

## Risks and Edge Cases
As a template, it includes example paths that may not exist. Copying it unchanged may add unused Valgrind variables or `SOME_BIN` with an empty base path.

## Test Signals
Signals are successful import as `tdc_config_local`, visible extra substitutions in `args.NAMES`, and subprocess environment values present during command execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config_local_template.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_helper.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_helper.py

## Purpose
Provides small list, category, and pretty-print helpers used by `tdc.py` when discovering and displaying test cases.

## Important APIs, Types, and Functions
Functions are `get_categorized_testlist`, `get_unique_item`, `get_test_categories`, `list_test_cases`, `list_categories`, `print_list`, `print_sll`, and `print_test_case`.

## Control Flow
Helpers take loaded JSON test dictionaries and compute category groupings, ordered unique lists, or user-facing display text. `tdc.py` calls these during `--list`, `--show`, category discovery, and ID generation flows.

## State and Persistence Behavior
All functions are stateless and return derived values or print to stdout. No files or global state are modified.

## Dependencies and Integration Points
Depends only on Python built-ins. It integrates with TDC CLI selection and display paths.

## Risks and Edge Cases
`get_unique_item` returns the original list unchanged when length is one, but a new list for longer inputs; callers should not depend on object identity. `print_test_case` treats lists specially but prints other nested structures with `str()`, which is adequate for display but not stable serialization.

## Test Signals
Signals include correct ordered category discovery, duplicate-free category lists, readable `--list` output, and full case details in `--show`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_helper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_multibatch.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_multibatch.py

## Purpose
Thin wrapper that generates multiple flower filter batch files by repeatedly invoking `tdc_batch.py`.

## Important APIs, Types, and Functions
Arguments are `device`, output `dir`, `num_filters`, `num_files`, `operation`, `--file_prefix`, `--duplicate_handles`, `--handle_start`, and `--mac_prefix`.

## Control Flow
After parsing arguments, it builds output filenames from prefix, operation, and index. It calls `./tdc_batch.py` via `os.system()` for each file, passing filter count, handle start, operation, MAC prefix, device, and output path. Unless `--duplicate_handles` is set, it advances the handle start by `num_filters` per file.

## State and Persistence Behavior
Persists generated batch files in the requested directory. Handle and MAC-prefix state are local loop variables.

## Dependencies and Integration Points
Depends on Python `argparse`, `os.system`, the current working directory containing `tdc_batch.py`, and a pre-existing output directory. It supports TDC batch-scaling tests that need several batch files.

## Risks and Edge Cases
Uses shell command construction without quoting, so paths/devices should be trusted simple strings. It does not check `os.system()` return status. Output directory creation is left to the caller.

## Test Signals
Signals include the expected number of files, expected line count per file, non-overlapping or duplicated handle ranges depending on the flag, and distinct MAC prefixes per file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_multibatch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/Makefile

## Purpose
Builds the TDX guest kselftest program.

## Important APIs, Types, and Functions
Sets `CFLAGS += -O3 -Wl,-no-as-needed -Wall $(KHDR_INCLUDES) -static`, defines `TEST_GEN_PROGS := tdx_guest_test`, and includes `../lib.mk`.

## Control Flow
Kselftest make infrastructure reads `TEST_GEN_PROGS`, compiles `tdx_guest_test.c` with kernel header includes, and emits the generated test binary.

## State and Persistence Behavior
Build output is the `tdx_guest_test` executable and normal kselftest build artifacts. The Makefile itself owns no runtime state.

## Dependencies and Integration Points
Depends on kernel UAPI headers, static linking support, and kselftest `lib.mk`. Integrates with `make -C tools/testing/selftests/tdx`.

## Risks and Edge Cases
Static linking can fail on environments without static libc. The test requires TDX guest driver support at runtime, so build success alone is not a functional signal.

## Test Signals
Signals are successful compilation with warnings enabled and generation of the `tdx_guest_test` binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/config

## Purpose
Kselftest configuration fragment declaring that the TDX guest driver is required.

## Important APIs, Types, and Functions
Contains `CONFIG_TDX_GUEST_DRIVER=y`.

## Control Flow
There is no executable flow. Kselftest/config tooling can use the fragment to identify kernel config requirements.

## State and Persistence Behavior
Static build/runtime requirement only; no state is modified.

## Dependencies and Integration Points
Integrates with kernel selftest config aggregation and the TDX guest test that opens `/dev/tdx_guest`.

## Risks and Edge Cases
The option being present is necessary but not sufficient; the system must also be running as a TDX guest with the device node available.

## Test Signals
Signal is kernel config coverage for `CONFIG_TDX_GUEST_DRIVER=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/tdx_guest_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/tdx_guest_test.c

## Purpose
Kselftest harness program that verifies TDX guest report generation through `/dev/tdx_guest`. It requests a TDREPORT and checks that the returned report embeds the caller-provided report data.

## Important APIs, Types, and Functions
Defines TDX report layout structs `tdreport_type`, `reportmac`, `td_info`, and `tdreport` matching the TDX specification. Uses `struct tdx_report_req`, `TDX_REPORTDATA_LEN`, and `TDX_CMD_GET_REPORT0` from `<linux/tdx-guest.h>`. Helper `print_array_hex()` dumps buffers when `DEBUG` is enabled. The test case is `TEST(verify_report)`.

## Control Flow
The test opens `/dev/tdx_guest` read/write synchronized, fills `req.reportdata` with a byte pattern, calls `ioctl(TDX_CMD_GET_REPORT0, &req)`, optionally dumps buffers, casts `req.tdreport` to `struct tdreport`, compares the `reportmac.reportdata` field with the original input, and closes the device.

## State and Persistence Behavior
No file persistence. The driver returns an attestation report for the running TDX guest. All buffers are stack-local to the test.

## Dependencies and Integration Points
Depends on the TDX guest driver, `/dev/tdx_guest`, TDX-capable guest environment, Linux UAPI header `tdx-guest.h`, and `kselftest_harness.h`.

## Risks and Edge Cases
The test is environment-specific and will fail rather than skip if the device cannot be opened unless harness assertions are interpreted by runner policy. Struct casts assume the UAPI TDREPORT byte layout matches the locally declared spec structs. It only verifies report-data echoing, not MAC validity or measurement semantics.

## Test Signals
Signals are successful device open, successful `TDX_CMD_GET_REPORT0` ioctl, byte-for-byte match of 64-byte report data, and clean close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/tdx_guest_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/Makefile

## Purpose
Builds the Intel power floor notification selftest on x86 hosts only.

## Important APIs, Types, and Functions
Normalizes `ARCH` values matching `i.86` or `x86_64` to `x86`, sets `TEST_GEN_PROGS := power_floor_test` when `ARCH` is x86, and includes `../../../lib.mk`.

## Control Flow
If not cross-compiling and the normalized architecture is x86, kselftest builds `power_floor_test`. Otherwise no test program is generated from this Makefile.

## State and Persistence Behavior
Only build artifacts are produced. Runtime sysfs state is controlled by the C test, not the Makefile.

## Dependencies and Integration Points
Depends on kselftest `lib.mk` and an x86 build environment. It integrates with the thermal Intel selftest tree.

## Risks and Edge Cases
Cross-compile builds are intentionally skipped. Architecture detection depends on `uname -m` when `ARCH` is unset.

## Test Signals
Signal is generation of `power_floor_test` on native x86 builds and omission elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/power_floor_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/power_floor_test.c

## Purpose
Interactive/polling selftest for Intel power floor notifications exposed through fixed sysfs attributes under PCI device `0000:00:04.0`.

## Important APIs, Types, and Functions
Constants are `POWER_FLOOR_ENABLE_ATTRIBUTE` and `POWER_FLOOR_STATUS_ATTRIBUTE`. Function `power_floor_exit()` disables notifications on SIGINT/SIGHUP/SIGTERM. `main()` enables notifications, opens the status file, waits for `POLLPRI`, rereads status, and prints changes.

## Control Flow
`main()` installs signal handlers, opens the enable attribute and writes `1\n`, then loops forever. Each loop opens the status attribute, reads initial status, polls indefinitely for priority data, seeks back, reads the new status, prints it, and closes the fd. Signal handler writes `0\n` to disable notifications and exits.

## State and Persistence Behavior
The test toggles a persistent sysfs enable knob on the platform device. If killed by an unhandled signal, the feature may remain enabled. It does not write output files.

## Dependencies and Integration Points
Depends on Intel thermal/power-limit sysfs support at `/sys/bus/pci/devices/0000:00:04.0/power_limits/`, pollable sysfs notification semantics, and permissions to write the enable attribute.

## Risks and Edge Cases
The hard-coded PCI BDF is platform-specific. The loop is infinite and intended for manual interruption. Error paths inside the signal handler call `exit(1)` and may leave descriptors open. `status_str` is a three-byte buffer and printed as a string even though reads may not NUL-terminate it.

## Test Signals
Signals include successful enable write, `POLLPRI` wakeups on status changes, printed status values, and disable write on handled termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/power_floor_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/Makefile

## Purpose
Builds the Intel workload hint selftest on x86 hosts only.

## Important APIs, Types, and Functions
Normalizes `ARCH` to `x86`, sets `TEST_GEN_PROGS := workload_hint_test` for x86, and includes `../../../lib.mk`.

## Control Flow
The kselftest build includes this program only when not cross-compiling and when the normalized architecture is x86.

## State and Persistence Behavior
Only build artifacts are produced. Runtime workload-hint sysfs state is managed by the C program.

## Dependencies and Integration Points
Depends on kselftest `lib.mk` and an x86 native build. Integrates with Intel thermal workload hint tests.

## Risks and Edge Cases
No program is built for cross-compile or non-x86 contexts even if target hardware could expose compatible sysfs.

## Test Signals
Signal is generation of `workload_hint_test` on native x86 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/workload_hint_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/workload_hint_test.c

## Purpose
Interactive/polling selftest for Intel workload type hints and slow workload hints exposed through sysfs on PCI device `0000:00:04.0`.

## Important APIs, Types, and Functions
Constants name sysfs attributes for `notification_delay_ms`, `workload_hint_enable`, `workload_slow_hint_enable`, and `workload_type_index`. `workload_types` maps indices to `idle`, `battery_life`, `sustained`, and `bursty`. Globals `wlt_slow` and `wlt_enable_attr` select normal or slow hint mode. Functions are `workload_hint_exit()`, `update_delay()`, and `main()`.

## Control Flow
`main()` prints usage, parses optional delay values and `slow`, writes notification delay if provided, installs signal handlers, selects the enable attribute, writes `1\n`, then loops opening and polling `workload_type_index`. On each `POLLPRI`, it rereads the index, converts it to a workload type string, and prints it. The signal handler writes `0\n` to the selected enable attribute.

## State and Persistence Behavior
The test changes sysfs enable and notification-delay state on the platform device. It runs indefinitely until interrupted and relies on handled signals to disable hints. No output files are persisted.

## Dependencies and Integration Points
Depends on Intel thermal workload-hint sysfs attributes, pollable status notifications, permissions to write sysfs, and the fixed PCI BDF.

## Risks and Edge Cases
The argument loop parses `argv[1]` for every non-`slow` argument instead of `argv[i]`, so multiple non-slow args are mishandled. `sscanf` failure check uses `ret < 0` rather than `ret != 1`. Fixed BDF and infinite loop limit automation. Index bounds must be checked before using `workload_types`.

## Test Signals
Signals include successful delay write, enable write for normal or slow mode, poll wakeups, valid workload index-to-name printing, and disable on handled termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/workload_hint_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/Makefile

## Purpose
Builds time namespace selftests and the extended `gettime_perf` benchmark.

## Important APIs, Types, and Functions
Sets `TEST_GEN_PROGS := timens timerfd timer clock_nanosleep procfs exec futex vfork_exec`, `TEST_GEN_PROGS_EXTENDED := gettime_perf`, `CFLAGS := -Wall -Werror -pthread`, `LDLIBS := -lrt -ldl`, and includes `../lib.mk`.

## Control Flow
Kselftest build compiles the listed programs with pthread, realtime, and dl dependencies. `gettime_perf` is marked extended rather than part of the default generated program set.

## State and Persistence Behavior
Only build outputs are produced. Runtime namespace/proc state is handled by individual tests.

## Dependencies and Integration Points
Depends on kselftest `lib.mk`, POSIX realtime library, pthreads, and dlopen support. Integrates with CONFIG_TIME_NS testing.

## Risks and Edge Cases
`-Werror` makes warnings build-breaking. Some tests require root/time namespace support at runtime even when compilation succeeds.

## Test Signals
Signals include successful build of all default time namespace tests and optional extended benchmark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/clock_nanosleep.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/clock_nanosleep.c

## Purpose
Tests `clock_nanosleep()` behavior inside a time namespace for relative and absolute sleeps across namespace-offset clocks.

## Important APIs, Types, and Functions
Uses `test_sig()` as a signal handler, `run_test(clockid, abs)` for one clock/mode, and `main()` to set up support checks and run cases. It includes `timens.h` and `log.h` for namespace helpers and kselftest logging.

## Control Flow
The program verifies time namespace support, unshares a new time namespace, applies offsets through `/proc/self/timens_offsets`, then runs `clock_nanosleep()` for selected clocks in relative and absolute modes. It checks that sleeps do not complete too early relative to the clock's offset behavior and reports kselftest results.

## State and Persistence Behavior
State is per-process namespace membership and offset entries in `/proc/self/timens_offsets`. No files are persisted. Signal state is process-local.

## Dependencies and Integration Points
Depends on `CLONE_NEWTIME`, `/proc/self/timens_offsets`, POSIX clock APIs, and kselftest helpers. Integrates with the shared skip logic in `timens.h`.

## Risks and Edge Cases
Requires privileges to unshare time namespaces. Alarm-clock and POSIX timer support may be unavailable and should be skipped. Timing tolerances can be affected by scheduler latency.

## Test Signals
Signals are kselftest pass/skip/fail lines for relative and absolute `clock_nanosleep` on supported clocks after applying namespace offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/clock_nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/config

## Purpose
Kselftest config fragment requiring time namespace support.

## Important APIs, Types, and Functions
Contains `CONFIG_TIME_NS=y`.

## Control Flow
No executable flow; consumed by selftest config tooling.

## State and Persistence Behavior
Static kernel configuration requirement only.

## Dependencies and Integration Points
Integrates with all tests under `tools/testing/selftests/timens` that rely on `CLONE_NEWTIME` and `/proc/self/ns/time`.

## Risks and Edge Cases
The config option does not guarantee the test runner has permissions to create time namespaces.

## Test Signals
Signal is kernel config coverage for `CONFIG_TIME_NS=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/exec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/exec.c

## Purpose
Tests that time namespace offsets survive an `exec` boundary and are visible in the executed program.

## Important APIs, Types, and Functions
Contains `main()` using helpers from `timens.h` and kselftest logging. It uses `unshare_timens()`, `_settime()`, `clock_gettime()`, and `exec`-style process replacement.

## Control Flow
The program checks namespace support, creates a child time namespace or detects an execed mode via arguments, sets offsets, then executes itself or a helper path to validate that the new image observes the expected shifted clock values.

## State and Persistence Behavior
Time namespace offsets are stored by the kernel for the namespace and should persist across `exec`. No external files are written.

## Dependencies and Integration Points
Depends on `CLONE_NEWTIME`, procfs timens offsets, `execve`, clock APIs, and shared timens helpers.

## Risks and Edge Cases
Exec argument handling must distinguish parent and execed phases correctly. Privilege failures should skip rather than look like clock regressions. Timing comparisons need tolerance for elapsed time during exec.

## Test Signals
Signals are successful observation of expected offsets after exec and kselftest skip on unsupported or unprivileged systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/futex.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/futex.c

## Purpose
Tests futex timeout behavior under time namespace offsets for supported clocks.

## Important APIs, Types, and Functions
Core function is `run_test(clockid)`, with `main()` setting up namespace support and iterating clocks. It uses futex syscalls, `_settime()`, `_gettime()`, and `check_skip()` from `timens.h`.

## Control Flow
The test creates a time namespace, applies clock offsets, computes timeout values, invokes futex waits, and verifies timeout behavior relative to the namespace-adjusted clock. Unsupported clocks are skipped.

## State and Persistence Behavior
State is a process-local futex word plus kernel time namespace offsets. No persistent files are created.

## Dependencies and Integration Points
Depends on futex syscall support, `CLONE_NEWTIME`, procfs offsets, and kselftest logging. Integrates with kernel futex absolute/relative timeout clock handling.

## Risks and Edge Cases
Futex timeout behavior differs by clock flag support. Scheduler delays can make late wakeups acceptable but early wakeups are failures. Requires privileges for namespace creation.

## Test Signals
Signals are kselftest pass/fail per clock, with skips for unsupported timer configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/gettime_perf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/gettime_perf.c

## Purpose
Extended benchmark comparing `clock_gettime()` performance inside and outside a time namespace, including vDSO function paths.

## Important APIs, Types, and Functions
Functions are `fill_function_pointers()`, `test(clockid, clockstr, in_ns)`, and `main()`. It uses `dlopen`/`dlsym`-style resolution for vDSO symbols and clock APIs.

## Control Flow
The program resolves clock function pointers, measures repeated gettime calls for selected clocks outside a namespace, enters a time namespace, applies offsets if needed, and measures again. Results are printed rather than strict pass/fail functional assertions.

## State and Persistence Behavior
No persistent state. Runtime state includes loaded symbol pointers, namespace membership, and measured timing loops.

## Dependencies and Integration Points
Depends on `-ldl`, vDSO availability, `clock_gettime`, time namespaces, and shared timens helpers. It integrates with performance regression tracking rather than functional gating.

## Risks and Edge Cases
Benchmarks are noisy and scheduler/CPU-frequency dependent. vDSO symbol availability differs by architecture/libc. Root/time namespace support is still required for in-namespace measurements.

## Test Signals
Signals are printed latency/performance numbers for supported clocks in host and namespace contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/gettime_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/log.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/log.h

## Purpose
Shared logging macros for time namespace selftests.

## Important APIs, Types, and Functions
Defines `pr_msg`, `pr_p`, `pr_err`, `pr_fail`, and `pr_perror`. The macros wrap kselftest output helpers and return `-1` for error/fail paths.

## Control Flow
No standalone execution. Test code calls these macros to print context-rich messages including file and line or errno-derived text.

## State and Persistence Behavior
No state is owned. Output is emitted through kselftest stdout/stderr conventions.

## Dependencies and Integration Points
Depends on `kselftest.h` functions such as `ksft_print_msg`, `ksft_test_result_error`, and `ksft_test_result_fail`. Included by timens C files.

## Risks and Edge Cases
Macros use GNU statement expressions, so they require a compatible compiler. `pr_p` relies on `%m` errno formatting.

## Test Signals
Signals are consistently formatted error and failure messages from time namespace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/procfs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/procfs.c

## Purpose
Tests procfs views affected by time namespaces, especially `/proc/uptime` and `btime` from `/proc/stat`.

## Important APIs, Types, and Functions
Functions include `switch_ns`, `init_namespaces`, `read_proc_uptime`, `read_proc_stat_btime`, `check_uptime`, `check_stat_btime`, and `main`. It uses parent/child namespace file descriptors and helpers from `timens.h`.

## Control Flow
The test opens the parent time namespace, unshares a child time namespace, verifies different namespace inodes, sets offsets, switches between namespace fds, reads procfs time values, and checks that uptime and boot-time reporting reflect namespace semantics.

## State and Persistence Behavior
Kernel namespace offsets and namespace file descriptors are runtime state. Procfs reads are transient; no files are modified except `/proc/self/timens_offsets`.

## Dependencies and Integration Points
Depends on `/proc/self/ns/time_for_children`, `/proc/self/timens_offsets`, `/proc/uptime`, `/proc/stat`, `setns`, and kselftest helpers. Integrates with procfs time namespace virtualization.

## Risks and Edge Cases
Parsing procfs text is format-sensitive. Switching namespaces requires privileges and open descriptors. Time advances during comparisons, so tests must allow small drift.

## Test Signals
Signals are successful namespace inode separation and expected shifted values in `/proc/uptime` and `btime`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.c

## Purpose
Core time namespace gettime test. It verifies that namespace offsets affect supported clocks through both vDSO/libc and raw syscall paths while parent namespace time remains unchanged.

## Important APIs, Types, and Functions
Defines `struct test_clock` and `clocks[]` for boottime, boottime alarm, monotonic, monotonic coarse, and monotonic raw. Functions are `switch_ns`, `init_namespaces`, `test_gettime`, and `main`.

## Control Flow
`init_namespaces()` opens the parent `time_for_children` namespace, unshares a new time namespace, opens the child namespace, and verifies different inodes. `test_gettime()` switches to parent to capture a baseline, switches to child, reads the clock through vDSO/libc or raw syscall, and compares it to expected parent time plus offset. `main()` sets clock offsets and runs all clocks through both access paths.

## State and Persistence Behavior
State is held in namespace file descriptors and per-clock offsets written to `/proc/self/timens_offsets`. No external persistence is used.

## Dependencies and Integration Points
Depends on `setns`, `unshare(CLONE_NEWTIME)`, procfs time namespace files, POSIX clock APIs, raw `SYS_clock_gettime`, and kselftest output. Integrates with vDSO and syscall implementations of time namespace offsets.

## Risks and Edge Cases
Coarse/raw clocks share monotonic offsets, represented by `off_id`; mapping mistakes cause false failures. Precision tolerances differ for coarse/raw clocks. Requires root or equivalent namespace privileges.

## Test Signals
Signals are pass lines for each clock and access path, skip lines for unsupported alarm/POSIX timers, and failure if parent/child offsets are wrong.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.h

## Purpose
Shared helper header for time namespace selftests.

## Important APIs, Types, and Functions
Defines `CLONE_NEWTIME` fallback, globals `config_posix_timers` and `config_alarm_timers`, and inline helpers `check_supported_timers`, `check_skip`, `unshare_timens`, `_settime`, `_gettime`, and `nscheck`.

## Control Flow
Tests include this header, call `nscheck()` and `check_supported_timers()`, create a namespace with `unshare_timens()`, write offsets through `_settime()`, read clocks through `_gettime()`, and skip unsupported clock cases through `check_skip()`.

## State and Persistence Behavior
The header owns per-translation-unit static booleans for timer feature availability. `_settime()` writes to `/proc/self/timens_offsets`, changing kernel namespace state.

## Dependencies and Integration Points
Depends on fcntl/unistd/stdlib/stdbool, kselftest, procfs time namespace files, clock APIs, and raw syscalls in includers. It integrates all timens tests with common skip and offset behavior.

## Risks and Edge Cases
Because globals are `static` in a header, each C file has its own copy, which is intended but notable. `_settime()` maps coarse/raw monotonic clocks to `CLOCK_MONOTONIC`; callers must understand shared offset semantics. `unshare_timens()` exits skip only on `EPERM`.

## Test Signals
Signals are consistent skip behavior for unsupported time namespaces, alarm timers, or POSIX timers, plus successful offset writes and clock reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timer.c

## Purpose
Tests POSIX timer expiration behavior under time namespace offsets.

## Important APIs, Types, and Functions
Core function is `run_test(clockid, now)`, with `main()` setting up namespace and iterating supported clocks. Uses `timer_create`, `timer_settime`, `clock_gettime`, and shared timens helpers.

## Control Flow
The test creates or enters a time namespace, sets offsets, gets current time, arms timers for selected clocks, waits for expiration or signal delivery, and verifies timers fire according to namespace-adjusted time rather than host time.

## State and Persistence Behavior
Runtime state includes POSIX timer IDs, signal/timer state, and namespace offsets. No persistent files are created.

## Dependencies and Integration Points
Depends on POSIX timers, supported clock IDs, `CLONE_NEWTIME`, procfs offset writes, and kselftest. Integrates with kernel timer namespace offset handling.

## Risks and Edge Cases
POSIX timers may be unavailable when `CONFIG_POSIX_TIMERS` is off, requiring skips. Timer delivery can be delayed by scheduling, so tests should detect early/wrong-clock behavior more strictly than late behavior.

## Test Signals
Signals are kselftest pass/skip/fail outcomes for timer expiration on each supported clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timerfd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timerfd.c

## Purpose
Tests `timerfd` behavior in time namespaces for namespace-offset clocks.

## Important APIs, Types, and Functions
Functions are `tclock_gettime(clockid, now)`, `run_test(clockid, now)`, and `main`. It uses `timerfd_create`, `timerfd_settime`, `read`, `clock_gettime`, and shared timens helpers.

## Control Flow
The test establishes time namespace offsets, gets current time for each clock, creates a timerfd, arms it with namespace-relevant expiration, reads the expiration count, and validates that it fires according to expected shifted time.

## State and Persistence Behavior
Timerfd descriptors and namespace offsets are runtime-only state. No files are persisted beyond procfs offset writes.

## Dependencies and Integration Points
Depends on Linux timerfd APIs, time namespace support, clock APIs, and kselftest. It integrates with timerfd clock handling and namespace offset code.

## Risks and Edge Cases
Some clock IDs are unsupported by timerfd and should be skipped. File descriptor cleanup matters to avoid leaks in loops. Timing checks can be sensitive to scheduler delay.

## Test Signals
Signals include successful timerfd creation/arming/read for supported clocks and correct skip/fail reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timerfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/vfork_exec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/vfork_exec.c

## Purpose
Tests time namespace behavior across `vfork` plus `exec`, including validation from both the execed process and a thread.

## Important APIs, Types, and Functions
Functions include `tcheck`, `check_in_thread`, `check`, and `main`. It uses pthreads, `vfork`, `exec`, clock reads, and shared timens helpers.

## Control Flow
The parent creates a time namespace and sets offsets, then uses `vfork`/`exec` to re-run or run a checking path. The check compares current clock values against expected namespace-shifted values and also performs a threaded check to ensure namespace semantics are consistent with threads.

## State and Persistence Behavior
Namespace offsets survive through the process transition. Runtime state includes expected times passed through arguments or inherited state and thread-local checks. No persistent files are written.

## Dependencies and Integration Points
Depends on `vfork`, `exec`, pthreads, time namespace support, and kselftest. It integrates with process-creation and namespace inheritance semantics.

## Risks and Edge Cases
`vfork` has strict parent/child memory-sharing constraints before exec. Timing comparison must allow elapsed time during process creation. Privilege failures should be skipped cleanly.

## Test Signals
Signals are pass/fail from both direct and threaded checks after vfork/exec under shifted namespace time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timens/vfork_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/Makefile

## Purpose
Builds the general kernel timer selftests and separates safe default tests from destructive time-changing tests.

## Important APIs, Types, and Functions
Sets `CFLAGS += -O3 -Wl,-no-as-needed -Wall -I $(top_srcdir)` and `LDLIBS += -lrt -lpthread -lm`. `TEST_GEN_PROGS` includes safe tests such as `posix_timers`, `nanosleep`, `nsleep-lat`, `mqueue-lat`, `inconsistency-check`, `raw_skew`, `threadtest`, and `rtcpie`. `DESTRUCTIVE_TESTS` includes `alarmtimer-suspend`, `valid-adjtimex`, `adjtick`, `change_skew`, `skew_consistency`, `clocksource-switch`, `freq-step`, `leap-a-day`, `leapcrash`, `set-tai`, `set-2038`, and `set-tz`. `TEST_GEN_PROGS_EXTENDED` is set to destructive tests.

## Control Flow
Default kselftest builds safe programs and extended destructive programs. The `run_destructive_tests` target first runs default tests, then invokes `RUN_TESTS` for destructive tests.

## State and Persistence Behavior
Build outputs are test binaries. Destructive runtime state can include system time, NTP state, clocksource selection, suspend state, and timezone/TAI settings, but those are controlled by individual tests.

## Dependencies and Integration Points
Depends on kselftest `lib.mk`, realtime library, pthreads, math library, and top source includes. Integrates with generic timers selftest execution.

## Risks and Edge Cases
The Makefile explicitly distinguishes tests that modify global system state or trigger suspend. Running `run_destructive_tests` on shared machines can disrupt timekeeping or power state.

## Test Signals
Signals include successful compilation of safe and extended tests and deliberate opt-in execution of destructive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/adjtick.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/adjtick.c

## Purpose
Destructive timer test that adjusts the kernel tick length with `adjtimex(ADJ_TICK)` and verifies the measured monotonic-vs-raw drift matches the expected ppm shift.

## Important APIs, Types, and Functions
Uses global `systick`. Helpers are `llabs`, `ts_to_nsec`, `nsec_to_ts`, `diff_timespec`, `get_monotonic_and_raw`, `get_ppm_drift`, `check_tick_adj`, and `main`.

## Control Flow
`main()` checks `CLOCK_MONOTONIC_RAW`, computes the nominal tick from `_SC_CLK_TCK`, and iterates tick values across +/-10 percent. `check_tick_adj()` sets tick/frequency/status through `adjtimex`, waits, measures drift over 15 seconds, validates returned adjtimex values, compares expected and measured ppm within 100 ppm, and prints OK/FAILED. Finally it resets tick/frequency to nominal.

## State and Persistence Behavior
It modifies global kernel timekeeping discipline through `adjtimex`. It attempts to reset tick, offset, and frequency at the end, but interruption or failure can leave altered state.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, `CLOCK_MONOTONIC_RAW`, `CLOCK_MONOTONIC`, and kselftest. It integrates with kernel NTP/tick adjustment code.

## Risks and Edge Cases
The test is long-running and sensitive to NTP daemons, scheduler interruptions, and clocksource precision. It destructively changes system timekeeping and assumes it can restore state.

## Test Signals
Signals are per-tick OK lines with measured ppm close to expected, no unexpected adjtimex return values, and final kselftest pass after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/adjtick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/alarmtimer-suspend.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/alarmtimer-suspend.c

## Purpose
Destructive test for alarm timers and RTC wakeup across suspend. It arms realtime and boottime alarm timers and verifies wake latency while repeatedly suspending the system.

## Important APIs, Types, and Functions
Globals include `alarmcount`, `alarm_clock_id`, `start_time`, and `final_ret`. Functions are `clockstring`, `timespec_sub`, signal handler `sigalarm`, and `main`.

## Control Flow
`main()` installs a real-time signal handler, loops over `CLOCK_REALTIME_ALARM` and `CLOCK_BOOTTIME_ALARM`, creates an interval timer firing every 15 seconds, waits for five alarms without suspend, then enters suspend loops by writing `mem` to `/sys/power/state` until ten alarms have fired or suspend fails. `sigalarm()` computes latency from expected interval count and flags excessive latency over five seconds.

## State and Persistence Behavior
It creates POSIX timers and writes to `/sys/power/state`, changing global system power state. It does not persist files, but it can suspend the machine and depends on RTC wake alarms.

## Dependencies and Integration Points
Depends on alarmtimer support, RTC wake capability, permissions to suspend, signal delivery, and kselftest. Integrates with kernel alarmtimer, suspend/resume, and clock code.

## Risks and Edge Cases
This test is disruptive and can suspend active systems. Hardware without RTC wake support, disabled suspend, or delayed resume can fail. It breaks from the clock loop if `timer_create` fails for an alarm clock.

## Test Signals
Signals include alarm latency lines marked OK, successful suspend/resume cycles, and kselftest fail if latency exceeds the threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/alarmtimer-suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/change_skew.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/change_skew.c

## Purpose
Destructive meta-test that changes kernel clock frequency skew and runs other timer tests to detect regressions under adjusted timekeeping.

## Important APIs, Types, and Functions
Functions are `change_skew_test(ppm)` and `main`. It uses `adjtimex(ADJ_FREQUENCY)`, `system("./raw_skew")`, `system("./inconsistency-check")`, and `system("./nanosleep")`.

## Control Flow
`main()` kills `ntpd`, clears offset adjustment, then iterates ppm values `{0, 250, 500, -250, -500}`. For each value, `change_skew_test()` applies frequency adjustment and runs the three companion tests, accumulating failures. At the end it resets frequency to zero and exits pass/fail.

## State and Persistence Behavior
It modifies global kernel frequency discipline and kills the `ntpd` process. It relies on cleanup to reset frequency, but abrupt termination can leave changed timekeeping.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, companion binaries in the current directory, shell `system()`, and kselftest. Integrates with NTP frequency adjustment and timer correctness tests.

## Risks and Edge Cases
Highly disruptive: kills NTP and changes global clock skew. It assumes current working directory contains required binaries. `system()` return aggregation loses detailed failure attribution.

## Test Signals
Signals are successful companion test runs under each ppm setting and final reset to zero frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/change_skew.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/clocksource-switch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/clocksource-switch.c

## Purpose
Destructive test that cycles available clocksources and runs timer consistency checks after each switch.

## Important APIs, Types, and Functions
Functions are `get_clocksources`, `get_cur_clocksource`, `change_clocksource`, `run_tests`, and `main`. It reads and writes sysfs clocksource files and invokes companion tests.

## Control Flow
The test reads available clocksources, records the current one, switches to each available source via sysfs, runs timer checks for a requested duration or default, and finally restores the original clocksource. Companion checks include consistency and skew-related timer tests.

## State and Persistence Behavior
It modifies `/sys/devices/system/clocksource/clocksource0/current_clocksource`, affecting global timekeeping source selection. It attempts to restore the original source.

## Dependencies and Integration Points
Depends on root privileges, clocksource sysfs, available alternative clocksources, companion timer binaries, and kselftest. Integrates with kernel clocksource switching and timekeeping consistency.

## Risks and Edge Cases
Switching clocksources can affect the whole system. Some clocksources may be unstable or unavailable for writing. Failure before restore can leave a non-default clocksource.

## Test Signals
Signals include successful enumeration, successful switch to each source, companion test success, and restoration of the original clocksource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/clocksource-switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/freq-step.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/freq-step.c

## Purpose
Destructive precision test for kernel response to frequency steps made with `adjtimex()`. It measures `CLOCK_MONOTONIC` frequency error and stability relative to `CLOCK_MONOTONIC_RAW` after step changes.

## Important APIs, Types, and Functions
Defines `struct sample` and globals for bases, user HZ, precision, and raw frequency offset. Functions are `diff_timespec`, `get_sample`, `reset_ntp_error`, `set_frequency`, `regress`, `run_test`, `init_test`, and `main`.

## Control Flow
`init_test()` verifies raw and monotonic clocks, estimates sampling precision, skips if precision is too poor, seeds randomness, and calibrates raw frequency offset. `main()` runs multiple randomized frequency base/step combinations. `run_test()` sets a base frequency, resets NTP error, applies a step, samples 100 monotonic/raw offsets, performs linear regression on first and second halves, and fails if second-interval frequency error or standard deviation exceed thresholds. It resets frequency to zero at the end.

## State and Persistence Behavior
Modifies global timekeeping frequency and NTP error through `adjtimex`. Runtime samples are stack arrays. Cleanup resets frequency, but interruption can leave modified timekeeping.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, math library, monotonic/raw clocks, `sysconf(_SC_CLK_TCK)`, and kselftest. Integrates with kernel timekeeping frequency discipline.

## Risks and Edge Cases
Results are sensitive to CPU scheduling, virtualization, clocksource quality, and NTP interference. Randomized intervals can make failures hard to reproduce without logging seeds.

## Test Signals
Signals are acceptable sampling precision, printed frequency error/stddev/max rows marked OK, and final pass after resetting frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/freq-step.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/inconsistency-check.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/inconsistency-check.c

## Purpose
Checks that repeated clock reads do not go backward or become inconsistent across supported clocks over a test duration.

## Important APIs, Types, and Functions
Defines `CLOCK_HWSPECIFIC` and `CALLS_PER_LOOP`. Important functions include `clockstring`, `in_order`, `consistency_test(clock_type, seconds)`, and `main`.

## Control Flow
`main()` prints a kselftest plan and iterates clock IDs, skipping unsupported or inappropriate clocks. `consistency_test()` repeatedly samples a clock for the requested duration and flags any out-of-order timestamps. Unsupported clocks are skipped.

## State and Persistence Behavior
No persistent state. It reads clocks only and keeps last/current timestamps in memory.

## Dependencies and Integration Points
Depends on POSIX clock APIs, kselftest, and optionally command-line duration. It integrates with generic timekeeping monotonicity validation and is also invoked by destructive meta-tests.

## Risks and Edge Cases
Virtualized or unstable clocksources can produce false failures. CPU time clocks and deprecated hardware-specific clock IDs need special handling. Very short or long durations alter detection sensitivity.

## Test Signals
Signals are pass/skip/fail results per clock, with failures indicating time moved backward or clock reads were inconsistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/inconsistency-check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leap-a-day.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leap-a-day.c

## Purpose
Destructive leap-second stress test. It repeatedly schedules insert/delete leap seconds, optionally sets the system time near midnight UTC, and checks timer/NTP state around the leap boundary.

## Important APIs, Types, and Functions
Globals are `next_leap` and `error_found`. Functions include `in_order`, `timespec_add`, `time_state_str`, `clear_time_state`, `handler`, `sigalarm`, `test_hrtimer_failure`, and `main`.

## Control Flow
`main()` parses options for wait mode, iterations, and TAI printing; validates `CLOCK_TAI` when requested; installs handlers; then loops. Each iteration computes next midnight, optionally uses `settimeofday()` to move to ten seconds before it, clears NTP state, sets `STA_INS` or `STA_DEL`, arms a realtime timer for the leap moment, sleeps to just before the leap, repeatedly prints `adjtimex` state through the boundary, checks for early hrtimer expiry, toggles insert/delete mode, and exits after the requested iterations. Cleanup clears time state.

## State and Persistence Behavior
It modifies global wall clock time, NTP leap status, TAI/leap state, and POSIX timers. It tries to clear state on normal exit and SIGINT, but it cannot catch SIGKILL despite registering a handler call.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, `settimeofday`, POSIX timers, realtime clock, optional `CLOCK_TAI`, and kselftest. Integrates with kernel leap-second state machine and hrtimer behavior.

## Risks and Edge Cases
Very disruptive: changes system time by days in default mode. NTP daemons can conflict. Signal registration for SIGKILL is ineffective. Option string in source includes `s` but switch handles `w`, indicating documentation/parser drift.

## Test Signals
Signals include correct `TIME_WAIT` observation at the leap, no early timer expiration, no hrtimer failure, and cleanup of NTP state before pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leap-a-day.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leapcrash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leapcrash.c

## Purpose
Destructive regression/demo test for historical leap-second deadlocks. It repeatedly sets the system near a leap second and hammers `adjtimex(STA_INS)` through the boundary.

## Important APIs, Types, and Functions
Functions are `clear_time_state`, `handler`, and `main`. It uses `clock_gettime`, `settimeofday`, `adjtimex`, signal handling, and kselftest exits.

## Control Flow
`main()` clears NTP time state, computes next midnight, then loops 20 times. Each loop sets wall time to two seconds before the leap, calls `adjtimex`, repeatedly sets `STA_INS` until after the leap second, clears time state, and prints progress. Permission failures from `settimeofday` fail the test.

## State and Persistence Behavior
It modifies global wall clock time and NTP leap status. It attempts cleanup on SIGINT and normal loop completion, but abrupt termination can leave time state changed.

## Dependencies and Integration Points
Depends on root privileges, realtime clock, `settimeofday`, `adjtimex`, and kselftest. Integrates with leap-second handling and NTP state transitions.

## Risks and Edge Cases
The source warning notes possible hard hangs and data loss on affected kernels. It is destructive and should only run in controlled environments. SIGKILL cannot actually be handled.

## Test Signals
Signals are completion of 20 boundary-hammer loops, printed progress dots, cleanup of time state, and kselftest pass without hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leapcrash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/mqueue-lat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/mqueue-lat.c

## Purpose
Measures POSIX message queue timed-receive timeout latency.

## Important APIs, Types, and Functions
Defines `TARGET_TIMEOUT` as 100 ms and `UNRESONABLE_LATENCY` as 40 ms. Functions are `timespec_sub`, `timespec_add`, `mqueue_lat_test`, and `main`.

## Control Flow
`mqueue_lat_test()` opens `/foo` as a read-only POSIX message queue, obtains message size, then performs 100 `mq_timedreceive()` calls on an empty queue with absolute realtime deadlines 100 ms in the future. It measures elapsed monotonic time and fails if average timeout exceeds target plus latency threshold. `main()` prints a status line and exits pass/fail.

## State and Persistence Behavior
Creates a POSIX message queue named `/foo` and closes it, but the source does not call `mq_unlink`, so the queue name may persist depending on system behavior and prior state.

## Dependencies and Integration Points
Depends on POSIX mqueue support, realtime library, `/dev/mqueue` availability/configuration, and kselftest. Integrates with `mq_timedreceive` timeout handling.

## Risks and Edge Cases
Lack of `mq_unlink` can leave stale `/foo`. Existing queue attributes may influence `mq_msgsize` if `/foo` already exists. Scheduler load can cause latency failures.

## Test Signals
Signals are `[OK]` when average timeout latency is within 40 ms of 100 ms, or failure on mqueue API errors/unreasonable latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/mqueue-lat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nanosleep.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nanosleep.c

## Purpose
Verifies `clock_nanosleep()` does not return before requested absolute or relative deadlines, and that interrupted sleeps report a sane remaining time.

## Important APIs, Types, and Functions
Defines `CLOCK_HWSPECIFIC` and `UNSUPPORTED`. Functions are `clockstring`, `in_order`, `timespec_add`, `nanosleep_test`, `dummy_event_handler`, `nanosleep_test_remaining`, and `main`.

## Control Flow
`main()` plans tests for clocks from `CLOCK_REALTIME` through `CLOCK_TAI`, skipping process/thread CPU and hardware-specific clocks. For each supported clock it runs absolute and relative sleeps from 10 ns to 10 seconds and fails on early return. It then arms a timer to interrupt a longer sleep and validates returned remaining time is between zero and requested duration.

## State and Persistence Behavior
No persistent state. Runtime state includes a temporary POSIX timer and SIGALRM handler, restored to default after the interrupted-sleep check.

## Dependencies and Integration Points
Depends on POSIX clocks, `clock_nanosleep`, POSIX timers, signal handling, and kselftest. Integrates with generic timer and sleep paths.

## Risks and Edge Cases
Unsupported clocks are skipped. The remaining-time test depends on signal delivery and `timer_create` support for the same clock. It treats early wakeups as hard failures but tolerates late wakeups.

## Test Signals
Signals are per-clock pass/skip lines, with immediate failure if any sleep returns before target or remaining time is invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nsleep-lat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nsleep-lat.c

## Purpose
Measures `clock_nanosleep()` latency for relative and absolute sleeps across supported clocks.

## Important APIs, Types, and Functions
Defines `UNRESONABLE_LATENCY`, `CLOCK_HWSPECIFIC`, `UNSUPPORTED`, and `SKIPPED_CLOCK_COUNT`. Functions are `clockstring`, `timespec_add`, `timespec_sub`, `nanosleep_lat_test`, and `main`.

## Control Flow
`main()` iterates clocks from realtime through TAI, skipping CPU-time and hardware-specific clocks. For each clock, it tests sleep lengths from 10 ns up to 10 seconds. `nanosleep_lat_test()` checks average relative sleep latency over 10 iterations and average absolute sleep latency over 10 iterations, failing if either exceeds 40 ms.

## State and Persistence Behavior
No persistent state. It only reads clocks and sleeps.

## Dependencies and Integration Points
Depends on POSIX clock APIs, `clock_nanosleep`, and kselftest. Integrates with scheduler/timer latency behavior.

## Risks and Edge Cases
Latency results are workload and scheduler dependent. The threshold is permissive but can still fail under heavy load or virtualized environments. Unsupported clocks are skipped.

## Test Signals
Signals are per-clock pass/skip/fail lines, with failure messages showing large relative or absolute latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nsleep-lat.c -->

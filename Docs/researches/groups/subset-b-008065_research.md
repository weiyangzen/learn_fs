# Research: subset-b-008065

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/blockade.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/blockade.py

Purpose: Python wrapper around the external `blockade` CLI used by Ozone network fault-injection tests. It centralizes cluster lifecycle and network partition commands so tests and `OzoneCluster` do not shell out directly.

Important APIs/types/functions: `Blockade.blockade_destroy`, `blockade_up`, `blockade_status`, `make_flaky`, `blockade_fast_all`, `blockade_create_partition`, `blockade_join`, `blockade_stop`, `blockade_start`, and `blockade_add`. All are classmethods. Most use `subprocess.call`; `blockade_create_partition` uses `ozone.util.run_command` to assemble variadic partition sets into a single command string.

Control flow: callers first check/destroy an existing blockade state, run `blockade up`, add docker-compose containers, then use partition/fast/join/stop/start helpers during tests. Failures are surfaced by assertions on exit codes for mutating operations.

State and persistence behavior: no Python-local persistent state. State lives in blockade/docker networking and container runtime. `blockade_create_partition` builds a space-delimited list of comma-joined node groups that blockade interprets as separate network partitions.

Dependencies and integration points: depends on `blockade` being installed and on `ozone.util.run_command`. Integrated by `ozone.cluster.OzoneCluster` and `test_blockade_flaky.py`.

Risks: asserts can be optimized away with Python `-O`; command construction is string-based; `import util` is package-relative fragile; there is no timeout around blockade calls.

Test signals: exercised indirectly by all blockade tests that create partitions, restore networks, or mark nodes flaky.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/blockade.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/client.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/client.py

Purpose: thin test client that runs Ozone shell and Freon commands inside the cluster's `ozone_client` docker container.

Important APIs/types/functions: `OzoneClient` stores an `OzoneCluster`. `create_volume` runs `ozone sh volume create`. `create_bucket` runs `ozone sh bucket create`. `put_key` validates the source file inside the client container and runs `ozone sh key put`, optionally with `--replication`. `get_key` runs `ozone sh key get`. `run_freon` builds an `ozone freon rk` command with volume, bucket, key count, key size, replication type, and replication factor.

Control flow: callers obtain it through `OzoneCluster.get_client()`, prepare volumes/buckets/keys or use `run_freon` to generate data, then assert exit status. `run_freon` intentionally returns `(exit_code, output)` for tests to assert later.

State and persistence behavior: creates Ozone volumes, buckets, keys, and downloaded files in the client container. It does not cache Ozone metadata locally.

Dependencies and integration points: imports `ozone.util.run_docker_command` and `Command` from `ozone.cluster`/constants. Used throughout blockade tests to seed containers and verify client-visible recovery.

Risks: command arguments are concatenated into shell strings; API assumes root user and fixed Ozone CLI shape; replication option spelling must match the Freon/key command versions. Importing `Command` through `ozone.cluster` relies on a re-export side effect.

Test signals: tested by end-to-end blockade tests where Freon and key put/get must succeed across partition restore.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/cluster.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/cluster.py

Purpose: docker-compose/blockade backed Ozone test cluster harness for network fault-injection tests. It discovers container names, starts/scales/stops the cluster, and exposes helpers for inspecting datanode container replicas.

Important APIs/types/functions: `Configuration` selects `docker-compose.yaml` from `MAVEN_TEST`, `OZONE_HOME`, or a relative compose path and sets `DOCKER_COMPOSE_FILE`. `OzoneCluster.create/start/stop` manage lifecycle. Properties expose `om`, `scm`, `datanodes`, and `client`. Helpers include `get_conf_value`, `scale_datanode`, `partition_network`, `restore_network`, `get_client`, `get_container`, `is_container_replica_exist`, `get_containers_on_datanode`, `get_container_state`, and `get_container_datanodes`.

Control flow: `start` validates `OZONE_RUNNER_VERSION` and `HDDS_VERSION`, destroys an existing blockade environment if present, runs `blockade up`, launches docker-compose with scaled datanodes, sleeps for startup, parses `docker-compose ps`, adds all containers to blockade, records OM/SCM/datanodes/client, discovers SCM UUID, and reads datanode data directory. Replica inspection walks datanode disk files under `hdds/<scmUuid>/current/containerDir0` and parses `.container` YAML-ish metadata.

State and persistence behavior: mutates docker-compose containers, blockade network state, and Ozone on-disk datanode state. Python object state caches container names, SCM UUID, and datanode directory.

Dependencies and integration points: uses docker-compose, blockade, PyYAML, Ozone CLI, SCM CLI, local `Blockade`, `OzoneClient`, `Container`, and `ContainerNotFoundError`. Tests use the global `cluster` fixture-style variable.

Risks: Python 2 idioms (`filter()[0]`, `output.split` on bytes/string assumptions, `is not 0`) are fragile on Python 3; `yaml.load` lacks a safe loader; fixed sleeps can flake; shell commands embed paths and IDs directly; default argument `Configuration()` is constructed at import time.

Test signals: every blockade test depends on successful `start`, partition restore, and replica state parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/constants.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/constants.py

Purpose: command-name constants for blockade network tests.

Important APIs/types/functions: `Command` class exposes string constants `docker`, `docker_compose`, `ozone`, and `freon`. `ozone` points at `/opt/hadoop/bin/ozone`; `freon` is `/opt/hadoop/bin/ozone freon`.

Control flow: there is no executable flow; other modules import constants to build docker and Ozone commands.

State and persistence behavior: no state. The values represent external command entry points inside the test environment.

Dependencies and integration points: imported by `ozone.util`, `ozone.cluster`, and `ozone.client`.

Risks: command paths are hard-coded for the Ozone docker image. Changing the image layout or docker-compose binary name requires updating this file. `freon` embeds a space, so callers must know whether a list item is a shell fragment rather than an argv token.

Test signals: failures show up as command-not-found or nonzero exit assertions in blockade tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/container.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/container.py

Purpose: object wrapper for an Ozone container ID in blockade tests, with polling helpers for expected replica states under network partitions.

Important APIs/types/functions: `Container(container_id, cluster)` delegates all inspection to `OzoneCluster`. `is_on`, `get_datanode_states`, `get_state`, and wait helpers cover `QUASI_CLOSED`, `CLOSED`, and "not OPEN" conditions. Wait helpers use `ozone.util.wait_until` with 120 second timeout and 10 second frequency.

Control flow: tests obtain `Container` instances from `cluster.get_container` or `get_containers_on_datanode`, partition the network, then call state wait helpers before asserting exact or allowed replica states. Methods catch `ContainerNotFoundError` where a not-yet-materialized replica should be treated as false.

State and persistence behavior: stores only `container_id` and `cluster`. Replica state is live data read from datanode `.container` files through the cluster helper.

Dependencies and integration points: imports `ozone.exceptions.ContainerNotFoundError`, `ozone.util.wait_until`, and uses `cluster.datanodes` plus `cluster.get_container_state`.

Risks: polling returns assertion-style failures rather than rich diagnostics; all waits share fixed timeouts; replica state strings are hard-coded; missing replicas are sometimes false and sometimes errors depending on method.

Test signals: directly validates the core expected behavior of blockade tests: open, quasi-closed, and closed container replica transitions after isolation and healing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/container.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/exceptions.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/exceptions.py

Purpose: custom exception for missing Ozone containers in blockade tests.

Important APIs/types/functions: `ContainerNotFoundError(RuntimeError)` formats a message as `Container not found. ID = <id>` and passes it to `RuntimeError`.

Control flow: raised by `OzoneCluster.get_container` and `get_container_state` when SCM/datanode metadata lookups fail. `Container` wait predicates catch it where absence is acceptable while polling.

State and persistence behavior: no persistent state beyond the exception message.

Dependencies and integration points: imported by `ozone.cluster`, `ozone.container`, and `test_blockade_datanode_isolation.py`.

Risks: the constructor ignores extra positional/keyword args besides the first container ID, so callers should only pass the ID. The message is simple but sufficient for test diagnostics.

Test signals: missing container paths in blockade tests surface through this exception or through wait predicate retries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/exceptions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/util.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/util.py

Purpose: shell and polling utilities for blockade tests.

Important APIs/types/functions: `wait_until(predicate, timeout, check_frequency)` polls until a predicate returns true or asserts on timeout. `run_docker_command(command, run_on)` wraps `docker exec <container> bash -c <command>`. `run_command(cmd)` executes a shell command, captures stdout/stderr, logs output, returns `(returncode, output)`, and prints a simple duration. `get_checksum(file_path, run_on)` computes `md5sum` inside a container and extracts the checksum.

Control flow: command list fragments are joined with spaces before execution. `run_command` uses `subprocess.Popen(shell=True)` and `communicate`, then normalizes output with a regex.

State and persistence behavior: no local persistence; effects are external shell, docker, filesystem, and Ozone operations.

Dependencies and integration points: depends on `Command.docker`, Python `subprocess`, `time`, and `re`. Used by `Blockade`, `OzoneClient`, `OzoneCluster`, and tests.

Risks: shell=True with interpolated values, no timeout for commands, regex output normalization can alter diagnostics, and `wait_until` depends on asserts. String/bytes behavior is Python-version sensitive.

Test signals: every docker/Ozone command in blockade tests flows through this module, so failures are visible as nonzero exit codes and captured output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_client_failure.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_client_failure.py

Purpose: pytest scenarios for client-side write behavior when the client can reach only a subset of datanodes during container replication.

Important APIs/types/functions: module-level `setup_function` creates and starts `OzoneCluster`; `teardown_function` stops it. Tests are `test_client_failure_isolate_two_datanodes` and `test_client_failure_isolate_one_datanode`.

Control flow: each test seeds data with Freon, partitions OM/SCM/client with selected datanodes, writes a key from the client, inspects created containers and replica states, restores the network, waits for closure, and reruns Freon to prove the cluster still accepts workload. The one-datanode case also checks output text with regex and sleeps while the isolated datanode becomes stale.

State and persistence behavior: creates volumes/buckets/keys and container replicas in dockerized Ozone. Network state is mutated via blockade and restored during the test.

Dependencies and integration points: imports `OzoneCluster`, `ozone.util`, `re`, `time`, and logging. Uses `OzoneClient` APIs via `cluster.get_client()`.

Risks: fixed sleeps and output regexes can be brittle; the global `cluster` requires setup success; assertions assume a three datanode cluster and particular container state timing.

Test signals: asserts client-visible failure or success under partition, replica `OPEN/QUASI_CLOSED/CLOSED` states, and post-heal Freon success.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_client_failure.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_datanode_isolation.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_datanode_isolation.py

Purpose: pytest coverage for datanode-to-datanode isolation where one or all datanodes cannot communicate with peers while OM/SCM/client connectivity varies.

Important APIs/types/functions: `test_isolate_single_datanode` and `test_datanode_isolation_all`, with standard cluster setup/teardown. Imports `ContainerNotFoundError` for expected missing replica paths.

Control flow: tests seed a replicated container with Freon, create partitions, use `cluster.get_containers_on_datanode`, wait for one or all replicas to leave `OPEN`, assert replica states, restore network, wait for all closed, and verify Freon success. The all-isolated case checks each datanode's local view and tolerates missing container metadata during isolation.

State and persistence behavior: reads and writes Ozone container metadata on datanode disks. Network partitions are external blockade state.

Dependencies and integration points: relies on `OzoneCluster`, `Container` wait helpers, and Freon random key generation from the client container.

Risks: timing-sensitive state transitions; assumes replication factor three and three datanodes; direct disk metadata parsing can race with datanode writes; expected missing containers may mask unexpected placement changes.

Test signals: validates quasi-closed/closed convergence and post-restore all-closed replicas.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_datanode_isolation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_flaky.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_flaky.py

Purpose: pytest scenario for blockade's `flaky` mode applied to datanode containers while Ozone continues handling Freon load.

Important APIs/types/functions: `test_flaky(flaky_node)` is parameterized with `"datanode"`. Setup/teardown starts and stops `OzoneCluster`. It imports `Blockade` directly.

Control flow: chooses one datanode at random from `cluster.datanodes`, calls `Blockade.make_flaky`, runs Freon workload, then calls `Blockade.blockade_fast_all` to restore normal network speed/loss behavior.

State and persistence behavior: mutates blockade network impairment state and creates Ozone data through Freon. Does not inspect container metadata.

Dependencies and integration points: depends on `pytest`, `random`, `OzoneCluster`, and `Blockade`.

Risks: random node selection makes failures less reproducible unless test logs record the selected node; only datanode is parameterized despite a generic argument name; no `finally` around `blockade_fast_all` inside the test body.

Test signals: Freon exit code under a flaky datanode and ability to clear impairment with `fast --all`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_flaky.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure.py

Purpose: pytest scenarios combining datanode peer isolation with SCM isolation for one datanode.

Important APIs/types/functions: `test_one_dn_isolate_scm_other_dn` and `test_one_dn_isolate_other_dn`, plus standard setup/teardown.

Control flow: both tests seed data with Freon, build multiple partition sets containing OM/SCM/client/datanodes in different combinations, run Freon during the partition, inspect containers from a selected datanode, wait for quasi-closed or closed states, assert allowed state combinations, restore network, wait for all replicas closed, and rerun Freon.

State and persistence behavior: mutates blockade partitions and Ozone container metadata. Test state is entirely in dockerized cluster runtime.

Dependencies and integration points: relies on `OzoneCluster`, `OzoneClient.run_freon`, and `Container` wait methods.

Risks: expected outcomes are tightly coupled to current Ozone close/quasi-close algorithms; multiple overlapping partition sets are hard to reason about; direct state reads can race with recovery.

Test signals: mixed failures should produce specific `QUASI_CLOSED`, `OPEN`, and `CLOSED` combinations during isolation, then all `CLOSED` after healing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_three_nodes_isolate.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_three_nodes_isolate.py

Purpose: pytest scenarios for all three datanodes isolated from each other, with zero, one, two, or three datanodes also unable to communicate with SCM.

Important APIs/types/functions: tests are `test_three_dns_isolate_one_scm_failure`, `test_three_dns_isolate_two_scm_failure`, and `test_three_dns_isolate_three_scm_failure`.

Control flow: each test starts from Freon-created data, partitions each datanode into its own group with OM/client and optional SCM reachability, waits on a representative container state, asserts per-datanode replica states, restores the network, waits for all replicas closed, and runs Freon again. The three-SCM-failure case sleeps 150 seconds for SCM stale marking before checking states.

State and persistence behavior: blockade network topology and datanode container metadata are the main state. The test intentionally observes divergent local replica state while partitions exist.

Dependencies and integration points: imports `time`, logging, and `OzoneCluster`; uses `Container` methods from the cluster model.

Risks: long fixed sleep increases runtime and flake risk; assumes datanode ordering and three replicas; assertions encode specific current recovery semantics.

Test signals: one SCM-reachable isolated datanode should close, two SCM-isolated peers remain open; with no SCM connectivity all replicas remain open until restore; restore closes all.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_three_nodes_isolate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_two_nodes.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_two_nodes.py

Purpose: pytest scenarios where two datanodes have SCM communication failures, either in the same partition or different partitions.

Important APIs/types/functions: `test_two_dns_isolate_scm_same_partition` and `test_two_dns_isolate_scm_different_partition`.

Control flow: after Freon seeding, tests construct two or three blockade partitions, run Freon during failure, select containers from the datanode expected to have authoritative state, wait until a replica is quasi-closed or not open, assert accepted state combinations, restore network, wait for all closed, and verify Freon success.

State and persistence behavior: external network partitions and datanode on-disk container files. No durable test-local state.

Dependencies and integration points: uses `OzoneCluster` and its `Container` wrappers.

Risks: expected alternatives in the different-partition case show nondeterministic outcomes; direct string state comparisons can hide future state additions; no explicit cleanup if mid-test assertion fails beyond teardown.

Test signals: verifies same-partition SCM failures produce one quasi-closed and two open replicas; different partitions allow either all closed for connected replicas or open/quasi-closed combination before final closure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_mixed_failure_two_nodes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_scm_isolation.py -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_scm_isolation.py

Purpose: pytest coverage for datanodes that can communicate with peers but not SCM.

Important APIs/types/functions: `test_scm_isolation_one_node` and `test_scm_isolation_two_node`.

Control flow: tests seed data, partition a subset of datanodes away from SCM, run Freon during the partition, fetch containers from a SCM-connected datanode, wait for two closed replicas or a non-open state, assert the allowed states, restore network, wait for all closed, and run Freon again.

State and persistence behavior: uses blockade network partition state and reads Ozone container state from datanode disk metadata.

Dependencies and integration points: imports `OzoneCluster`; uses `OzoneClient.run_freon` and `Container` polling helpers.

Risks: the two-node expectation permits either quasi-closed/open or closed/closed outcomes, indicating timing or algorithm sensitivity; fixed polling windows may be insufficient under slow CI.

Test signals: confirms SCM isolation does not prevent the connected majority from closing replicas and that all replicas converge to closed after healing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/test_blockade_scm_isolation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/compose/docker-compose.yaml -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/compose/docker-compose.yaml

Purpose: docker-compose topology for Ozone network fault-injection tests.

Important APIs/types/functions: defines services `datanode`, `om`, `scm`, and `ozone_client`. Each uses `${docker.image}` and `./docker-config`. Commands are `/opt/hadoop/bin/ozone datanode`, `om`, `scm`, while `ozone_client` runs `tail -f /etc/passwd` as an idle command target for `docker exec`.

Control flow: `OzoneCluster.start` invokes docker-compose with `--scale datanode=<count>`, then adds all service containers to blockade. `om` and `scm` use `ENSURE_*_INITIALIZED` environment variables to wait for metadata version files.

State and persistence behavior: compose creates runtime containers and Ozone metadata/data volumes inside them according to image defaults and `docker-config`.

Dependencies and integration points: consumed by Maven/network test harness through `MAVEN_TEST` or by local `OzoneCluster.Configuration`.

Risks: compose version 3 and unpinned exposed ports can conflict with local environments; client service is intentionally long-running but not an Ozone daemon; `${docker.image}` must be supplied.

Test signals: if this topology fails, all blockade tests fail before partition logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/compose/docker-compose.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/pom.xml -->
## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/pom.xml

Purpose: Maven aggregator for Apache Ozone fault-injection test modules.

Important APIs/types/functions: POM inherits from root `org.apache.ozone:ozone:2.3.0-SNAPSHOT`, has artifactId `ozone-fault-injection-test`, packaging `pom`, and declares modules `mini-chaos-tests` and `network-tests`.

Control flow: Maven builds this as an aggregator; module ordering lets the reactor include both fault-injection suites under the parent.

State and persistence behavior: no runtime state; build metadata only.

Dependencies and integration points: root Ozone parent supplies versions, plugins, and profiles. The network tests module contains the blockade tests researched in this group.

Risks: aggregator has no direct dependencies or plugin overrides, so parent POM changes can alter behavior. Module paths must remain accurate.

Test signals: `mvn` reactor selection or parent build should include both modules; missing module directories would fail project loading.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/dev-support/findbugsExcludeFile.xml -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude filter for the Freon module.

Important APIs/types/functions: root element `<FindBugsFilter>` is empty, meaning no Freon-specific bug patterns are excluded.

Control flow: referenced by `freon/pom.xml` in the `spotbugs-maven-plugin` configuration as `${basedir}/dev-support/findbugsExcludeFile.xml`.

State and persistence behavior: build-time static configuration only.

Dependencies and integration points: integrates with Maven SpotBugs plugin.

Risks: an empty filter is explicit but may surprise maintainers expecting suppressions; any future suppression should be narrowly scoped to avoid hiding Freon command defects.

Test signals: SpotBugs should analyze Freon without module-local exclusions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/pom.xml -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/pom.xml

Purpose: Maven build definition for the `ozone-freon` jar, Ozone's load generator and performance test CLI.

Important APIs/types/functions: declares dependencies on AWS S3 SDK, Jackson, Guava, commons-codec/io/lang3, picocli, metrics, OpenTelemetry, Hadoop common, HDDS/Ozone client/common/interface modules, Ratis, SLF4J, and metainf-services. Build plugins configure SpotBugs, compiler annotation processors, and an enforcer override for selected banned annotation imports.

Control flow: annotation processors generate `@MetaInfServices` service registrations for Freon subcommands and picocli GraalVM native-image metadata during compile. SpotBugs uses the empty exclude file. Enforcer allows this module to use the selected annotation processors while still banning Ozone config/request-validation annotations.

State and persistence behavior: build metadata only; generated service/native config artifacts are compile outputs.

Dependencies and integration points: Freon commands depend on Ozone client APIs, OM/SCM protocols, Hadoop FS, datanode container protocols, metrics, tracing, and picocli.

Risks: broad dependency surface can create classpath and shading conflicts; annotation processor configuration is required for subcommand discovery; runtime SLF4J reload4j dependency affects logging behavior.

Test signals: compilation should generate service entries for all `@MetaInfServices(FreonSubcommand.class)` commands; SpotBugs and enforcer should pass.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/AbstractOmBucketReadWriteOps.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/AbstractOmBucketReadWriteOps.java

Purpose: shared base for Freon workloads that create/list/read and write Ozone bucket paths via either Hadoop FS or Ozone bucket APIs.

Important APIs/types/functions: extends `BaseFreonGenerator` and implements `Callable<Void>`. Abstract hooks: `display`, `initialize`, `createPath`, `getReadCount`, and `create`. Concrete workflow includes `readOperations`, `writeOperations`, `create`, and `getSizeInBytes`. Picocli options configure object size, buffer size, random name length, total thread count, read-thread percentage, read operation count, and write operation count.

Control flow: `call` initializes Freon, computes read/write thread counts, prints configuration, builds `ContentGenerator` and metrics timer, then delegates to subclass `initialize`. `readOperations` precreates objects under a read path and runs concurrent list/read-count tasks. `writeOperations` creates a write path and concurrently writes batches. `create` writes random-named objects using subclass output streams.

State and persistence behavior: local state includes timers, content generator, and thread counts. Persistent effects are Ozone keys/files created in subclass storage backends.

Dependencies and integration points: used by `OmBucketReadWriteFileOps` and `OmBucketReadWriteKeyOps`; depends on Dropwizard metrics, Hadoop `StorageSize`, Ozone path constants, and `ContentGenerator`.

Risks: nested executors inside `runTests` can create high thread counts; read/write services are shutdown but not awaited after shutdown beyond completion-service takes; IOExceptions in worker tasks are logged and converted to partial counts instead of failing.

Test signals: validate subclasses with small read/write counts and assert created object counts and metrics timer increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/AbstractOmBucketReadWriteOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/BaseFreonGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/BaseFreonGenerator.java

Purpose: core execution framework for Freon subcommands: common CLI options, threading, metrics, tracing, progress, naming, Ozone client creation, and helper utilities.

Important APIs/types/functions: options include `--number-of-tests`, `--threads`, `--duration`, `--fail-at-end`, and `--prefix`. Key methods are `init`, `runTests`, `runTaskLoop`, `tryNextTask`, `printReport`, `printOption`, `createOmClient`, `createStorageContainerLocationClient`, `findPipelineForTest`, `generateObjectName`, `generateBucketName`, `ensureVolumeAndBucketExist`, `ensureVolumeExists`, digest helpers, `allowEmptyPrefix`, `allowDuration`, `realTimeStatusSupplier`, and `TaskProvider`.

Control flow: subcommands call `init`, then `runTests(provider)`. `init` starts optional Freon HTTP server, sets counters, resolves or randomizes prefix, parses duration, registers shutdown hooks, creates executor/progress bar, and records start time. `runTests` sets the span name, starts fixed-thread runners, waits until count/duration/failure completion, shuts down progress and executor, and throws if failures occurred.

State and persistence behavior: local atomic counters track attempts/success/failure/completion; `ThreadLocal` stores thread sequence IDs. Persistent effects are delegated to task providers. Shutdown hook prints metrics and stops HTTP server.

Dependencies and integration points: parent `Freon` command, Ozone/OM/SCM clients, HA utils, Dropwizard metrics, OpenTelemetry tracing, picocli, Hadoop RPC/security.

Risks: `counter % testNo` is used even for duration mode, so `testNo` must remain positive; failure handling logs and increments counters but only throws at end; thread-local sequence removal in main shutdown does not remove worker locals; shutdown hooks can print reports even during partial initialization.

Test signals: unit tests should cover prefix resolution, duration validation, failure counting, fail-at-end behavior, pipeline selection, and volume/bucket creation idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/BaseFreonGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ContentGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ContentGenerator.java

Purpose: reusable random content writer for Freon key/file workloads.

Important APIs/types/functions: constructors accept key size, buffer size, copy buffer size, and optional `SyncOptions` (`NONE`, `HFLUSH`, `HSYNC`). `write(OutputStream)` writes repeated slices of a preallocated random ASCII buffer and optionally hflush/hsyncs after each write. `write(OzoneDataStreamOutput)` writes `ByteBuffer` slices and closes the stream. `getBuffer` is visible for tests.

Control flow: for each remaining byte range, choose `curSize`, then either write one byte at a time if `copyBufferSize == 1` or write chunks of `copyBufferSize`. Sync options only apply when the stream implements Hadoop `Syncable`.

State and persistence behavior: stores immutable random buffer and sizes. Persistent output is written to supplied streams; streaming Ozone output is closed by this class.

Dependencies and integration points: used across Freon generators for key/file/chunk content. Depends on commons-lang3 random strings, Hadoop `Syncable`, and Ozone streaming output.

Risks: buffer and copy sizes are not validated against zero/negative values here; closing only the `OzoneDataStreamOutput` overload creates different ownership semantics than `OutputStream`; random ASCII is not cryptographically required.

Test signals: `TestContentGenerator` likely covers generated byte counts, buffer reuse, copy size behavior, and stream write paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ContentGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DNRPCLoadGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DNRPCLoadGenerator.java

Purpose: Freon subcommand `dn-echo`/`dne` for generating datanode echo RPC load against the datanodes associated with a container.

Important APIs/types/functions: extends `BaseFreonGenerator`, implements `Callable<Void>`. Options cover request/response payload KB, container ID, datanode sleep time, number of Xceiver clients, read-only flag, and Ratis vs gRPC mode. Main task is `sendRPCReq`.

Control flow: `call` validates payload sizes, gets config, fetches container info and matching pipeline from SCM, switches non-Ratis mode to read-only and `copyForRead`, gets a container token, creates secure or insecure `XceiverClientCreator`, acquires `numClients`, initializes Freon, generates protobuf payload, computes response size, runs tests, then closes OM, Xceiver clients, factory, and SCM client.

State and persistence behavior: no Ozone metadata mutation unless Ratis/write mode is requested by the underlying echo call. Local state stores clients, payload bytes, timer, and token.

Dependencies and integration points: uses SCM `ContainerOperationClient`, `ContainerProtocolCalls.echo`, Xceiver clients, Ozone security, OM service info for CA certificates, and payload utilities.

Risks: container ID must exist; response payload calculation clamps to `MAX_SIZE_KB` bytes despite name in KB; non-Ratis mode mutates `readOnly`; client release occurs after direct close paths need careful handling.

Test signals: validate payload validation, secure/insecure client setup, client index distribution, and echo RPC success against a test container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DNRPCLoadGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeBlockPutter.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeBlockPutter.java

Purpose: Freon subcommand `dbp`/`datanode-block-putter` that issues raw `PutBlock` datanode commands with fake chunk metadata to a Ratis/THREE pipeline.

Important APIs/types/functions: options include chunks per block, fake chunk size, and optional pipeline ID. `call` sets up clients and checksum data; `putBlock` builds `DatanodeBlockID`, `BlockData`, chunk list, and `ContainerCommandRequestProto`.

Control flow: initialize Freon, reject secure clusters, create SCM client, find pipeline, acquire Xceiver client, generate random data and CRC32 checksum protobuf, then run `putBlock` tasks. Each task uses container ID `1L`, local ID and BCSID from task number, and sends a `PutBlock` command timed by metrics.

State and persistence behavior: mutates datanode/Ratis metadata by committing fake block records for container 1; chunks do not actually exist. Local state is client, timer, and checksum protobuf.

Dependencies and integration points: direct HDDS datanode protocol protobufs, SCM pipeline lookup, Xceiver client, Ozone security check, and `BaseFreonGenerator.findPipelineForTest`.

Risks: unsupported in secure environments; hard-coded container ID 1 and fake chunks can fail if the container is absent or validation changes; fake metadata can pollute test clusters.

Test signals: useful for stress testing datanode block metadata path and measuring `put-block` timer counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeBlockPutter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkGenerator.java

Purpose: Freon subcommand `dcg`/`datanode-chunk-generator` that writes raw chunks through Xceiver clients to one or more datanode pipelines.

Important APIs/types/functions: options include async mode, chunk size, pipeline IDs, and datanode host filters. Methods include `call`, `pipelineContainsDatanode`, `arePipelinesOrDatanodesProvided`, `runTest`, `writeChunk`, and `sendWriteChunkRequest`.

Control flow: reject secure clusters, parse comma-separated pipeline/datanode selectors, list SCM pipelines, initialize Freon, choose default first factor-three pipeline or selected pipelines containing IDs/hosts, acquire clients, prepare random payload and CRC32 checksum, then run write tasks. Each task uses container ID 1, local ID `stepNo % 20`, offset `(stepNo / 20) * chunkSize`, and sends sync or async `WriteChunk`, waiting for commit in async mode.

State and persistence behavior: writes chunk data into datanode container storage for fake block IDs. Local state stores Xceiver clients, payload, checksum, and timer.

Dependencies and integration points: SCM pipeline list, Xceiver client, datanode protobufs, checksum utilities.

Risks: selector loop only iterates `pipelinesFromCmd`, so datanode-only selection with an empty pipeline string depends on filtering behavior; hard-coded container 1; unsupported in secure clusters; async commit wait can block.

Test signals: paired with `DatanodeChunkValidator`; chunk-write metrics and successful raw reads validate behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkValidator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkValidator.java

Purpose: Freon subcommand `dcv`/`datanode-chunk-validator` that reads chunks generated by `DatanodeChunkGenerator` and verifies checksums against chunk zero.

Important APIs/types/functions: options include pipeline ID and chunk size. Core methods are `call`, `readReference`, `validateChunk`, `createReadChunkRequest`, and `computeChecksum`.

Control flow: initialize Freon, reject secure clusters, find pipeline, acquire read-data Xceiver client, create checksum metadata, read reference chunk `stepNo=0`, start timer, then run validation tasks. Each task builds a `ReadChunk` request using the same naming/local-ID/offset scheme as the generator, reads the chunk, computes checksum, and compares to reference.

State and persistence behavior: read-only against datanode storage. Local state includes Xceiver client, checksum algorithm, reference checksum, and timer.

Dependencies and integration points: depends on chunks written by `DatanodeChunkGenerator`, SCM pipeline lookup, Xceiver read client, Ozone checksum APIs.

Risks: IOExceptions during individual validation are logged but not rethrown, which may hide read failures; hard-coded container ID/local ID scheme must stay aligned with generator; unsupported in secure environments.

Test signals: checksum mismatch throws; successful run indicates chunk content consistency across generated chunks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FollowerReader.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FollowerReader.java

Purpose: Freon subcommand `fr`/`follower-reader` that repeatedly reads metadata size of the same key through multiple Ozone clients, intended to test OM follower/read performance.

Important APIs/types/functions: options configure volume, bucket, and key. `call` creates one `OzoneClient` per Freon thread and runs `readKeySize`; `readKeySize` selects a client by counter and calls `getKey(keyName).getDataSize()`.

Control flow: initialize Freon, create Ozone configuration, allocate clients, create timer, and run threaded tasks. Each task is timed under `follower-read`.

State and persistence behavior: read-only Ozone metadata calls; local state is the client list and timer.

Dependencies and integration points: uses `BaseFreonGenerator.createOzoneClient` and Ozone object store APIs.

Risks: clients are not closed in `call`, creating a resource leak in long runs; `omServiceID` is a private field fixed to null with no CLI option; target key must already exist.

Test signals: useful for measuring key metadata read throughput; should be paired with pre-created volume/bucket/key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FollowerReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/Freon.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/Freon.java

Purpose: top-level `ozone freon` CLI command and extensible parent for all Freon subcommands.

Important APIs/types/functions: extends `GenericCli` and implements `ExtensibleParentCommand`. `execute` initializes metrics/tracing and delegates to picocli. `subcommandType` returns `FreonSubcommand`. `startHttpServer` and `stopHttpServer` manage optional internal HTTP server. `main` runs the command. `isInteractive` reports console presence.

Control flow: command execution captures `OzoneConfiguration`, initializes metrics as `ozone-freon`, wraps the full command in a tracing span, then lets `GenericCli` discover and run registered subcommands. Subcommands call `BaseFreonGenerator.init`, which may call `startHttpServer`.

State and persistence behavior: holds configuration, optional `FreonHttpServer`, and an immutable interactive flag. Persistent effects are delegated to subcommands.

Dependencies and integration points: picocli, HDDS CLI framework, metrics, OpenTelemetry tracing, `FreonSubcommand` service discovery.

Risks: HTTP server startup errors are logged but non-fatal; `interactive` is computed once from `System.console`; tracing span name includes raw argv.

Test signals: CLI should discover `@MetaInfServices` subcommands and initialize metrics/tracing before command execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/Freon.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonHttpServer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonHttpServer.java

Purpose: HTTP/HTTPS server wrapper for Freon metrics and profiling endpoints.

Important APIs/types/functions: extends `BaseHttpServer`. Overrides configuration key accessors for HTTP/HTTPS addresses, bind hosts, default ports, Kerberos keytab/principal, enabled key, auth type, and auth config prefix.

Control flow: constructed by `Freon.startHttpServer(conf)` when `--server` is enabled. Base class owns actual server lifecycle.

State and persistence behavior: no independent state beyond base HTTP server internals. Runtime effects are listening sockets and metrics/profile endpoints.

Dependencies and integration points: uses `MutableConfigurationSource`, HDDS `BaseHttpServer`, and Freon-specific keys from `OzoneConfigKeys`.

Risks: config-key correctness is critical; bad bind address or Kerberos settings cause startup failures that Freon logs but does not propagate.

Test signals: with `--server`, Freon should bind using `ozone.freon.*` HTTP config defaults and expose base endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonReplicationOptions.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonReplicationOptions.java

Purpose: Freon-specific replication CLI mixin that extends shell `ReplicationOptions` and preserves legacy `--factor` support.

Important APIs/types/functions: options include deprecated `-F/--factor`, `--type/--replication-type`, and `--replication/-r`. Overrides setters and `fromParams(ConfigurationSource)`.

Control flow: when picocli parse result matched `--factor`, `fromParams` returns a RATIS replication config with the provided factor; otherwise it delegates to the generic replication options parser.

State and persistence behavior: stores parsed factor and picocli `CommandSpec`; no persistence.

Dependencies and integration points: used as `@Mixin` by key/file creation Freon commands. Depends on HDDS replication config classes and Ozone shell replication parsing.

Risks: legacy `--factor` forces RATIS regardless of other type options; precedence depends on picocli parse-result availability; default factor THREE may silently apply when `--factor` is matched without a value.

Test signals: parse combinations for `--replication`, `--type`, and `--factor`, including legacy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonReplicationOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonS3TraceContextRequestHandler.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonS3TraceContextRequestHandler.java

Purpose: AWS SDK request handler that injects W3C trace context headers into outgoing S3 requests from Freon.

Important APIs/types/functions: extends `RequestHandler2` and overrides `beforeRequest(Request<?>)`.

Control flow: before an AWS SDK request is sent, checks whether the current OpenTelemetry span context is valid. If valid, uses `W3CTraceContextPropagator.inject` with the request as carrier and `addHeader` as setter.

State and persistence behavior: stateless. It mutates outgoing request headers only.

Dependencies and integration points: integrates AWS Java SDK request handling with OpenTelemetry tracing. Intended for Freon S3 workloads so S3 Gateway spans can attach to Freon task spans.

Risks: no-op without active valid span; assumes AWS request headers preserve W3C trace fields; adding duplicate headers depends on AWS SDK request behavior.

Test signals: unit/integration tests can install the handler under an active span and assert `traceparent` header propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonS3TraceContextRequestHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonSubcommand.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonSubcommand.java

Purpose: marker interface for commands registered under `ozone freon`.

Important APIs/types/functions: empty interface `FreonSubcommand`.

Control flow: `Freon.subcommandType()` returns this marker; classes annotated with `@MetaInfServices(FreonSubcommand.class)` are discoverable as extensible subcommands.

State and persistence behavior: no state.

Dependencies and integration points: used by Freon command classes and metainf-services annotation processor configured in `freon/pom.xml`.

Risks: subcommands missing the marker or service annotation will not be discovered; no compile-time method contract beyond marker identity.

Test signals: service loader/picocli discovery should include all annotated subcommands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FreonSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopBaseFreonGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopBaseFreonGenerator.java

Purpose: base class for Freon commands that operate through Hadoop `FileSystem`.

Important APIs/types/functions: option `--rpath/--path` sets a root Hadoop FS URI, default `o3fs://bucket1.vol1`. `init` captures Ozone configuration, parses URI, disables FS cache for the scheme, and delegates to base init. `getFileSystem` returns a thread-local FileSystem. `taskLoopCompleted` closes the thread-local FS.

Control flow: subclasses call `super.init`, then use `getRootPath` and `getFileSystem` in task providers. Each Freon worker thread lazily gets its own FileSystem instance.

State and persistence behavior: thread-local FileSystem clients and configuration are local. Persistent effects are filesystem operations performed by subclasses.

Dependencies and integration points: base for `HadoopFsGenerator`, `HadoopFsValidator`, `HadoopNestedDirGenerator`, and `HadoopDirTreeGenerator`.

Risks: `taskLoopCompleted` only closes the FileSystem for threads that reached it; `ThreadLocal` is not removed; disabling cache mutates local config and may surprise callers sharing it.

Test signals: verify per-thread FS creation, cache-disable key, and FS close after task loop.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopBaseFreonGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopDirTreeGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopDirTreeGenerator.java

Purpose: Freon subcommand `dtsg`/`dfs-tree-generator` that creates a recursive directory tree and files through Hadoop FS.

Important APIs/types/functions: options configure depth, file count per directory, file size, buffer size, child span, and random name length. Methods include `call`, `createDir`, `createSubDirRecursively`, `makeDirWithGivenNumberOfFiles`, `createFile`, and `createFiles`.

Control flow: validates depth and span, initializes base FS, creates a `ContentGenerator`, starts timer, and runs `createDir` for each test. Each root creates one random directory with files, then recursively creates depth/span child directories, each populated with files.

State and persistence behavior: creates directories and files under the configured root path. Local `AtomicLong totalDirsCnt` and timer track counts.

Dependencies and integration points: extends `HadoopBaseFreonGenerator`, uses Hadoop `FileSystem`, `Path`, `FSDataOutputStream`, `ContentGenerator`, and metrics.

Risks: one Freon task can create many directories/files, so `--number-of-tests` multiplies quickly; random names make repeat cleanup harder; invalid options only print messages and return success.

Test signals: small depth/span/file-count runs should produce expected directory and file counts and timer increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopDirTreeGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsGenerator.java

Purpose: Freon subcommand `dfsg`/`dfs-file-generator` that creates random files through any Hadoop-compatible filesystem.

Important APIs/types/functions: options configure file size, content buffer size, copy-buffer size, and sync option (`NONE`, `HFLUSH`, `HSYNC`). `call` initializes FS and content generator; `createFile` writes each generated file.

Control flow: initialize base FS, create parent directory for object zero, build `ContentGenerator`, create timer, then run tests. Each task constructs `<root>/<prefix>/<counter>`, creates the file, writes generated content, and closes the stream.

State and persistence behavior: creates files under the configured root path. Local state is content generator and timer.

Dependencies and integration points: extends `HadoopBaseFreonGenerator`, uses Hadoop `FileSystem` and `FSDataOutputStream`.

Risks: static `flushOrSync` option is shared across instances in a JVM; parent directory is only proactively created for object zero but the path schema is shallow so this is enough by default; overwrite behavior depends on FS create semantics.

Test signals: pair with `HadoopFsValidator`; check file creation count and sync behavior on Syncable streams.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsValidator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsValidator.java

Purpose: Freon subcommand `dfsv`/`dfs-file-validator` that validates generated files have the same digest as the first file.

Important APIs/types/functions: `call` reads object zero's digest, starts a `file-read` timer, and runs `validateFile`. `validateFile` reads an entire file into a byte array and compares MD5 digest to the reference with `MessageDigest.isEqual`.

Control flow: initialize Hadoop FS, open `<root>/<object0>`, compute digest via `BaseFreonGenerator.getDigest(InputStream)`, then each task opens the generated path for its counter, reads bytes through `IOUtils.toByteArray`, computes digest, and throws on mismatch.

State and persistence behavior: read-only against Hadoop FS. Stores reference digest locally.

Dependencies and integration points: pairs with `HadoopFsGenerator`, extends `HadoopBaseFreonGenerator`, uses commons-io and Java digest comparison.

Risks: reads whole files into memory, so large validation objects can exhaust heap; assumes all generated files have identical content, which is true for a single `ContentGenerator` run but not necessarily across independent generator invocations.

Test signals: digest mismatch throws; missing file or read error is counted as Freon task failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopNestedDirGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopNestedDirGenerator.java

Purpose: Freon subcommand `ddsg`/`dfs-directory-generator` that creates nested directory paths through Hadoop FS.

Important APIs/types/functions: options configure depth, span of child directories under the leaf, and random name length. `call` validates options and runs `createDir`.

Control flow: for each task, generate a random path of `depth` segments, call `mkdirs` on the parent path, derive a leaf prefix, then create `span` sibling/child paths by appending numeric names and `/0`.

State and persistence behavior: creates directory metadata under the configured FS root. No file content is written.

Dependencies and integration points: extends `HadoopBaseFreonGenerator`, uses commons random strings and Hadoop `Path`.

Risks: string slicing for `leafDir` assumes name length and trailing segment layout; invalid depth/span prints and exits without failing; random paths are not reproducible.

Test signals: small depth/span run should create expected directory structure under the root path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopNestedDirGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HsyncGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HsyncGenerator.java

Purpose: Freon subcommand `hg`/`hsync-generator` that simulates HBase WAL-style writes plus concurrent `hsync` calls on a Hadoop FS file.

Important APIs/types/functions: options configure root path, bytes per write, and writes per transaction. `call` opens a file, starts a daemon transaction writer, and runs `sendHsync` tasks. Shared state includes `writtenTransactions` queue and `lastSyncedTransaction`.

Control flow: initialize Freon, get FS from URI, create `<root>/<object0>`, prepare payload, start writer thread. The writer loops forever, writing `writesPerTransaction` records and enqueueing transaction IDs. Freon worker tasks take transaction IDs and call `outputStream.hsync` only when the transaction is newer than the last synced value.

State and persistence behavior: writes to one persistent file and forces syncs. Local queue and atomic integer coordinate writer/sync threads.

Dependencies and integration points: uses Hadoop `FileSystem`/`FSDataOutputStream`, Ozone payload utilities, and `BaseFreonGenerator`.

Risks: daemon writer runs indefinitely until JVM exit and can throw unchecked exceptions; shared output stream is written and synced by different threads; queue backpressure can block writer; output stream is not protected by explicit synchronization.

Test signals: hsync timer count and generated file existence; stress runs reveal sync latency and concurrency issues.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HsyncGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/KeyGeneratorUtil.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/KeyGeneratorUtil.java

Purpose: utility for deterministic Freon key-name generation.

Important APIs/types/functions: constants `PURE_INDEX`, `MD5`, and `FILE_DIR_SEPARATOR`. Methods `generatePureIndexKeyName`, `pureIndexKeyNameFunc`, `generateMd5KeyName`, and `md5KeyNameFunc`.

Control flow: pure-index methods stringify numeric indexes. MD5 methods hash the decimal number string and return the first seven hex characters.

State and persistence behavior: stateless. Names influence persistent Ozone keys created by callers.

Dependencies and integration points: used by `OzoneClientKeyReadWriteListOps` and related key-range generators to choose contiguous or distributed key names.

Risks: seven-character MD5 prefix can collide for large ranges; pure index ordering differs from zero-padded ordering used by `OmMetadataGenerator`.

Test signals: deterministic name output for representative indexes and collision considerations for benchmark ranges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/KeyGeneratorUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketGenerator.java

Purpose: Freon subcommand `ombg`/`om-bucket-generator` that creates Ozone buckets directly through OM protocol.

Important APIs/types/functions: options configure volume and OM service ID. Overrides `allowDuration` to false. `call` ensures the volume exists and creates an OM client. `createBucket` builds `OmBucketInfo` with DISK storage and calls `createBucket`.

Control flow: initialize Freon, create Ozone client, ensure volume, create OM protocol translator, create timer, and run bucket creation tasks.

State and persistence behavior: persists Ozone bucket metadata under the target volume. Local state stores OM client and timer.

Dependencies and integration points: uses Ozone RPC client for volume existence and OM protocol for bucket creation.

Risks: duplicate bucket names fail unless previous runs use unique prefixes; duration disabled because repeated bucket namespace generation is count-based; OM client is manually closed in finally.

Test signals: bucket-create timer and resulting bucket count under the volume.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteFileOps.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteFileOps.java

Purpose: Freon subcommand `obrwf` that measures mixed file create/list behavior through Hadoop FS paths.

Important APIs/types/functions: extends `AbstractOmBucketReadWriteOps`. Options configure root path, number of files for read prepopulation, and number of files for write batches. Implements `display`, `initialize`, `mainMethod`, `createPath`, `getReadCount`, and `create`.

Control flow: base `call` prints shared config and invokes `initialize`. This command obtains a FileSystem for `rootPath`, then `runTests(mainMethod)`. Each main task runs inherited `readOperations` and `writeOperations`, prints total files read/written, and leaves TODO hooks for read/write lock metrics.

State and persistence behavior: creates directories/files under `rootPath/readPath` and `rootPath/writePath`. Local state holds a shared `FileSystem`.

Dependencies and integration points: Hadoop FS, `AbstractOmBucketReadWriteOps`, Ozone path constants.

Risks: shared FileSystem is used by nested read/write thread pools; no explicit close of `fileSystem`; `createPath` calls `mkdirs` during each list, which adds metadata writes to read workload.

Test signals: count files returned by `listStatus` and created files under write path; metrics timer is inherited.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteFileOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteKeyOps.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteKeyOps.java

Purpose: Freon subcommand `obrwk` that measures mixed key create/list behavior through Ozone bucket APIs.

Important APIs/types/functions: extends `AbstractOmBucketReadWriteOps`. Options configure volume, bucket, read/write key counts, OM service ID, and replication mixin. Implements `display`, `initialize`, `mainMethod`, `createPath`, `getReadCount`, and `create`.

Control flow: base `call` initializes shared workload config, then `initialize` resolves replication, ensures target volume/bucket, obtains `OzoneBucket`, and runs `mainMethod`. Each main task precreates/list-reads keys under `/readPath`, writes batches under `/writePath`, and prints totals.

State and persistence behavior: persists keys in the target Ozone bucket. Local state holds metadata map, replication config, and bucket handle.

Dependencies and integration points: Ozone client object store APIs, `FreonReplicationOptions`, inherited content writer and metrics.

Risks: `bucket` is used by concurrent nested threads and must be thread-safe; list path includes leading/trailing OM separators; repeated runs can accumulate random keys and affect list counts.

Test signals: listStatus result size, created key count, and `om-bucket-read-write-ops` timer values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteKeyOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketRemover.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketRemover.java

Purpose: Freon subcommand `ombr`/`om-bucket-remover` that deletes generated Ozone buckets through OM protocol.

Important APIs/types/functions: options configure volume and OM service ID. `call` creates OM client and runs `removeBucket`; `removeBucket` calls `deleteBucket(volumeName, generateBucketName(index))`.

Control flow: initialize Freon, create Ozone configuration, create OM client, start `bucket-remove` timer, run tests, close OM client.

State and persistence behavior: deletes bucket metadata from the target volume. Local state stores OM client and timer.

Dependencies and integration points: intended to clean up or benchmark buckets created by `OmBucketGenerator`.

Risks: delete fails for non-empty or missing buckets; unlike generator it does not ensure volume existence; failures stop early unless `--fail-at-end` is set.

Test signals: bucket-remove timer, absent buckets after run, and expected failures for non-empty buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketRemover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmKeyGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmKeyGenerator.java

Purpose: Freon subcommand `omkg`/`om-key-generator` that creates key metadata directly in OM without writing data blocks.

Important APIs/types/functions: options configure volume, bucket, replication, and OM service ID. `call` ensures volume/bucket and creates OM client. `createKey` builds `OmKeyArgs`, opens a key, then commits it.

Control flow: initialize Freon, parse replication, ensure bucket via Ozone client, create OM protocol client, create `key-create` timer, and run tasks. Each task uses current user ACLs, empty location info, generated key name, and optional replication config.

State and persistence behavior: creates OM key metadata entries with no block locations. Local state stores OM client, timer, and replication config.

Dependencies and integration points: Ozone OM protocol, Ozone ACL utilities, user group information, `FreonReplicationOptions`.

Risks: keys without location info are synthetic and may not behave like fully written keys; duplicate names fail; current user/ACL behavior depends on security config.

Test signals: OM metadata key counts and timer; lookup/list commands can consume generated keys for metadata-only benchmarks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmKeyGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmMetadataGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmMetadataGenerator.java

Purpose: Freon subcommand `ommg`/`om-metadata-generator` for broad OM metadata operation benchmarking: create/read/list keys and files, bucket/volume info, and mixed workloads.

Important APIs/types/functions: options configure volume, bucket, data size, buffer, list batch size, random access, operation enum, mixed operation lists/counts, client count, OM service ID, follower-read affinity, and replication. Key methods include `call`, `initMixedOperation`, `getUsage`, `createKeyArgsBuilder`, `realTimeStatusSupplier`, `applyOperation`, `performWriteOperation`, `performReadOperation`, `getOMFollowerNodeIds`, and `changeInitialProxyForFollowerRead`.

Control flow: if `--ophelp` or missing operation, prints usage. MIXED maps thread sequence IDs to operation enum values based on `--ops`/`--opsnum`. It initializes Freon, creates content generator and per-thread key args builder, ensures target bucket, creates multiple Ozone clients, optionally points clients at OM followers, then runs `applyOperation`. The operation switch performs create/read/lookup/list/info actions via `ClientProtocol` or `OzoneManagerProtocol`, timing each operation name separately.

State and persistence behavior: creates keys/files when using create operations; read/list/info operations are read-only. Local state includes client array, thread-local args builders, operation mapping, timers, and replication config.

Dependencies and integration points: Ozone client protocol, OM protocol, HA follower-read failover transport, Dropwizard metrics, content generation, replication mixin.

Risks: read/list operations require pre-existing sufficient objects; `randomOp` can create/read the same key concurrently; follower affinity only supports `Hadoop3OmTransport`; mixed operation mutates the instance `operation` field from worker threads, which is a concurrency hazard.

Test signals: operation-specific timers, rate display, validation that list operations throw when there are not enough objects, and integration coverage for follower-read affinity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmMetadataGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmRPCLoadGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmRPCLoadGenerator.java

Purpose: Freon subcommand `om-echo`/`ome` that generates OM echo RPC load with configurable request/response payloads.

Important APIs/types/functions: options include request payload KB, response payload KB, number of clients, and `--ratis` to write to Ratis log. `call` creates OM protocol clients, generates payload, and runs `sendRPCReq`.

Control flow: validate nonnegative payload sizes, create `clientsCount` OM clients, initialize Freon, generate byte payload, set response size, create timer, run tasks, and close all clients.

State and persistence behavior: read-only echo by default; with `--ratis`, echo requests write through Ratis as implemented by OM. Local state is client array, payload, response size, and timer.

Dependencies and integration points: `BaseFreonGenerator.createOmClient`, Ozone OM protocol translator, payload utilities, metrics.

Risks: no upper bound enforcement despite help text mentioning max; payload size multiplication can overflow for very large integers; client count less than one is not normalized here.

Test signals: RPC success, payload handling, timer counts, and cleanup of clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmRPCLoadGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientCreator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientCreator.java

Purpose: Freon subcommand `occ`/`ozone-client-creator` that measures client creation and close overhead.

Important APIs/types/functions: option `--om-service-id`; `call` initializes Freon, stores config, creates `client-create` timer, and runs `createClient`; `createClientSafely` creates and immediately closes an Ozone RPC client.

Control flow: each task times a client create/close cycle. Exceptions are wrapped in `RuntimeException` so BaseFreonGenerator counts failures.

State and persistence behavior: no Ozone metadata persistence; local state is config and timer.

Dependencies and integration points: `BaseFreonGenerator.createOzoneClient`, Ozone client factory.

Risks: high counts can create connection churn against OM; wrapped exceptions lose checked exception type; no extra validation of OM service ID.

Test signals: timer count should match success count; resource leaks show as open connections/threads after run.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyGenerator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyGenerator.java

Purpose: Freon subcommand `ockg`/`ozone-client-key-generator` that writes full Ozone keys through the client API, optionally using Ratis streaming.

Important APIs/types/functions: options configure volume, bucket, key size, buffer size, OM service ID, replication, and `--enable-streaming/--stream`. Methods include `call`, `createKey`, `createKeyWithData`, and `createStreamKey`.

Control flow: initialize Freon, create content generator and metadata map, resolve replication config, ensure target bucket, obtain `OzoneBucket`, set `key-create` timer, and choose normal or stream task provider. Normal writes create a key output stream and write content inside tracing spans. Streaming writes force RATIS/THREE replication config and use `createStreamKey`.

State and persistence behavior: creates Ozone keys and writes data bytes. Local state includes bucket handle, content generator, metadata, timer, and replication config.

Dependencies and integration points: Ozone client object store, Ozone streaming output, tracing, `FreonReplicationOptions`, `ContentGenerator`.

Risks: streaming ignores user replication options and forces RATIS THREE; generated content is repeated from one buffer; duplicate key names fail unless prefix changes.

Test signals: pair with `OzoneClientKeyValidator`; assert key-create timer and readable generated keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyReadWriteListOps.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyReadWriteListOps.java

Purpose: Freon subcommand `ockrw` that mixes read, write, and list operations over a bounded key range from multiple Ozone clients.

Important APIs/types/functions: options configure volume, bucket, metadata-only reads, start index, range, object size, contiguous vs MD5 key naming, linear vs random selection, read/list percentages, max list result, and OM service ID. Methods include `call`, `readWriteListKeys`, `processReadTasks`, `processWriteTasks`, `processListTasks`, `decideReadWriteOrListTask`, and `getKeyName`. Enum `TaskType` has read/write/list.

Control flow: initialize Freon, create one Ozone client per Freon thread, ensure target bucket, prepare random key content, initialize `KeyGeneratorUtil`, and run tasks. Each task selects a client by counter, chooses task type by random percentage, chooses key name either linearly or randomly in range, and performs read, write, or list through client proxy.

State and persistence behavior: writes keys and reads/lists existing keys in the target bucket. Static `NEXT_NUMBER` coordinates linear key selection across instances in the JVM.

Dependencies and integration points: Ozone client proxy, `KeyGeneratorUtil`, commons IO/random, metrics.

Risks: percentage values are not bounded to 0-100; static linear counter persists across runs; MD5 seven-character names can collide; metadata-only read still requires key existence.

Test signals: distribution of task types, key naming mode, successful read/write/list against prepared ranges, and client cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyReadWriteListOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyRemover.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyRemover.java

Purpose: Freon subcommand `ockr`/`ozone-client-key-remover` that deletes generated keys through the Ozone client API.

Important APIs/types/functions: options configure volume, bucket, and OM service ID. `call` obtains target `OzoneBucket`, creates `remove` timer, and runs `removeKey`; `removeKey` deletes `generateObjectName(counter)`.

Control flow: initialize Freon, create Ozone client, get volume/bucket, run timed deletes, close client through try-with-resources.

State and persistence behavior: deletes Ozone key metadata/data references in the target bucket. Local state stores bucket handle and timer.

Dependencies and integration points: paired with `OzoneClientKeyGenerator`; uses Ozone object store APIs.

Risks: fails on missing keys; does not ensure bucket existence; delete semantics may be asynchronous with respect to physical block cleanup.

Test signals: removed keys should no longer be readable/listed; timer count should match deletes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyRemover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyValidator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyValidator.java

Purpose: Freon subcommand `ockv`/`ozone-client-key-validator` that verifies generated Ozone keys have the same digest as key zero.

Important APIs/types/functions: options configure volume, bucket, stream digest mode, and OM service ID. Methods include `call`, `readReference`, `getKeySize`, `validateKey`, `getDigest(String)`, `calculateDigestStreaming`, `readKeyToByteArray`, `readKey`, and `validateDigest`.

Control flow: initialize Freon, create Ozone client, read reference digest from object zero. If non-stream mode and key size exceeds byte-array capacity, switch to streaming. Then run validation tasks: read each key by generated name, calculate digest either during stream read or after loading to byte array, compare with reference, and close client.

State and persistence behavior: read-only against Ozone keys. Local state stores reference digest, reference key size, timer, stream mode, and client.

Dependencies and integration points: pairs with `OzoneClientKeyGenerator`, uses `BaseFreonGenerator.getDigest`, commons IO, and Ratis checked function.

Risks: non-stream mode reads whole keys into memory; generated keys must share identical content and size; client close is not in finally if validation throws.

Test signals: digest mismatch throws; large key path should force streaming; successful validation confirms readable generated data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/PathSchema.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/PathSchema.java

Purpose: simple Freon path-name generator used by `BaseFreonGenerator.generateObjectName`.

Important APIs/types/functions: constructor stores a prefix; `getPath(long counter)` returns `prefix + "/" + counter`.

Control flow: no branching. Base Freon initializes one schema per command after prefix resolution.

State and persistence behavior: stores prefix. Generated names become persistent key/file paths in many Freon workloads.

Dependencies and integration points: used by `BaseFreonGenerator`.

Risks: empty prefix produces names like `/0`, which some commands intentionally allow but others avoid through random prefix generation; no zero-padding, so lexicographic order differs from numeric order.

Test signals: prefix and counter mapping should be deterministic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/PathSchema.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ProgressBar.java -->
## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ProgressBar.java

Purpose: background progress reporter for Freon command execution.

Important APIs/types/functions: constructors accept output stream, max value, current value supplier, interactive flag, and real-time message supplier. Public methods: `start`, `shutdown`, `terminate`, and `print`. Internal methods render interactive or log-style progress.

Control flow: `start` launches one thread. The thread prints an initial line, loops once per second while running and current value is below max, prints current progress, then prints final state and marks stopped. `shutdown` waits for natural completion; `terminate` stops early. Interactive mode renders carriage-return progress bar; noninteractive mode logs percentage.

State and persistence behavior: volatile `running` and `startTime`; no persistence. Output goes to `PrintStream` or logger.

Dependencies and integration points: created by `BaseFreonGenerator.init`; real-time supplier can include command-specific rates such as `OmMetadataGenerator`.

Risks: percent divides by `maxValue`; max should be positive. Interactive bar uses block characters and width proportional to percent; log mode can emit repeated progress logs. `Thread` cannot be restarted after termination.

Test signals: `TestProgressBar` likely checks lifecycle and output behavior for interactive/noninteractive modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ProgressBar.java -->

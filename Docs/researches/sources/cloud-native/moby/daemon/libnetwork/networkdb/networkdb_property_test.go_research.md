## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_property_test.go

Purpose: slow property-based convergence test for NetworkDB. It randomly drives clusters through joins, leaves, creates, updates, deletes, and sleeps, then asserts eventual convergence to the union of expected owned entries across joined networks.

Important APIs/types/functions: `TestNetworkDBAlwaysConverges` runs `rapid.Check`; `testConvergence` builds 2-25 NetworkDB instances and 1-5 networks; `networkDBFSM` implements rapid state-machine actions; action methods include `JoinNetwork`, `LeaveNetwork`, `CreateEntry`, `UpdateEntry`, `DeleteEntry`, and `Sleep`.

Control flow: random actions mutate the model and real NetworkDB instances without stepwise assertions because the system is eventually consistent. After action generation finishes, the test computes expected per-node views, polls `WalkTable` and local network membership until actual state matches, logs mutation history, and records convergence time to `testdata/convergence_time.csv` when possible.

State and persistence behavior: model state is in `state []map[string]map[string]string`, tracking node-owned entries by network. `keysUsed` prevents immediate key reuse after deletion because replicas may not have observed tombstones yet. The test writes optional CSV timing data but treats failures to write statistics as non-fatal.

Dependencies and integration points: uses `pgregory.net/rapid`, `gotest.tools/v3/poll`, `google/go-cmp/cmp`, and helper constructors from `networkdb_test.go`. It depends on real NetworkDB clustering and gossip, not mocks.

Risks: marked `slowtests`, with up to 25 nodes and a 5-minute convergence timeout, so it is expensive and environment-sensitive. Random action traces can be noisy; the mutation log and convergence CSV are important for diagnosing flakes. The model intentionally avoids key reuse, leaving some duplicate-key edge cases to targeted tests.

Test signals: strong signal for eventual consistency across broad operation sequences. It complements deterministic unit/integration tests by exploring interleavings and timing, especially convergence after network membership churn and table mutation races.

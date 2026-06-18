# sources/control-plane/rook/pkg/daemon/multus/resources_test.go

Purpose: tests the small `perNodeTypeCount` map helper used by the Multus validation state machine for expected pod counts per node type.

Important APIs/types/functions: `Test_perNodeTypeCount_Increment()`, `Test_perNodeTypeCount_Equal()`, and `Test_perNodeTypeCount_Total()` cover mutation, equality, and aggregate count behavior.

Control flow: each test table initializes a map pointer, calls the relevant method, and compares to expected maps or values. Equality tests cover empty maps, differing keys, matching keys with differing values, and multiple-key cases.

State and persistence behavior: purely in-memory tests. The methods mutate only the receiver map and do not interact with Kubernetes.

Dependencies and integration points: uses `testify/assert` for comparisons. The helper under test feeds image-puller stabilization, host-checker expectations, and client expected pod counts in `validation.go`.

Risks: tests do not cover nil map pointers or nil map values; current production paths initialize maps before use. The broader correctness of scheduled-count discovery is not covered here.

Test signals: good confidence in basic count math, but limited coverage of resource-listing functions that produce these counts.

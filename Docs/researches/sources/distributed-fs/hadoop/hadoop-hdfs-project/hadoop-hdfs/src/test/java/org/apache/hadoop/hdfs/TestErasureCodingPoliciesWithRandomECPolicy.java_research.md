# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPoliciesWithRandomECPolicy.java

## Purpose
Runs the `TestErasureCodingPolicies` suite using a random non-default EC policy. This expands the policy semantics tests beyond the default policy and catches hidden assumptions about data/parity unit counts, cell sizes, and policy IDs.

## Important APIs and Types
Extends `TestErasureCodingPolicies` and overrides `getEcPolicy()`. Uses `StripedFileTestUtil.getRandomNonDefaultECPolicy()`, `ErasureCodingPolicy`, and logging.

## Control Flow
The constructor selects a random non-default policy and logs the superclass and policy name. All tests are inherited; the superclass setup consumes this policy to size the MiniDFSCluster and to drive policy assertions.

## State, Persistence, Dependencies, Integration
The only local state is the selected policy field. Persistence, permission, listing, file-level override, replicated override, and policy-manager behavior are inherited from the superclass but executed with alternate policy geometry.

## Risks and Test Signals
The signal is repeated central policy coverage under varied system policy selection. The risk is nondeterministic policy choice, which can make failures policy-dependent; logs include the selected policy for diagnosis.

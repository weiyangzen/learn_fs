# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/ECAdmin.java`

## Purpose

`ECAdmin` implements the `hdfs ec` command set for erasure coding administration: listing, adding, removing, enabling, disabling, setting, unsetting, querying policies, listing codecs, and verifying cluster topology support for EC policies.

## Important APIs, Types, and Functions

- `run` resolves an `AdminHelper.Command` from the first dash-prefixed argument, strips the command name, and invokes the command with the current configuration.
- `ListECPoliciesCommand` calls `DistributedFileSystem.getAllErasureCodingPolicies`.
- `AddECPoliciesCommand` loads policy XML through `ECPolicyLoader` and calls `addErasureCodingPolicies`.
- `GetECPolicyCommand`, `SetECPolicyCommand`, and `UnsetECPolicyCommand` resolve path-specific `DistributedFileSystem` instances and call path EC APIs.
- `RemoveECPolicyCommand`, `EnableECPolicyCommand`, and `DisableECPolicyCommand` mutate named cluster EC policies.
- `ListECCodecsCommand` calls `getAllErasureCodingCodecs`.
- `VerifyClusterSetupCommand` calls `getECTopologyResultForPolicies`, optionally with policy names after `-policy`.
- `COMMANDS` registers all subcommands for usage and dispatch.

## Control Flow

Every subcommand owns its option parsing using `StringUtils.popOptionWithArgument`, `StringUtils.popOption`, or `CommandFormat`. Most commands reject leftover args as "Too many arguments". Path commands choose DFS based on the path URI. Mutating commands catch `IOException`, prettify the exception, print to stderr, and return command-specific nonzero status.

`-setPolicy` permits either `-policy <policy>`, `-replicate`, or neither. `-replicate` maps to the replication pseudo-policy name. After setting or unsetting, it lists directory status to warn that existing files in non-empty directories are not converted automatically. `-enablePolicy` also asks the NameNode for topology support and prints a warning if the cluster cannot support the enabled policy.

## State and Persistence Behavior

All persistent state is in HDFS: EC policy definitions and enablement are cluster metadata, and path EC policy settings are namespace metadata. `-addPolicies` reads local XML policy definitions. `-verifyClusterSetup` and listing commands are read-only.

## Dependencies and Integration Points

The class integrates with `DistributedFileSystem` EC APIs, `ECPolicyLoader`, `ErasureCodingPolicy*` protocol types, `ECTopologyVerifierResult`, `NoECPolicySetException`, `ErasureCodeConstants.REPLICATION_POLICY_NAME`, `AdminHelper`, Hadoop `TableListing`, and `ToolRunner`.

## Risks and Edge Cases

- `-removePolicy` prints `"policy Xis removed"` without a space, a user-facing formatting defect.
- Directory non-empty warnings call `listStatusIterator`; permission or listing errors make the whole command fail after the policy mutation may already have succeeded.
- `-setPolicy` with neither `-policy` nor `-replicate` sets the default EC policy; callers must understand inherited/default behavior.
- `VerifyClusterSetupCommand` maps remote `HadoopIllegalArgumentException` by substring matching class name.
- Command-specific return codes are not uniform across subcommands.

## Test Signals

Tests should cover dispatch and dash-prefix validation, XML policy loading success/failure, path URI filesystem selection, `-setPolicy` option conflicts/default/replicate modes, non-empty directory warnings, `NoECPolicySetException` hint text, topology verifier supported/unsupported returns, and user-facing output regressions.

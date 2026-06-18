# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/CancelCommand.java

## Purpose

`CancelCommand` implements `hdfs diskbalancer -cancel`. It cancels an active disk-balancer plan either from a plan file, whose node address and hash can be derived, or from an explicit plan ID/hash plus `-node` address.

## Important APIs, Control Flow, and State

The constructor registers valid `-cancel` and `-node` options. `execute` verifies the command, then branches: with `-node`, it treats the cancel argument as the plan hash and calls `cancelPlanUsingHash`; without `-node`, it treats the cancel argument as a plan file, reads it as UTF-8 through `open`, and calls `cancelPlan`. `cancelPlan` parses `NodePlan` JSON, builds `host:port`, obtains a `ClientDatanodeProtocol` proxy, computes the SHA-1 hex hash of the full plan data, and calls `cancelDiskBalancePlan`. `cancelPlanUsingHash` obtains the proxy for the provided address and calls the same RPC.

The command has no persistent state beyond the inherited command configuration and any filesystem reads. It logs `DiskBalancerException` result/message and rethrows so CLI exit handling can report failure. `printHelp` documents both cancellation modes.

## Dependencies, Integration, Risks, and Tests

Dependencies include Commons CLI, Commons Codec SHA-1, Commons IO, `FSDataInputStream`, `NodePlan`, `ClientDatanodeProtocol`, `DiskBalancerException`, and `DiskBalancerCLI`. It integrates with plan execution/query commands because users can cancel by the query-reported plan ID/hash.

Risks include help text mentioning plan ID while implementation accepts whatever string is passed as hash, comment drift saying SHA-512 while code uses SHA-1, plan-file parsing failure, stale node address in plan files, and hash calculation depending on exact plan file bytes. Tests should cover cancel by file, cancel by node/hash, missing/invalid options, malformed plan JSON, RPC `DiskBalancerException` propagation, and hash consistency with execute command.

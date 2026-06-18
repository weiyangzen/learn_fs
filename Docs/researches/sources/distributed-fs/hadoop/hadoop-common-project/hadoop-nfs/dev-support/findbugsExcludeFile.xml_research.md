# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file suppresses a known exposure warning in the Hadoop NFS module.

## Important Entries
- It matches `org.apache.hadoop.oncrpc.security.CredentialsSys#getAuxGIDs()` returning `int[]`.
- It suppresses bug code `EI`, with a comment explaining that callers are not supposed to mutate the returned array and copying would be more expensive.

## Control Flow and State
The file is static build metadata consumed by the module's SpotBugs Maven configuration.

## Dependencies and Integration Points
It is referenced by `hadoop-nfs/pom.xml` together with Hadoop's global SpotBugs exclude file.

## Risks and Edge Cases
Suppressing mutable exposure is a deliberate performance tradeoff. If callers begin mutating the returned auxiliary group IDs, this suppressed issue could become a security or correctness problem.

## Test Signals
Static analysis should suppress only this known warning while continuing to report other NFS module issues.

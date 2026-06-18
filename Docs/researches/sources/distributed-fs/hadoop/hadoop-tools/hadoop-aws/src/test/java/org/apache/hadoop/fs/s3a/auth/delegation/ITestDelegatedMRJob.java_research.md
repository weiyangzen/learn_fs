<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestDelegatedMRJob.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestDelegatedMRJob.java

## Purpose

`ITestDelegatedMRJob` verifies that MapReduce job submission collects S3A delegation tokens for all S3A resources used by a job: input path, output path, and an extra cache-file resource. It runs as a parameterized integration test across session, full-credentials, and role delegation-token bindings.

## Important APIs, Types, and Functions

- `params()` returns parameter tuples for session, full, and role token bindings and token kinds.
- `setupCluster()` starts `MiniKerberizedHadoopCluster`; `teardownCluster()` stops it.
- `createConfiguration()` patches YARN/Kerberos config, configures fast RM failure, sets an external ORC job resource, clears its bucket endpoint override, and enables the selected delegation-token binding.
- `setup()` logs into the cluster principal, probes role ARN when needed, sets UGI config/security, and starts `MiniMRYarnCluster`.
- `testCommonCrawlLookup()` checks the extra job resource exists and is encrypted.
- `testJobSubmissionCollectsTokens()` builds a `MockJob` WordCount job, adds S3 input/output/cache resources, submits it, and validates submitted credentials contain tokens for each filesystem URI.

## Control Flow and State

The class-level MiniKDC fixture is shared across parameterized runs. Each test logs in a principal, starts a one-node MiniMR YARN cluster, creates a mock MapReduce job, and submits it through a mocked client-side protocol. The job remains in `RUNNING` state under `MockJob`, but its submitted credentials are available for inspection. Teardown deletes destination output, terminates YARN, tears down the S3A test base, and closes user filesystems.

## State and Persistence Behavior

Persistent test effects are S3A output directories under `destPath` and local MiniKDC/YARN state. The credentials object is in-memory. Static `cluster` holds the Kerberos fixture across tests. Filesystem caching is disabled in class setup to avoid stale token state.

## Dependencies and Integration Points

This file integrates `MiniKerberizedHadoopCluster`, `MiniMRYarnCluster`, `MockJob`, MapReduce WordCount classes, `TokenCache`-style job resource token collection, public dataset utilities, role-test utilities, and S3A delegation-token bindings.

## Risks and Edge Cases

The test depends on live S3 paths, public dataset availability, Kerberos-secure UGI, and role ARN configuration for role mode. It explicitly uses an extra S3 cache resource to cover token extraction from localized resources, a historically fragile path in YARN resource localization.

## Test Signals

Success is signaled by `MockJob` submission with `RUNNING` status, credentials containing token kinds matching source/destination/extra-resource URIs, and encrypted metadata on the extra public ORC resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestDelegatedMRJob.java -->

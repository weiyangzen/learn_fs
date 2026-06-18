# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestArnResource.java

## Purpose

Unit tests for parsing S3 access point ARNs and deriving access point endpoints across AWS partitions and services.

## Important APIs, Types, and Functions

Tests call `ArnResource.accessPointFromArn()`, then assert `getName()`, `getOwnerAccountId()`, `getRegion()`, and `getEndpoint()`. The helper `getArnResourceFrom()` builds `arn:partition:service:region:account:accesspoint/name` strings.

## Control Flow

`parseAccessPointFromArn()` loops through standard, GovCloud, and China region/partition pairs and checks parsed fields. Endpoint tests separately validate `s3-accesspoint.<region>.amazonaws.com` and `s3-outposts.<region>.amazonaws.com`. Invalid input is expected to throw `IllegalArgumentException`.

## State, Dependencies, and Integration Points

No persistent state. It depends on AWS SDK `Region`, AssertJ, Hadoop test base logging, and S3A `ArnResource` endpoint construction used by access point client setup.

## Risks and Test Signals

Endpoint expectations are intentionally partial and stable around AWS SDK changes. The tests catch ARN grammar regressions, partition/region field loss, invalid ARN acceptance, and wrong S3 versus S3 Outposts endpoint prefixes.

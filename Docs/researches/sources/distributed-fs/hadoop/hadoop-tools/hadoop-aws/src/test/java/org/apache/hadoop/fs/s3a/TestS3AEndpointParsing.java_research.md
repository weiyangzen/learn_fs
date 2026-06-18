# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AEndpointParsing.java

## Purpose

Focused unit tests for deriving AWS regions from standard S3 and VPC endpoint hostnames.

## Important APIs, Types, and Functions

Both tests call `DefaultS3ClientFactory.getS3RegionFromEndpoint(endpoint, false)` and compare the result with AWS SDK `Region.of(...)`.

## Control Flow

`testVPCEndpoint()` parses `vpce-...s3.us-west-2.vpce.amazonaws.com` and expects `us-west-2`. `testNonVPCEndpoint()` parses `s3.eu-west-1.amazonaws.com` and expects `eu-west-1`.

## State, Dependencies, and Integration Points

There is no state. It depends on `AbstractS3AMockTest`, AssertJ, AWS SDK `Region`, and endpoint parsing in the default S3 client factory.

## Risks and Test Signals

Endpoint parsing is easy to break with VPC endpoint hostname shapes. These tests catch incorrect token selection for both VPC and classic endpoints, but do not cover dualstack, FIPS, China, GovCloud, or custom endpoints.

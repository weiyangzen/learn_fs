# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AProxy.java

## Purpose

Unit tests verifying S3A proxy configuration is translated into AWS SDK Apache HTTP proxy configuration with the correct scheme.

## Important APIs, Types, and Functions

Tests set `Constants.PROXY_HOST`, `PROXY_PORT`, and `PROXY_SECURED`, then call `AWSClientConfig.createProxyConfiguration(conf, "testBucket")` and inspect `ProxyConfiguration.scheme()`.

## Control Flow

`testProxyHttp()` creates an unsecured proxy config and expects `http`. `testProxyHttps()` creates a secured proxy config and expects `https`. `testProxyDefault()` sets only a proxy host and expects the default scheme `http`. `verifyProxy()` builds the proxy configuration and asserts the scheme.

## State, Dependencies, and Integration Points

State is limited to Hadoop `Configuration`. It integrates S3A proxy options, per-bucket-aware AWS client config creation, and AWS SDK Apache proxy configuration.

## Risks and Test Signals

The test only checks scheme, not host, port, credentials, or no-proxy lists. It catches regressions where `fs.s3a.proxy.secured` is ignored or defaults change unexpectedly.

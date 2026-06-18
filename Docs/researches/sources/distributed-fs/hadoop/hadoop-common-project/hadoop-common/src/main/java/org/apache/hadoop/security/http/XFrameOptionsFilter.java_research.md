# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/XFrameOptionsFilter.java

## Purpose

`XFrameOptionsFilter` adds and preserves the `X-Frame-Options` response header to protect Hadoop web applications from clickjacking.

## Important APIs, Types, and Functions

It defines header `X-Frame-Options`, init param `xframe-options`, default option `DENY`, static `getFilterParams`, and nested `XFrameOptionsResponseWrapper` that blocks later changes to that header.

## Control Flow

`init` optionally replaces the default option. `doFilter` sets the configured header on the original response, then passes a wrapper down the chain. The wrapper suppresses subsequent add/set operations for the protected header while allowing other headers through.

## State and Persistence Behavior

The configured option is per-filter instance state. No persistent state is written.

## Dependencies and Integration Points

It depends on Servlet APIs and Hadoop `Configuration`. Hadoop HTTP servers can initialize it from prefixed configuration.

## Risks and Edge Cases

Header-name comparisons are case-sensitive, while HTTP header names are semantically case-insensitive. The wrapper's `containsHeader` implementation returns false for non-protected headers because it does not return `super.containsHeader(name)`, which can affect downstream filters.

## Test Signals

Tests should cover default/custom option, prevention of downstream overwrite/add, non-protected header pass-through, `containsHeader` behavior, and config prefix extraction.

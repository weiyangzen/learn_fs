# sources/distributed-fs/seaweedfs/weed/s3api/s3api_domain_test.go

Purpose: Tests domain classification for mixed virtual-host and path-style S3 access, especially issue #7356.

Important APIs/types/functions: `TestClassifyDomainNames`, `TestClassifyDomainNamesOrder`, `TestClassifyDomainNamesEdgeCases`, and `TestClassifyDomainNamesUseCases`.

Control flow: tests call `classifyDomainNames` with lists containing parent domains and subdomains. Expected behavior: a configured domain with a configured parent is classified path-style, while parent/base domains remain virtual-host style. Additional tests verify input order independence, duplicates, long domains, similar domains, IP addresses, localhost, and multi-environment setups.

State and persistence: pure classification tests; no server state or persistence.

Dependencies and integration: depends on `testify/assert` and the production `classifyDomainNames` helper used by S3 domain routing. It protects host-header routing for virtual-host-style bucket names and path-style deployments.

Risks: tests do not cover IDNA/punycode, ports in hostnames, trailing dots, uppercase normalization, wildcard domains, or IPv6 literals. Duplicate handling is asserted only loosely with contains checks.

Test signals: strong regression coverage for mixed parent/child domain configurations and order-insensitive classification.

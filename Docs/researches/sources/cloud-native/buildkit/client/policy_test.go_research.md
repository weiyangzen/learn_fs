# sources/cloud-native/buildkit/client/policy_test.go

## Purpose
This integration-test file covers BuildKit client source policy, policy session callbacks, proxy-network behavior, provenance material capture, source metadata resolution, Git signature metadata, and HTTP checksum assist. It verifies both static source policies and interactive session providers used by `SolveOpt.SourcePolicyProvider`.

## Important APIs, Types, and Functions
- Proxy-network tests: `testProxyNetworkNoRootless`, `testProxyNetworkModesNoRootless`, `testProxyNetworkDefaultEgressNoRootless`, `proxyNetModeDefaultHasHostLoopback`, `newProxyHTTPServer`, and `testHostIP`.
- Policy-session tests: `testSourcePolicySession`, `testSourcePolicySessionDenyMessages`, `testSourceMetaPolicySession`, `testSourceMetaPolicySessionResolveAttestations`, `testSourcePolicyParallelSession`, and `testSourcePolicySessionConvert`.
- Git and checksum tests: `testSourcePolicySignedCommit`, `testSourcePolicySessionHTTPChecksumAssist`, `toPBChecksumAlgo`, `payloadWithSuffixDigest`, and `tamperDigestHex`.
- Core dependencies include `policysession.NewPolicyProvider`, gateway `ResolveSourceMetadata`, source-policy protobufs, LLB image/git/http sources, SLSA provenance types, and PGP signature helpers.

## Control Flow
The proxy tests create local HTTP servers, run LLB execs through BuildKit proxy mode, inspect status logs, validate deny/convert policy behavior, and assert provenance material completeness. Network-mode tests verify default, host, and none modes with entitlement gating. Source-policy tests build LLB graphs or gateway metadata requests, then drive policy callbacks that allow, deny, request resolved metadata, request attestation chains, convert identifiers/attrs, or deliberately loop until the request limit is hit. Git tests create a local repository with signed and unsigned refs and validate policy-driven signature requirements. HTTP checksum tests request resolver-computed digests with signature suffixes and verify positive and negative signature checks.

## State and Persistence Behavior
The tests create temporary HTTP servers, temporary Git repositories, local output directories containing exported files and `provenance.json`, and policy provider session state such as callback counters and synchronization channels. BuildKit daemon state includes source resolver metadata, provenance records, network proxy logs, and source policy decisions. Environment variables gate expensive or fixture-dependent cases: network integration and signing fixtures.

## Dependencies and Integration Points
This file is a dense integration point for client `Solve`, client `Build`, gateway frontends, source resolver APIs, BuildKit proxy networking, entitlements, provenance export, policy-helper image attestations, Git source handling, and PGP verification. It also consumes integration sandbox values such as network mode, Docker/containerd address, rootless status, and worker feature flags.

## Risks and Edge Cases
Covered risks include host-network leakage through proxy env injection, missing `network.host` entitlement enforcement, incorrect default proxy egress behavior, incomplete provenance materials, policy deny messages being lost, metadata callbacks receiving incomplete platform/source fields, attestation chain blobs missing requested predicate types, deadlocks or serialization bugs in parallel policy checks, infinite convert loops, bad Git signature policy handling, oversized checksum suffixes, and unsupported checksum algorithms.

## Test Signals
A pass indicates that source policy remains enforceable across direct solve, gateway metadata resolution, proxy HTTP fetches, Git sources, image attestations, and provenance export. Failures tend to reveal security-sensitive regressions in network isolation, source substitution, metadata verification, or provenance completeness rather than superficial client formatting issues.

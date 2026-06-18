# sources/cloud-native/buildkit/solver/llbsolver/proc/sbom.go

Purpose: defines the post-solve processor that generates SBOM attestations with a configured scanner image/reference.

Important APIs/types/functions: `SBOMProcessor(scannerRef, useCache, resolveMode, params)`. It returns an `llbsolver.Processor`.

Control flow: skips generation if the result already has an SBOM, starts a tracing span, parses platform metadata, creates an SBOM scanner through the solver bridge, then for each platform ref builds an LLB state from the ref definition. It optionally applies `llb.IgnoreCache`, invokes the scanner, converts scanner output to BuildKit attestations, and solves any attestation state refs through the solver bridge.

State/persistence: mutates the result by adding attestations. Any scanner-created refs are solved through the same job/bridge and become regular solver results.

Dependencies/integration: frontend SBOM helper, source resolver image resolve mode, LLB state/definition conversion, solver bridge, result attestation conversion, exporter platform metadata, and tracing.

Risks: scanner creation can return nil, producing no attestation. Missing platform refs are fatal. The conversion callback performs nested solves, so scanner definitions must be safe under the current session and cache policy.

Test signals: no direct tests in this subset; behavior depends on SBOM frontend integration tests elsewhere.

# sources/cloud-native/buildkit/frontend/dockerfile/builder/build.go

Purpose: gateway frontend entry point for Dockerfile builds. It reads Dockerfile input, optionally forwards to another syntax frontend, handles subrequests, converts Dockerfile to LLB per platform, solves it, attaches SBOM attestations, and finalizes `dockerui` build results.

Important APIs: `Build(ctx, c)` is invoked by the frontend binary; `forwardGateway` invokes gateway frontend forwarding; `warnOpts` maps parser ranges to gateway warnings; `wrapSource` attaches source maps to errors.

Control flow: wraps the gateway client in `withResolveCache`, loads dockerui config, validates frontend caps, reads the Dockerfile, and honors syntax directives or `BUILDKIT_SYNTAX` by forwarding unless already in forwarded mode. Subrequests delegate to outline, target list, lint, or convertllb handlers. Normal build prepares `dockerfile2llb.ConvertOpt`, creates optional SBOM scanner, and calls `bc.Build` for each platform. Each platform converts Dockerfile, marshals and solves LLB, records scan targets, then `rb.Finalize` returns the result. SBOM scanning solves scanner states and attaches attestations per platform.

State and persistence: per-platform `scanTargets` map tracks conversion results. Build result refs and attestations persist in gateway result objects, not disk.

Dependencies and integration: central integration point for dockerui, dockerfile2llb, linter warnings, gateway client, platform handling, SBOM scanner, errdefs source mapping, and solver results.

Risks and test signals: risks include forwarding cap handling, source-location wrapping, stale resolve cache errors, multi-platform warning suppression after first platform, SBOM target mismatch, and subrequest behavior. Integration tests across Dockerfile frontend cover this file heavily.

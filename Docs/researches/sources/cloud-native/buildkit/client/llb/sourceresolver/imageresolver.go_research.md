# sources/cloud-native/buildkit/client/llb/sourceresolver/imageresolver.go

Purpose: adapts a generic source metadata resolver into the `llb.ImageMetaResolver` interface used by image states.

Important APIs/types/functions: `ImageMetaResolver` interface declares `ResolveImageConfig`. `NewImageMetaResolver` wraps a `MetaResolver`. Internal `imageMetaResolver.ResolveImageConfig` constructs a `pb.SourceOp`, calls `ResolveSourceMetadata`, validates image metadata, and returns resolved ref/digest/config.

Control flow: input ref is normalized with distribution/reference. Default source identifier is `docker-image://<ref>`; if `OCILayoutOpt` is present, identifier becomes `oci-layout://<ref>` and OCI session/store attrs are set. The metadata resolver may rewrite the op; the wrapper strips docker/OCI prefixes from the returned identifier and returns image digest/config, or returns `ResolveToNonImageError` if metadata is not image data.

State and persistence: no local persistence; delegates to supplied `MetaResolver`.

Dependencies/integration points: generic solver source metadata resolution, source policies/options, OCI layout resolver options, and image state async config resolution.

Risks/test signals: assumes returned identifiers use known prefixes. Non-image responses are converted to a typed imageutil error. No direct test in this subset; exercised indirectly where frontends use metadata resolvers.

## sources/cloud-native/soci-snapshotter/cmd/soci/commands/push.go

Purpose: implements `soci push`, uploading local SOCI v1 artifacts for an image to a registry.

Important APIs/types/functions: `PushCommand`, `pushDescs`, `debugClient`, and constants for quiet/concurrency flags.

Control flow: parse image ref, connect to containerd, resolve platforms, open artifacts DB and selected source store, build ORAS remote repository and auth, validate existing-index policy, choose most recent v1 SOCI index per platform while warning on v2, optionally inspect remote referrers, then copy each artifact graph with ORAS.

State and persistence: reads local content/artifacts DB and writes remote registry artifacts; no local mutation except network-side effects.

Dependencies and integration: containerd image/content, SOCI descriptor lookup, ORAS copy graph, remote auth, OCI artifact referrers, registry credentials.

Risks and test signals: v2 indexes are intentionally skipped. Existing remote checks rely on referrers support. TLS-related flags are declared elsewhere but not fully wired here. No direct tests here.

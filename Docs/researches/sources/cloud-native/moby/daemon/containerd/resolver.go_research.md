<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/resolver.go -->
# sources/cloud-native/moby/daemon/containerd/resolver.go

Purpose: builds authenticated containerd registry resolvers and authorizers from Docker daemon registry configuration and per-request auth.

Important APIs and flow: `newResolverFromAuthConfig` creates an in-memory docker status tracker, wraps registry hosts with auth when provided, clones meta headers, sets a Docker/containerd/storage-driver user agent, and returns `docker.NewResolver`. `hostsWrapper` replaces each host authorizer with one derived from request auth. `authorizerFromAuthConfig` normalizes auth server host, handles Docker Hub host aliases, returns a bearer authorizer for registry tokens, or a docker authorizer for username/password or identity token. `bearerAuthorizer` only adds Authorization when request host matches and returns not-implemented from `AddResponses` to avoid token retry.

State and persistence: no durable state; status tracker is in-memory for push progress.

Dependencies and integration: used by pull and push. Depends on Moby registry host conversion, Docker user-agent construction, containerd docker remotes, containerd version, daemon snapshotter name, and request auth config.

Risks: host mismatch results in warnings and no credentials, which can be confusing when aliases or ports differ. Bearer token authorizer performs exact `req.Host` matching. Meta headers are cloned then user-agent is overwritten.

Test signals: no direct tests in this subset; auth behavior needs registry integration or focused unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/resolver.go -->

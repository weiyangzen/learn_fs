<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/client_opts.go -->
# sources/cloud-native/containerd/client/client_opts.go

Purpose: option types for configuring the high-level client and remote image transfer contexts.

Important APIs/types/functions: `clientOpts`, `Opt`, and functions for default namespace/runtime/sandboxer/platform, dial/call options, service injection, and timeout. `RemoteOpt` configures `RemoteContext`: platform strings/matcher, pull unpack, unpack opts, snapshotter, labels, child label mapping, resolver, image handlers/wrappers, download/upload limiters, concurrent layer buffer, all metadata, and referrers provider.

Control flow: each option mutates a config struct. `WithDialOpts` replaces base dial options, while `WithExtraDialOpts` appends to defaults. `WithPlatform` deduplicates platform strings. `WithPlatformMatcher` supersedes platform strings in later client logic. Label options initialize maps and copy values.

State/persistence: options affect client defaults and remote operation behavior but do not persist by themselves. Pull labels persist on image records; snapshotter/unpack options affect snapshot state when used.

Dependencies/integration: uses Go `maps/slices`, containerd content/images/remotes/snapshots, platform matchers, OCI descriptors, semaphores, and gRPC options.

Risks: `WithDialOpts` can accidentally remove required defaults such as credentials, dialer, or message size unless caller supplies replacements. Platform matcher precedence can surprise callers combining platform options. Label maps passed through may be later mutated by caller depending on option.

Test signals: option composition tests should cover append vs replace dial opts, repeated platform dedupe, label copy behavior, matcher precedence, limiter fields, and service injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/client_opts.go -->

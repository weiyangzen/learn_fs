<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers.go -->
# sources/cloud-native/moby/daemon/containerd/platform_matchers.go

Purpose: wraps containerd platform matchers so Docker can match requested platforms strictly while preferring the daemon host platform when no platform was requested.

Important APIs and flow: `platformsWithPreferenceMatcher` matches either all platforms or a provided list, but delegates ordering to a preferred matcher. `matchAnyWithPreference` constructs it. `platformMatcherWithRequestedPlatform` embeds the matcher and remembers the explicit requested platform. `ImageService.matchRequestedOrDefault` returns a strict/requested matcher when a platform is supplied, otherwise a match-any matcher ordered by `hostPlatformMatcher`. `hostPlatformMatcher` uses a test override or `platforms.Default`.

State and persistence: stateless except for the test-only `defaultPlatformOverride` field on `ImageService`.

Dependencies and integration: used by list, inspect, push descriptor selection, and save/load behavior. Depends on containerd `platforms.MatchComparer`.

Risks: matching and ordering are intentionally separate; no requested platform means any platform can match, which is correct for summaries but can surprise push/export decisions when content is partial. Windows OSVersion semantics depend on containerd platform behavior and runtime OS.

Test signals: `platform_matchers_test.go` covers Linux ARM variant ordering, Windows OSVersion behavior where applicable, and list-limited preference matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers.go -->

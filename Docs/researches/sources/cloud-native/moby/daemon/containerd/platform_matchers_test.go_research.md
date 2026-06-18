<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers_test.go -->
# sources/cloud-native/moby/daemon/containerd/platform_matchers_test.go

Purpose: validates Docker/containerd platform matcher behavior used by list, inspect, push, load, and save paths.

Important APIs and flow: test fixtures define Linux amd64, ARM v5/v6, ARM64 v8, and Windows amd64 platforms. `TestMatcherOnLinuxArm64v8` checks default host preference and requested platform behavior with strict vs non-strict ARM variant matching. `TestMatcherOnWindowsAmd64` checks Windows OSVersion preference when running on Windows. `testOnlyAndOnlyStrict` executes the shared matrix. `TestPlatformsWithPreferenceMatcher` verifies list matching and preferred ordering.

State and persistence: no persistent state; uses `ImageService.defaultPlatformOverride` to emulate daemon platforms.

Dependencies and integration: depends on containerd `platforms`, Go runtime OS, and gotest assertions.

Risks and gaps: Windows OSVersion test is skipped outside Windows. The tests validate matcher mechanics, not every caller-specific policy decision.

Test signals: strong unit-level signal for strict requested platform and host-preferred ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/platform_matchers_test.go -->

# sources/cloud-native/moby/integration-cli/docker_cli_pull_test.go

Purpose: Docker Hub and platform-mismatch pull tests covering output, implicit reference handling, all-tags behavior, client disconnect cancellation, reserved names, and OS manifest errors.

Important APIs and functions: `DockerCLIPullSuite`, `DockerHubPullSuite` command helpers, `digest.Parse`, regex extraction of `Digest:`, `deleteImages`, `s.MakeCmd`, stdout pipe reads, and `dockerCmdWithError`.

Control flow: central registry tests pull `hello-world`, assert default tag/library prefix output and digest validity, then inspect images. Implicit reference tests pull equivalent refs and guard against legacy fallback. Scratch pull expects reserved-name failure. All-tags pulls compare image table size and preserve the `latest` line after normalizing relative age columns. Client-disconnect test kills the pull process after first output and verifies the image is absent. Platform tests pull Linux image on Windows and Windows image on Linux expecting manifest mismatch.

State and persistence: mutates local image store and relies on cleanup via `deleteImages`; process cancellation should prevent image persistence.

Dependencies and integration points: Docker Hub/network access, registry rate limit handling, digest parser, image table formatting, OS-specific manifest resolution, and snapshotter skip for malformed fixture image.

Risks: external network/rate limits can skip or fail tests; output text is CLI-version sensitive; cancellation timing is inherently racy.

Test signals: pull output must include expected defaulting and digest information, all-tags must add tags without corrupting existing latest metadata, cancelled pulls must not leave images, and platform-incompatible manifests must be rejected clearly.

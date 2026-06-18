# sources/cloud-native/moby/integration/image/size_test.go

Purpose: API compatibility test ensuring image sizes are never reported as negative for current and minimum API versions.

Important APIs and helpers: `TestImagesSizeCompatibility` creates clients with latest and `client.MinAPIVersion`, calls `ImageList`, and checks each `image.Summary.Size`.

Control flow: for each API version case, the test creates a client from environment, lists images, requires at least one image, and asserts all sizes are `>= 0`.

State and persistence: reads existing daemon image metadata only. It relies on frozen images from package setup.

Dependencies and integration: depends on API version negotiation, client environment configuration, and image list response serialization.

Risks: if the test environment has no images, it fails rather than skips. It does not validate exact sizes, only non-negative compatibility.

Test signals: protects old-client compatibility for image size fields, specifically against historical `-1` size regressions.

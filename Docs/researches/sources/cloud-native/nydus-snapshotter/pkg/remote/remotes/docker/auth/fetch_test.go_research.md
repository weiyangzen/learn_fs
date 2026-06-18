# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch_test.go

This test file covers `GenerateTokenOptions`. It builds Bearer challenges for multiple scopes, single scope, and no scope, then checks that realm, service, username, secret, and scope splitting are propagated into `TokenOptions`. It also verifies missing `realm` and syntactically invalid realm return errors.

The tests lock in the current behavior that the `scope` parameter is split by a single space. In the no-scope case, the challenge still includes `"scope": ""` in the test map, so the expected scopes become `strings.Split("", " ")`, a slice containing one empty string; that is a noteworthy behavior for downstream token requests.

Coverage gaps include `FetchToken`, `FetchTokenWithOAuth`, HTTP status errors, user-agent defaults, refresh token options, response decoding, and missing-token errors. The tests are pure in-memory and use no HTTP server or persistent state.

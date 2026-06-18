# sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer_test.go

Purpose: unit tests for Docker container connection-helper URL parsing.

Important APIs/types/functions: `TestSpecFromURL` table-tests `SpecFromURL` for a bare container URL, a URL with `context`, and an empty host.

Control flow: each input string is parsed by `net/url`, then `SpecFromURL` is called. Non-nil expected specs require no error and structural equality; nil expected specs require an error.

State and persistence: no persistent state; pure parser test.

Dependencies/integration points: standard `net/url`, Go testing, and `testify/require`.

Risks/test signals: confirms missing container rejection and context query extraction. It does not test dialer command arguments, URL path behavior, unexpected query keys, or Docker context value validation.

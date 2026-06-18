# sources/cloud-native/moby/daemon/logger/loggerutils/log_tag_test.go

Purpose: tests log tag template rendering.

Important APIs/types/functions: `TestParseLogTagZeroValues`, `TestParseLogTag`, and `buildContext`.

Control flow/state/persistence: constructs `logger.Info` values with container/image/env/label data and asserts rendered strings.

Dependencies/integration: validates behavior used by multiple drivers.

Risks: tests cover known templates and representative custom templates; template engine edge cases are delegated to the templates package.

Test signals: direct signal for tag compatibility across drivers.

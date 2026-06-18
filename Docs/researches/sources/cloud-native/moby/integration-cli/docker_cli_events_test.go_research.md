# sources/cloud-native/moby/integration-cli/docker_cli_events_test.go

Purpose: integration coverage for `docker events` historical queries, filters, formatting, object types, and event emission from containers, images, plugins, copy/archive operations, resize, attach, rename, commit, push, and daemon reloads.

Important APIs/types/functions: `DockerCLIEventSuite`; tests such as `TestEventsTimestampFormats`, `TestEventsContainerEvents`, `TestEventsContainerEventsAttrSort`, `TestEventsImageTag`, `TestEventsImagePull`, `TestEventsImageImport`, `TestEventsImageLoad`, `TestEventsPluginOps`, `TestEventsFilters`, `TestEventsFilterImageName`, `TestEventsFilterLabels`, `TestEventsFilterImageLabels`, `TestEventsFilterContainer`, `TestEventsCopy`, `TestEventsResize`, `TestEventsAttach`, `TestEventsFormat`, and daemon reload tests `TestDaemonEvents` and `TestDaemonEventsWithFilters`.

Control flow: tests capture daemon time, perform Docker operations, then run `docker events --since/--until` with filters and parse output using scan utilities or JSON decoding. Some tests run event streams with timeouts. Daemon reload tests start with config files, rewrite settings, send SIGHUP, and validate daemon reload event attributes.

State and persistence: relies on daemon event history and streaming state. Operations create and remove containers, tags, imported/loaded images, plugins, volumes via cp events, and daemon config labels. Saved image tar files and temp files are cleaned up.

Dependencies and integration points: event API types, event test parsing utilities, CLI/build helpers, Docker client resize API, private registry push path, network/pull availability, plugin image availability, and daemon time helpers.

Risks: event order and timestamp granularity are sensitive; several tests sleep to avoid second-level boundary issues. Output parsing depends on stable event text formatting and sorted attributes. Network, plugin, registry, and platform gates reduce portability.

Test signals: failures indicate missing or misfiltered events, event attribute formatting regressions, incorrect event IDs/actions for images/plugins/copy operations, broken JSON format output, or bad validation of event time windows and templates.

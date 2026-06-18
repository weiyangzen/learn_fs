# sources/cloud-native/moby/integration-cli/docker_cli_events_unix_test.go

Purpose: Unix-only event tests for terminal output cleanliness, OOM events, live event streaming, volume/network event types and filters, and daemon reload event filtering.

Important APIs/types/functions: `TestEventsRedirectStdout`, `TestEventsOOMDisableFalse`, `TestEventsOOMDisableTrue`, `TestEventsContainerFilterByName`, `TestEventsContainerFilterBeforeCreate`, `TestVolumeEvents`, `TestNetworkEvents`, `TestEventsContainerWithMultiNetwork`, `TestEventsStreaming`, `TestEventsImageUntagDelete`, `TestEventsFilterVolumeAndNetworkType`, `TestEventsFilterVolumeID`, `TestEventsFilterNetworkID`, `TestDaemonEvents`, and `TestDaemonEventsWithFilters`.

Control flow: tests start event listeners before or after actions, perform container/network/volume/image operations, and match actions by object ID/type. OOM tests run memory-consuming containers under memory limits and wait for either process exit or observed `oom`. Streaming tests use an observer with per-action channels. Redirect tests run through a pty and scan redirected output for control characters.

State and persistence: exercises event stream subscriptions, daemon event history, memory-limited containers, OOM state, network/volume create/connect/mount/unmount/destroy records, image delete/untag events, and daemon config reload events.

Dependencies and integration points: Linux daemon, memory and swap limit support, OOM control, pty, Unix signals, event observer helpers, Build helper, network and volume CLIs, and daemon harness with config reload.

Risks: OOM tests are flaky on constrained CI and are skipped in some environments. Live streaming is timing-sensitive and can fail if observer startup races with event emission. Volume and network event ordering depends on daemon internals.

Test signals: failures indicate event delivery/filtering regressions for Unix-only resource events, missing OOM notifications, control characters in redirected events output, broken live subscription matching, or daemon reload events not carrying expected attributes.


<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop_test.go -->
# sources/cloud-native/containerd/internal/cri/server/container_stop_test.go

## Purpose

This test file covers selected stop-path helpers in the CRI server package. It verifies that `waitContainerStop` observes timeout, cancellation, and already-finished container states, and it validates CRI signal-name conversion for stop signals and realtime signal spellings.

## Important APIs, Types, and Functions

The file defines `TestWaitContainerStop`, `TestCRISignalToOCIStopSignal`, and `TestConvertFromCRISignal`. The tests use `newTestCRIService`, `containerstore.NewContainer`, `containerstore.WithFakeStatus`, `criService.waitContainerStop`, `criSignalToOCIStopSignal`, and `convertFromCRISignal`. Runtime signal constants come from `k8s.io/cri-api/pkg/apis/runtime/v1`.

## Control Flow

`TestWaitContainerStop` builds fake container statuses with started and finished timestamps, inserts a fake container into the test CRI service store, optionally wraps the context with cancellation or timeout, and asserts whether `waitContainerStop` returns an error. The signal tests are table-driven and compare expected string forms for default, standard, realtime-min-plus, realtime-max-minus, and unknown signals.

## State and Persistence Behavior

The tests only manipulate in-memory fake container store state. The relevant observable state is `containerstore.Status.CreatedAt`, `StartedAt`, and `FinishedAt`, which controls whether a container is considered stopped. No runtime task, containerd metadata, or filesystem state is persisted.

## Dependencies and Integration Points

The tests integrate with the CRI server test harness, `containerstore`, and CRI runtime signal enums. They indirectly protect container stop implementations that wait on store status updates and translate CRI stop signals into OCI-compatible stop signal strings.

## Risks and Edge Cases

The timeout test uses a short wall-clock duration and could be scheduler-sensitive if `waitContainerStop` behavior changes. The tests cover signal-name conversion but not actual delivery to task shims. The signal conversion cases include unknown enum values, but they do not exhaust every CRI signal constant.

## Test Signals

Passing tests show `waitContainerStop` returns errors on timeout or canceled context, succeeds for already-finished containers, preserves runtime-default stop signal as an empty OCI override, maps standard signals, and rewrites `SIGRTMINPLUS1`/`SIGRTMAXMINUS1` into `SIGRTMIN+1`/`SIGRTMAX-1`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_stop_test.go -->

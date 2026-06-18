<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/debug-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/debug-modal.tsx

## Purpose
`debug-modal.tsx` opens a modal for collecting runtime debug artifacts from a pod container, streaming progress over websocket, and downloading the collected files.

## Important APIs, Types, and Functions
`DebugModal` is memoized and uses Monaco `Editor`, Ant Design modal/buttons/input numbers, lodash `max`, `useCountdown`, `useWebsocket`, and `useDownloadPodDebugFiles`. It tracks modal state, collection state, streamed text, download readiness, and sampling durations for stats/trace/profile.

## Control Flow, State, and Persistence
The websocket connects only while the modal is open and collecting. Query parameters pass the three durations. Incoming messages append to the editor and set `canDownload` when the backend reports collection completion. Closing the modal resets the text to a help message and clears download state. Start resets countdown and begins collection; Download calls the download hook.

## Dependencies and Integration Points
It depends on backend websocket path `/api/v1/ws/pod/{namespace}/{name}/{container}/debug` and matching download endpoint in `useDownloadPodDebugFiles`. Monaco worker setup comes from `App.tsx`.

## Risks and Test Signals
Risks include brittle completion detection by substring, countdown not necessarily matching backend close, unlimited text accumulation, no websocket error display, and no min/max validation on duration inputs. Signals are websocket lifecycle tests, completion/download enablement, modal reset behavior, and large-output editor performance checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/debug-modal.tsx -->

# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-modal.tsx

## Purpose
`UpgradeModal` performs an interactive smooth upgrade or binary upgrade for a single mount pod and streams progress logs.

## APIs, Control Flow, and State
It accepts namespace, pod name, `recreate`, and a render-prop trigger. When opened it fetches the latest image with `useMountPodImage`, initializes help text, and connects to `/api/v1/ws/pod/:namespace/:name/upgrade` only after Start. It sends `recreate=true|false` as query data, appends logs, and detects `POD-SUCCESS` plus a specific backend message to redirect to the recreated pod after a countdown.

## Dependencies and Integration Points
It is used by container/pod controls, depends on `useWebsocket`, Monaco, Ant Design, and backend log grammar.

## Risks and Test Signals
The success regex accepts DNS-like names but is tightly coupled to English backend output. Logs are unbounded in state. Test recreate and non-recreate flows, missing latest image, failed upgrade, close before completion, and success redirect parsing.

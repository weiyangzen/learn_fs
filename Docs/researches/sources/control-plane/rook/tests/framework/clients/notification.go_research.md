# sources/control-plane/rook/tests/framework/clients/notification.go

Purpose: `NotificationOperation` manages `CephBucketNotification` CRs and verifies notification delivery to a test HTTP endpoint.

Important APIs/types/functions: constructor `CreateNotificationOperation`; `CreateNotification`, `DeleteNotification`, `UpdateNotification`; `CheckNotificationCR`; `CheckNotificationFromHTTPEndPoint`.

Control flow: CRUD methods render `CephBucketNotification` manifests and use kubectl create/delete/apply. `CheckNotificationCR` performs a simple `kubectl get cephbucketnotification`. `CheckNotificationFromHTTPEndPoint` sleeps for five seconds, tails logs from pods matching a selector, and checks for both event and file name substrings.

State and persistence behavior: persistent state is the notification CR and backend RGW notification config created by operator reconciliation. Delivery evidence is transient in HTTP server pod logs.

Dependencies and integration points: depends on bucket topic resources, RGW bucket notifications, `K8sHelper.Kubectl`, and the HTTP server created by `TopicOperation`.

Risks: status is not inspected despite a TODO, so CR existence may be treated as success before reconciliation. Fixed sleep and tailing only five log lines are flaky under load. Log substring matching can false-positive if old messages remain.

Test signals: stronger tests should validate notification CR status, RGW notification config, and fresh HTTP endpoint receipt scoped to unique object names.

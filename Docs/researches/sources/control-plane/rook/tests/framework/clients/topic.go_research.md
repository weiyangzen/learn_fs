# sources/control-plane/rook/tests/framework/clients/topic.go

Purpose: `TopicOperation` manages `CephBucketTopic` resources and a simple HTTP endpoint used to receive RGW bucket notifications in integration tests.

Important APIs/types/functions: constructor `CreateTopicOperation`; topic CRUD methods `CreateTopic`, `DeleteTopic`, `UpdateTopic`; validator `CheckTopic`; helper `CreateHTTPServer`.

Control flow: topic CRUD methods render manifests and use kubectl create/delete/apply. `CheckTopic` ensures the CR exists and has a non-empty `.status.ARN`. `CreateHTTPServer` constructs a Deployment and NodePort Service YAML using a third-party Python web server image, applies it via stdin, then waits for pods labeled with the server name.

State and persistence behavior: persistent state includes the topic CR, HTTP server Deployment/Service, and backend RGW topic configuration after reconciliation.

Dependencies and integration points: depends on `CephManifests.GetBucketTopic`, Kubernetes deployments/services, RGW topic operator status, and the notification client that later tails HTTP server logs.

Risks: hand-built YAML string interpolation can break with invalid names/ports. The third-party image is explicitly noted by TODO and may disappear/change. `IsAlreadyExists` handling on `kubectl apply` errors is mostly irrelevant because apply should be idempotent. NodePort service choice requires cluster support.

Test signals: non-empty topic ARN, HTTP server pod readiness, notification delivery logs, and topic cleanup are the main signals.

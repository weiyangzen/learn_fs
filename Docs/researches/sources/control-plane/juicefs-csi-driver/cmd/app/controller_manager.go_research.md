# sources/control-plane/juicefs-csi-driver/cmd/app/controller_manager.go

## Purpose
This Go file defines the controller-runtime manager used by the CSI controller process for mount management, webhook-sidecar management, cache client config watching, and controller metrics.

## Important APIs, Types, and Functions
`ControllerManager` stores a `ctrl.Manager`, feature flags for mount manager and webhook, and a `k8sclient.K8sClient`. `NewControllerManager(...)` builds the manager from in-cluster config with metrics on `0.0.0.0:8084`, optional leader election, cached Pod and Job informers, optional webhook server, and a shared Kubernetes client. `Start(ctx)` registers controllers according to enabled flags and starts the manager.

## Control Flow
Construction gets Kubernetes config, builds `ctrl.Options`, optionally attaches a webhook server when `config.Webhook` is true, creates the controller-runtime manager, then creates the project-specific Kubernetes client. Startup registers webhook handlers and `AppController` in sidecar mode, registers `MountController` and `JobController` when mount management is enabled, registers `PVController` and `SecretController` when `config.CacheClientConf` is enabled, then calls `mgr.Start(ctx)`.

## State and Persistence Behavior
The manager itself persists no files. It watches Pods and Jobs, writes metrics, participates in leader election through Kubernetes Leases, and delegates state changes to registered controllers that create/update/delete mount pods, jobs, PV/Secret cache state, and webhook-admitted pods.

## Dependencies and Integration Points
It depends on controller-runtime, Kubernetes core and batch APIs, JuiceFS common labels, global config, `pkg/controller`, `pkg/k8sclient`, and `pkg/webhook/handler`. It is called from `cmd/controller.go` when the controller process enables mount manager or webhook mode.

## Risks
`NewControllerManager` calls `os.Exit(1)` on `ctrl.NewManager` failure instead of returning the error, which makes it harder to unit test and reason about caller cleanup. The `enableWebhook` parameter controls registration, while `config.Webhook` controls whether the webhook server is configured; a mismatch could register handlers without a server or vice versa. Cache filters Jobs by `common.PodTypeKey=common.JobTypeValue`, so mislabeled jobs are invisible to the manager cache.

## Test Signals
There are no direct tests in this file. It is covered by Go build, controller package tests, and E2E modes that exercise mount manager, webhook, cache client config, and volume deletion jobs.

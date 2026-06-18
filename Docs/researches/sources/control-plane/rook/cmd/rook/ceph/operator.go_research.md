# sources/control-plane/rook/cmd/rook/ceph/operator.go

## Purpose

Defines the `rook ceph operator` command that starts the Rook-Ceph Kubernetes operator.

## Important APIs, Types, and Functions

`operatorCmd` registers `--enable-machine-disruption-budget`, imports Go standard flags, sets flags from `ROOK_` environment variables, and runs `startOperator()`. `containerName` is `rook-ceph-operator`.

## Control Flow

Execution sets logging, logs flags, creates a cluster context, forces config dir to `k8sutil.DataDir`, validates the pod namespace env var, checks operator resources, discovers the operator image and base Ceph version, stores the base version in controller global state, gets the service account name, constructs the Ceph operator, and calls `op.Run()`.

## State and Persistence Behavior

The command starts long-lived controller loops that reconcile Kubernetes and Ceph resources. This wrapper also updates process-global `opcontroller.OperatorCephBaseImageVersion`.

## Dependencies and Integration Points

It integrates with Cobra, Rook command helpers, Kubernetes clientsets, operator resource discovery, image/service-account discovery, Ceph base image version detection, and `pkg/operator/ceph`.

## Risks and Edge Cases

Missing pod namespace is fatal. Failure to detect base image Ceph version is logged but not fatal, so downstream logic must tolerate an empty or unknown version. Adding standard flags to Cobra can expose klog/client flags through the operator command.

## Test Signals

Operator startup unit tests and integration canaries validate command wiring indirectly by deploying the operator and reconciling clusters.

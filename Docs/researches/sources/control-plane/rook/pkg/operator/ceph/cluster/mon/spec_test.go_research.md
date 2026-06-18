# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec_test.go

## Purpose
This file tests monitor Kubernetes spec generation: Deployments, pod templates, PVCs, scheduling requirements, failure-domain labels, security context, probes, and msgr2 binding behavior.

## Important APIs, Types, And Functions
`TestPodSpecs` and `testPodSpec` build clusters and monitor configs for both new-style IDs (`a`) and legacy IDs (`mon0`), with hostPath and PVC variants. They exercise `makeDeployment()` and `makeMonDaemonContainer()`. `checkMsgr2Required()` inspects command-line flags for `--ms-bind-msgr1=false` and `--public-bind-addr`. `TestDeploymentPVCSpec` covers `makeDeploymentPVC()`. `TestRequiredDuringScheduling`, `TestGetFailureDomainLabel`, and `TestMakeMonSecurityContext` cover smaller spec helpers.

## Control Flow And State
The tests create fake cluster specs with Ceph image, resources, priority classes, health-check probe overrides, network settings, and volume claim templates. They then inspect generated objects in memory. PVC tests verify default storage request injection and preservation of explicit storage limits or requests. Probe tests verify cluster-provided startup/liveness probe fields override generated defaults. Msgr2 tests mutate `monConfig.Port` and `c.spec.Network` across default, dual-stack, IPv4, and IPv6 scenarios.

## Dependencies And Integration Points
The tests depend on Rook fake clientsets, Ceph client test owner refs, operator test helpers for label/pod-template assertions, Kubernetes resource quantities, and Ceph API spec structures. They integrate normal monitor spec generation with shared Rook daemon volume/env/probe helpers.

## Risks And Test Signals
The strongest signals are around stable labels, resources, service account, priority class, probe overrides, and network-specific bind address formatting. The test explicitly catches IPv6 bracket requirements and dual-stack avoidance of forced port binding. It also confirms `ROOK_CEPH_MON_RUN_AS_ROOT=true` changes the pod security context to `RunAsUser: 0`. Runtime behavior of the generated containers is not tested.

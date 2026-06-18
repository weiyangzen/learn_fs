# Research: sources/cloud-native/buildkit/examples/eksctl/bottlerocket.yaml

## Purpose
eksctl cluster config for a Bottlerocket EKS node group suitable for BuildKit user namespace/rootless experiments.

## Important APIs, Types, and Functions
Declares `ClusterConfig` v1alpha5, cluster metadata, a `buildkit` node group, managed IAM policies, and Bottlerocket kernel sysctl `user.max_user_namespaces`.

## Control Flow
eksctl reads the YAML, creates cluster/node group resources, attaches IAM policies, and applies Bottlerocket settings.

## State and Persistence
State lives in AWS/EKS resources after application; this file is static desired state.

## Dependencies and Integration Points
Depends on eksctl schema, EKS/Bottlerocket support, AWS IAM policy names, and region/version availability. Supports the Kubernetes rootless/userns BuildKit manifests.

## Risks and Edge Cases
Pinned Kubernetes `1.27` can become unsupported; region, policies, and sysctl are example values needing review.

## Test Signals
No tests; validation is cluster creation and later BuildKit pod scheduling.

# sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/webhook.yaml

## Purpose
deployment manifest for `apps/v1` `Deployment` named `snapshot-conversion-webhook-deployment`.

Source size: 48 lines, 1587 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `apps/v1` `Deployment` named `snapshot-conversion-webhook-deployment`.
- Important fields: `spec.replicas=1`, `spec.selector` (matchLabels), `spec.template` (metadata, spec), namespace `default`, labels `app.kubernetes.io/name`.
- Contains 2 YAML documents; document kinds: Deployment, Service.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

## State and Persistence
- No local persistence; applying the manifest creates or updates Kubernetes API objects.
- Object state lives in the API server and is reconciled by controllers after admission.
- For CEL fixtures, state is temporary test state created by server-side dry run or by pre/post transaction setup.

## Dependencies and Integration Points
- Kubernetes API server and the relevant built-in or CRD API group.
- External snapshotter CRDs/controllers when the object uses snapshot or group snapshot APIs.
- `kubectl`/kustomize for application and validation.

## Risks and Edge Cases
- Field drift against CRD schemas can make the fixture or deployment fail admission.
- Name, namespace, driver, and selector values are often test-specific and may not be valid in arbitrary clusters.
- Expected-failure fixtures are sensitive to exact validation error text.

## Test Signals
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/update-image-pull-policy.sh -->
# sources/control-plane/longhorn/dev/scripts/update-image-pull-policy.sh

Purpose: live-cluster helper that patches Longhorn DaemonSets and Deployments so their containers use `imagePullPolicy: Always`.

Important APIs/types/functions: namespace `longhorn-system`, kinds `daemonset deployments`, function `patch_kind`, `kubectl get <kind> -o name`, and strategic merge patch over `spec.template.spec.containers`.

Control flow: lists objects for each kind, derives container name from object name, applies a patch setting that container's pull policy to `Always`, then starts `kubectl get pods -w`.

State and persistence: mutates live workload pod templates, which triggers rollouts and changes future pod image pulling behavior.

Dependencies/integration points: depends on `kubectl`, current cluster permissions, object names matching container names, and Kubernetes patch semantics.

Risks/test signals: not every workload's container name necessarily equals object name; multi-container pods are only partially patched. Test signals are inspecting deployment/daemonset pod templates, rollout status, and pod image pull behavior after restart.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/update-image-pull-policy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/ui-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/ui-network-policy.yaml

Purpose: ingress NetworkPolicy allowing Longhorn UI traffic from an ingress-nginx controller.

Important APIs/types/functions: selects `app: longhorn-ui` and allows ingress from namespace label `kubernetes.io/metadata.name: ingress-nginx` plus ingress-nginx controller pod labels.

Control flow: with a policy CNI, only matching ingress controller pods can initiate traffic to UI pods.

State and persistence: Kubernetes NetworkPolicy object only.

Dependencies/integration points: depends on ingress-nginx namespace/pod labels matching the example and on a separate Ingress/Service exposing the UI.

Risks/test signals: different ingress controllers or labels require changes; direct cluster access may be blocked. Test signals are UI reachability through ingress and denied direct pod/service access where expected.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/ui-network-policy.yaml -->

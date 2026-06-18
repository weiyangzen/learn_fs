# sources/control-plane/rook/pkg/daemon/multus/nginx-pod.yaml

Purpose: template for the single validation web server pod that attaches to the configured public and cluster Multus networks and serves a simple Nginx endpoint.

Important APIs/types/functions: embedded as `nginxPodTemplate` and rendered by `generateWebServerPod()` from `webServerTemplateConfig`. Uses `.NetworksAnnotationValue`, `.Placement`, and `.NginxImage`.

Control flow: `startWebServer()` renders the pod using the best node placement from config, owner-references it, and creates it after the Nginx ConfigMap. `getWebServerInfo()` later reads its Multus network status and readiness before clients and host checkers are started.

State and persistence behavior: a single Kubernetes Pod owned by the validation owner ConfigMap. It persists for the duration of the validation and is removed during cleanup.

Dependencies and integration points: depends on Multus network annotation, Nginx image UID/GID 101 behavior, ConfigMap volume from `nginx-config.yaml`, emptyDir mounts for Nginx writable paths, and Kubernetes readiness probe. It integrates with `getNetworksFromPod()` to discover public and cluster IPs.

Risks: the YAML says `apiVersion: apps/v1` for `kind: Pod`; Kubernetes Pods normally use `apiVersion: v1`, so this template is risky unless unmarshaled object creation normalizes or tests do not exercise API server validation. Network annotation must be non-empty for configured networks. Security settings assume the Nginx unprivileged image layout.

Test signals: no direct test validates the rendered Pod against Kubernetes API validation. Runtime failures would surface as web server creation/readiness errors in the validation workflow.

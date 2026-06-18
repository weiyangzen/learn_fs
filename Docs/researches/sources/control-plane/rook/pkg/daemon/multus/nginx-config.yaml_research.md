# sources/control-plane/rook/pkg/daemon/multus/nginx-config.yaml

Purpose: template for the ConfigMap mounted into the validation web server pod, configuring Nginx to respond on port 8080 with the connecting client's remote address.

Important APIs/types/functions: embedded as `nginxConfigTemplate` and rendered by `generateWebServerConfigMap()`. It produces ConfigMap `multus-validation-test-web-server-conf` with key `server.conf`.

Control flow: `startWebServer()` creates this ConfigMap before creating the web server pod to avoid initial mount failures. The Nginx server listens on IPv4 and IPv6 and returns `$remote_addr` as plain text for any path.

State and persistence behavior: temporary Kubernetes ConfigMap owned by the validation owner ConfigMap. Its data is static for a validation run.

Dependencies and integration points: consumed by `nginx-pod.yaml` via a ConfigMap volume at `/etc/nginx/conf.d`. The returned client address is mostly diagnostic; readiness checks only require HTTP success.

Risks: if Nginx image path or config include conventions differ, the mounted config may not be loaded. The template has no dynamic fields today but still goes through template rendering.

Test signals: no direct test for ConfigMap content or server response; rendering errors would surface when template parsing/unmarshaling is exercised indirectly.

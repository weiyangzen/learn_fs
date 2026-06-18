# sources/control-plane/longhorn/chart/templates/validate-psp-install.yaml

Purpose: contains a disabled Helm validation block intended to fail rendering when PSP is enabled on clusters without the PSP API.

Important APIs/types/functions: commented Helm `lookup`, `.Values.enablePSP`, `.Capabilities.APIVersions.Has "policy/v1beta1/PodSecurityPolicy"`, and `fail`.

Control flow: because every line is commented, the template currently emits no resources and performs no validation. If uncommented, it would first check cluster RBAC lookup availability, then fail when PSP is requested but unavailable.

State and persistence: no Kubernetes state is created. Its only intended effect would be render-time validation.

Dependencies/integration: relates to `psp.yaml` and Kubernetes version compatibility. The use of `lookup` would require Helm rendering against a live cluster rather than purely offline templating.

Risks: keeping the block commented means `enablePSP: true` can render an unsupported `policy/v1beta1` resource and fail later at install time. Un-commenting it would make offline template rendering and restricted RBAC contexts more complex.

Test signals: verify current `helm template` output contains no objects from this file. If validation is re-enabled, test offline rendering, live clusters with and without PSP API, and users lacking permission for the `lookup` call.

# sources/control-plane/rook/pkg/daemon/multus/templates.go

Purpose: embeds Multus validation YAML templates and renders them into typed Kubernetes Pod, ConfigMap, and DaemonSet objects.

Important APIs/types/functions: embedded templates are `nginxPodTemplate`, `nginxConfigTemplate`, `imagePullDaemonSet`, `hostCheckerDaemonSet`, and `clientDaemonSet`. Template config structs model web server, image puller, host checker, and client inputs. Generation methods include `generateWebServerPod()`, `generateWebServerConfigMap()`, `generateImagePullDaemonSet()`, `generateHostCheckerDaemonSet()`, and `generateClientDaemonSet()`. Helpers include label/name functions, `generateNetworksAnnotationValue()`, `applyServiceAccountToPodSpec()`, and `loadTemplate()`.

Control flow: each generator renders a text/template, unmarshals YAML into the corresponding Kubernetes API type, applies service account where relevant, and returns the object to resource creation helpers. Client template config builds the set of target server addresses and wraps IPv6 addresses in brackets before templates append `:8080`.

State and persistence behavior: no persistent state; outputs are in-memory Kubernetes objects later created by `resources.go`. Template strings are embedded at compile time.

Dependencies and integration points: depends on `text/template`, Kubernetes API structs, Kubernetes YAML unmarshaler, and `ValidationTest` config. Labels produced here are consumed by selectors in `resources.go` and state machine logic in `validation.go`.

Risks: templates are only parsed at runtime, so syntax errors surface when a validation path renders them. YAML API version/kind mismatches may not be caught until object creation. `generateNetworksAnnotationValue()` returns comma-separated network names, so names containing unexpected commas would break annotation semantics. Map iteration in templates can affect deterministic output ordering.

Test signals: no direct tests of rendered Kubernetes objects in this subset. `config_test.go` indirectly tests `loadTemplate()` for the config template only.

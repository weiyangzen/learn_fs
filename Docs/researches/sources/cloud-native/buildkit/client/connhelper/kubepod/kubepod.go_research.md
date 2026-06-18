# sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod.go

Purpose: connection helper for `kube-pod://<pod>` URLs, tunneling to `buildctl dial-stdio` inside a Kubernetes pod/container through `kubectl exec`.

Important APIs/types/functions: `init` registers scheme `kube-pod`. `Helper` returns a dialer that runs `kubectl --context=<context> --namespace=<namespace> exec --container=<container> -i <pod> -- buildctl dial-stdio`. `Spec` stores context, namespace, pod, and container. `SpecFromURL` extracts query parameters and validates pod/namespace/container identifiers. `validKubeIdentifier` matches `^[-a-z0-9.]+$`.

Control flow: URL host becomes pod name; namespace and container are optional but validated if set; context is not validated and may contain characters like `@`. Dialing always includes context/namespace/container flags even if values are empty, then runs the subprocess via `commandconn` with background context.

State and persistence: no persistent state beyond scheme registration. The helper depends on the user’s kubeconfig and target pod runtime state.

Dependencies/integration points: shared `connhelper`, Docker CLI `commandconn`, `kubectl`, Kubernetes naming rules, and BuildKit’s stdio dial endpoint inside the container.

Risks/test signals: always passing empty `--context=`, `--namespace=`, or `--container=` can interact with kubectl defaults differently than omitting flags; parser validation excludes underscores and uppercase names for pod/container/namespace but intentionally leaves context unrestricted. Unit tests cover valid/invalid identifiers and context with `@`.

# sources/cloud-native/cri-o/internal/factory/container/container_linux.go

Purpose: implements Linux SELinux label resolution for containers.

Important APIs/types/functions: `(*container).SelinuxLabel(sboxLabel string) ([]string, error)`.

Control flow: returns nil when the container is privileged. Otherwise it reads the container Linux security context. If `SelinuxOptions` are unset, it returns the sandbox label. If options are set, it calls `utils.GetLabelOptions` to convert CRI SELinux options into label options and returns them.

State and persistence behavior: no persistent state; reads container config and sandbox label input only.

Dependencies/integration points: opencontainers SELinux package and CRI-O `utils`. Called during OCI spec setup to apply labels.

Risks: privileged containers intentionally bypass SELinux labeling. Invalid or incomplete SELinux options propagate errors from `GetLabelOptions`.

Test signals: no tests for this file in the listed subset.

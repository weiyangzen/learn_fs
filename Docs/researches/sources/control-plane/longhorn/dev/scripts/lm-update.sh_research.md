<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/lm-update.sh -->
# sources/control-plane/longhorn/dev/scripts/lm-update.sh

Purpose: developer script for retagging the latest Longhorn manager image to a private DockerHub namespace, pushing it, patching local manager/driver manifests, and optionally recreating cluster resources.

Important APIs/types/functions: reads username and optional update flag, uses `${GOPATH}/src/github.com/longhorn/longhorn-manager`, `bin/latest_image`, `docker tag`, `docker push`, and multiple `sed -i` replacements against manager and driver YAML files.

Control flow: validates username, derives private image by replacing `longhornio` with username, pushes the tag, escapes slashes, rewrites image references and imagePullPolicy in two manifests, then deletes/recreates those manifests unless the second argument is non-empty.

State and persistence: mutates Docker registry state, local manifest files, and optionally live Kubernetes resources.

Dependencies/integration points: depends on GOPATH layout, Docker CLI credentials, `sed`, `kubectl`, and Longhorn manager deploy file paths in a separate repository.

Risks/test signals: regex replacement is broad, delete/create can disrupt running Longhorn, and it assumes old repository layout. Test signals are image push success, clean manifest diff, `kubectl apply --dry-run=server`, and rollout of manager/driver pods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/dev/scripts/lm-update.sh -->

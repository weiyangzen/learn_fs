# sources/cloud-native/soci-snapshotter/scripts/bump-deps.sh

Purpose: updates Go module dependencies while constraining containerd to patch releases and excluding Kubernetes dependencies.

Important APIs/types/functions: runs `go get -u=patch github.com/containerd/containerd/v2`, runs `go get` on direct non-main modules excluding containerd and `k8s.io/`, runs `make tidy`, then repeats analogous updates under `./cmd` while excluding the main soci-snapshotter module.

Control flow: enter project root, update root module, tidy, enter `cmd`, update cmd module, return, tidy again.

State and persistence: mutates `go.mod`/`go.sum` in root and `cmd`, plus any tidy-generated module changes.

Dependencies/integration points: Go module tooling and Makefile `tidy` target.

Risks: command substitution can fail if module list is empty. Exclusions encode policy that k8s uses newer Go/features and containerd minor bumps must be intentional. Broad updates can still introduce transitive shifts.

Test signals: no direct test; downstream CI/lint/test suites validate updated deps.

# sources/cloud-native/containerd/contrib/v2-migrate.sh

Purpose: one-shot shell migration helper that rewrites Go import paths from pre-v2 containerd paths to containerd/v2 module layout and related package moves.

Important behavior: iterates over all `.go` files outside `vendor`, applies many Perl in-place regex substitutions, then runs `gofmt -s -w`. It first inserts `/v2` for `github.com/containerd/containerd` imports except `/v2` and `/api`, then rewrites moved packages into `core`, `plugins`, `pkg`, `internal`, split-out repositories, and API packages.

Control flow and state: mutates every matching Go file in the current working tree. There is no dry-run, backup, or git safety check.

Dependencies and integration: depends on POSIX shell, `find`, `grep`, Perl, and gofmt. Encodes containerd v2 package layout knowledge, including split packages such as `github.com/containerd/platforms`, `github.com/containerd/errdefs`, `github.com/containerd/plugin`, and `github.com/moby/sys/user/userns`.

Risks: regex-based import rewriting can miss unusual import formatting or rewrite unintended strings if they look like imports. Running from the wrong directory can damage unrelated Go code. It does not update non-Go references or module requirements.

Test signals: no tests. Validation requires `git diff`, `go test`, `go list`, and manual review of import aliases after running.

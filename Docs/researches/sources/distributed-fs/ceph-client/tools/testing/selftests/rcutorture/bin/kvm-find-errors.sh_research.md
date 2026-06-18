# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-find-errors.sh

Purpose: locates build and runtime diagnostics in an rcutorture result directory and opens them in an editor.

Important APIs and functions: scans `Make.out` for compile/link diagnostics, checks missing kernel artifacts, collects existing `console.log.diags`, and invokes `${EDITOR:-vi}`.

Control flow: validate directory, find build errors and write `.diags`, maybe invoke editor, skip console checks for build-only runs, then open console logs with diagnostics or report no errors.

State and persistence: creates `Make.out.diags` files and possibly other diagnostic files.

Dependencies and integration: used interactively and by `kvm-recheck.sh` with `EDITOR=echo` to count failures.

Risks and test signals: editor invocation is side-effectful and interactive by default. Pattern matching can mark warnings as errors.

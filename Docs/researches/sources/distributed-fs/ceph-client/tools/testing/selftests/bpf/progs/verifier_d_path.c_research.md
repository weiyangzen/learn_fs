# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_d_path.c

## Purpose

`verifier_d_path.c` checks program-type restrictions for the `bpf_d_path` helper. The helper is accepted from a suitable fentry attachment that receives a file/dentry-related object and rejected from a probe context where the helper is not allowed.

## Important APIs, Types, and Functions

Two naked programs are declared: `d_path_accept` in `SEC("fentry/dentry_open")` and `d_path_reject` in `SEC("fentry/d_path")`. Both prepare a stack buffer and call the d_path helper. The expected rejection message is `helper call is not allowed in probe`.

## Control Flow

The accepted program extracts the needed kernel pointer from tracing context, points `r2` at a stack buffer, sets a size, calls the helper, and returns zero. The rejected program performs a similar call shape from a helper-ineligible attachment, proving the verifier checks helper allowlists independently of instruction form.

## State and Persistence Behavior

The only state is stack memory used as the pathname buffer. No maps are declared. Verifier state tracks helper availability by program type and whether the first argument is a suitable kernel pointer.

## Dependencies and Integration Points

The test depends on BTF fentry attachment points, the `bpf_d_path` helper prototype, and verifier helper allowlists. It integrates with filesystem tracing because the accepted path runs at `dentry_open`.

## Risks and Test Signals

Risks are widening helper availability to unsafe probe contexts or accidentally rejecting valid fentry usage. Test signals are one successful load and one failure with the helper-not-allowed diagnostic.

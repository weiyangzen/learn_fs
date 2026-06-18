# sources/cloud-native/ostree/tests/xtask/src/tmt.rs

## Purpose
This Rust module implements `ostree-xtask run-tmt`, running selected TMT plans inside isolated `bcvk` libvirt VMs.

## Important APIs, Types, And Functions
Key items include constants `SSH_TIMEOUT_SECS` and `SSH_POLL_INTERVAL_SECS`, `RunTmtArgs`, deserializable `BcvkInspect`, and functions `run_tmt`, `check_dependencies`, `discover_plans`, `run_plan`, `wait_for_ssh`, `cleanup_vm`, and `sanitize_plan_name`. It uses `anyhow`, `clap`, `serde_json`, `tempfile`, and `xshell::cmd`.

## Control Flow
`run_tmt()` checks `bcvk` and `tmt`, discovers plans with optional filters, builds a PID-derived VM name suffix, and runs each plan in sequence. `run_plan()` launches a detached VM from the requested image, waits for SSH by polling `bcvk libvirt ssh`, inspects JSON for SSH port and private key, writes the key to a temporary file, and runs `tmt run` with the connect provisioner against localhost. Each VM is cleaned up after the plan, and failures are collected and reported together. `sanitize_plan_name()` converts plan names into VM-safe suffixes.

## State And Persistence
State includes transient libvirt VMs, temporary private-key files, TMT run IDs named after VMs, and in-memory failure lists. `cleanup_vm()` attempts forced VM removal regardless of plan result.

## Dependencies And Integration Points
This integrates OSTree's dev tooling with `bcvk`, libvirt, TMT, SSH, container boot images, JSON inspection, and shell command orchestration. Extra `tmt_args` pass through after the plan selector.

## Risks
VM names use process ID plus sanitized final path component, so concurrent same-process reuse is unlikely but not globally unique. SSH polling has a fixed 300-second timeout. Failures in cleanup are ignored, which is pragmatic but can leave VMs behind. The temporary key file permissions rely on `tempfile` defaults.

## Test Signals
Dependency version checks, plan discovery output, per-plan pass/fail messages, SSH readiness messages, and final aggregate failure reporting are the observable signals. Unit tests are absent.

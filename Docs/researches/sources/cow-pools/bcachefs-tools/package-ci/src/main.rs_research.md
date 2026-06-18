# File Research: sources/cow-pools/bcachefs-tools/package-ci/src/main.rs

## Purpose
Rust daemon implementing a self-hosted Debian package CI orchestrator for bcachefs-tools.

## Architecture
- Filesystem-backed reconcile loop under `$STATE_DIR`.
- Desired target commit is read from `desired`.
- Per-commit state is stored under `builds/$commit`.
- Each job has `status`, timestamped logs, stable `log` symlink, optional `pid`, and result directory.
- No queue: the daemon continuously reconciles desired state against existing filesystem state.

## Build Matrix
- Distros: `unstable`, `forky`, `trixie`, `questing`, `plucky`.
- Architectures: `amd64`, `ppc64el`, `arm64`.
- Ubuntu ppc64el is skipped because cross-build is marked broken.
- arm64 jobs are remote; ppc64el is local cross-compile.

## Job Phases
1. Source package build.
2. Binary builds across the distro/arch matrix.
3. Publish successful outputs, even if some builds failed.

## Key Types
- `Distro`, `Arch`, `Job`
- `JobStatus`
- `BuildState`
- `Config`
- `RunningJob`
- `Orchestrator`
- `Signals`

## Important Behavior
- `effective_status()` detects stale `building` jobs by checking tracked children and `kill(pid, 0)`, then marks dead jobs failed.
- `reap_children()` updates statuses on child exit and kills builds exceeding the configured timeout.
- Local/remote concurrency is limited independently.
- Logs are redirected to per-job files.
- Tagged commits publish to `release`; other commits publish to `snapshot`.
- `SIGUSR1` wakes the loop, while SIGTERM/SIGINT trigger shutdown and child termination.
- Writes `orchestrator.pid` on startup and removes it on shutdown.

## Default Config
- Git repo: `/var/www/git/bcachefs-tools.git`
- State dir: `/home/aptbcachefsorg/package-ci`
- Scripts dir: `/home/aptbcachefsorg/package-ci/scripts`
- arm64 host: `farm1.evilpiepirate.org`
- Rust version: `1.89.0`
- Max local jobs: 2
- Max remote jobs: 1
- Poll interval: 60 seconds
- Build timeout: 2 hours

## Dependencies
Uses `anyhow`, `chrono`, `log`, `env_logger`, `libc`, and `signal-hook`, plus external shell scripts in `package-ci/scripts`.

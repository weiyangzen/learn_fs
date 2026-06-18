## sources/distributed-fs/tahoe-lafs/.github/workflows/ci.yml

Purpose: GitHub Actions CI for Tahoe-LAFS coverage, integration, and packaging across Linux, macOS, Windows, CPython, and PyPy.

Important elements: triggers on master pushes and pull requests, read-only token permissions, concurrency cancellation for pull request branches, global Hypothesis CI profile, jobs `coverage`, `finish-coverage-report`, `integration`, and `packaging`.

Control flow: coverage matrix checks out full history, sets up Python with pip cache, installs tox/tox-gh-actions, runs tox, uses a Windows passthrough helper for non-blocking pipe ENOSPC behavior, uploads logs, and reports parallel Coveralls results. Integration installs Tor per OS, runs tox integration or force-Foolscap mode, and uploads Eliot logs on failure. Packaging runs PyInstaller and uploads built artifacts.

State and dependencies: uses GitHub artifact storage, Coveralls tokens, pip cache, Tor packages, Chocolatey on Windows, Homebrew on macOS, and setup-python.

Risks: third-party action versions are pinned only by major version; Coveralls token is embedded. Integration depends on Tor package availability and OS-specific setup.

# Research: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia.go

Purpose: experimental on-demand CDI setup for NVIDIA GPUs. It validates host GPU/driver availability, installs NVIDIA container toolkit components on Debian/Ubuntu, and writes a generated CDI spec.

Important APIs and flow: init registers `nvidia.com/gpu`. `Validate` succeeds if driver version is readable or PCI/WSL GPU devices are found. `newVertex` creates progress vertices. `Run` checks OS release, detects driver/library needs, runs `apt-get update`, installs `gpg`, configures NVIDIA apt repository, installs toolkit and optional driver-library packages, runs `nvidia-ctk cdi generate`, and writes `/etc/cdi/nvidia.yaml`. Helpers run commands with progress streams, parse `/proc/driver/nvidia/version`, scan PCI vendor IDs, read `/etc/os-release`, detect WSL GPU, and glob libcuda paths.

State and persistence: mutates host/package state through apt, writes `/usr/share/keyrings/nvidia-cuda-keyring.gpg`, `/etc/apt/sources.list.d/nvidia-cuda.list`, and `/etc/cdi/nvidia.yaml`. It reads `/proc`, `/sys`, `/etc/os-release`, and library paths.

Dependencies and risks: depends on Debian/Ubuntu apt, network access to NVIDIA repository, root privileges, gpg, nvidia-ctk, kernel driver state, and BuildKit progress. It is explicitly experimental and not normally shipped. Tests cover version parsing only; setup side effects are not integration-tested here.

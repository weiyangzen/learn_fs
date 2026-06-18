# sources/cloud-native/containerd/internal/cri/server/container_create_test.go

## Purpose
This cross-platform suite validates generic container spec construction and helper behavior shared by Linux, Windows, and other builds. It focuses on CRI-to-OCI command resolution, annotations, image-defined volumes, base runtime specs, and Linux system-file mounts where available.

## Important APIs, Types, and Functions
Important helpers and tests include `checkMount`, `TestGeneralContainerSpec`, `TestPodAnnotationPassthroughContainerSpec`, `TestContainerSpecCommand`, `TestVolumeMounts`, `TestContainerAnnotationPassthroughContainerSpec`, `TestBaseRuntimeSpec`, and `TestLinuxContainerMounts`.

## Control Flow, State, and Persistence
Tests construct fake CRI configs, call `buildContainerSpec`, `runtimeSpec`, or `volumeMounts`, and assert in-memory OCI spec output. `TestBaseRuntimeSpec` uses a fake runtime service with a base OCI JSON spec and confirms the loaded base is deep-copied, not mutated. Linux mount tests use fake OS stat behavior to simulate sandbox files.

## Dependencies and Integration Points
The suite covers `customopts.WithProcessArgs`, passthrough annotation matching, image volume deduplication against CRI mounts, Linux idmap propagation to generated volumes, base runtime spec loading, cgroup path correction, and sandbox files such as `/etc/hostname`, `/etc/hosts`, `/etc/resolv.conf`, and `/dev/shm`.

## Risks and Test Signals
Risks include command/args precedence regressions, annotation leakage or omission, non-absolute Linux image volume paths, incorrect userns idmap propagation, accidental base-spec mutation, and missing sandbox mount compatibility. Signals are exact mount, env, annotation, and cgroup path checks.

# sources/cloud-native/containerd/integration/sandbox_clean_remove_windows_test.go

## Purpose

`sandbox_clean_remove_windows_test.go` provides Windows equivalents for sandbox IP cleanup and a raw CRI create/start/stop/remove container smoke test.

## Important APIs, Types, and Functions

- `getTestImage` maps Windows build numbers to compatible nanoserver images.
- `TestSandboxRemoveWithoutIPLeakage` verifies azure-vnet IPAM allocation is released only after sandbox removal.
- Helper functions wrap raw CRI requests for stopping/removing pods and containers.
- `TestCreateContainer` creates a Windows process-isolated sandbox and container using raw gRPC CRI calls.

## Control Flow

The IP cleanup test checks CNI config for azure-vnet IPAM, runs a sandbox, extracts the IP and HNS namespace, reads `azure-vnet-ipam.json` to find the IP allocation, kills the sandbox process, deletes the HNS namespace with `hnsdiag.exe`, waits for NOTREADY, then stops/removes and confirms IP release. The container smoke test selects a compatible nanoserver image, creates a raw sandbox, pulls the image, creates a container with CPU shares and a long-running ping command, starts and stops it, and relies on cleanup callbacks.

## State and Persistence Behavior

The file inspects HNS network namespace state, `azure-vnet-ipam.json`, verbose sandbox info, and CRI object lifecycle state.

## Dependencies and Integration Points

It integrates Windows registry build detection, hcsshim OS version constants, `hnsdiag.exe`, raw CRI gRPC client helpers, Windows CNI/IPAM files, and containerd image fixtures.

## Risks and Edge Cases

It is highly host-specific: compatible images, azure-vnet IPAM config, HNS tooling, and Windows build number mapping must all line up. The JSON walker assumes a stable azure-vnet checkpoint schema.

## Test Signals

Failures signal Windows CNI IP leak regressions or basic CRI lifecycle breakage for Windows process containers.

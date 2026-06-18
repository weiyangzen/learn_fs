# sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic.yml

## Purpose
This reusable/manual workflow provisions an Azure Windows Server VM with Containers and Hyper-V, builds containerd and hcsshim, and runs Windows Hyper-V integration, CRI integration, and critest suites.

## Important APIs, Types, And Functions
It defines Azure, SSH, image, and runtime environment variables, accepts Azure secrets through `workflow_call`, uses Azure login/CLI, SSH/SCP, PowerShell setup scripts, HNS NAT setup, hcsshim build from `master`, generated CRI config for `runhcs-wcow-hypervisor`, `go-junit-report`, `xmlstarlet`, and `actions/github-script` for final stage status.

## Control Flow
The workflow creates log directories and an SSH key, logs into Azure, creates a resource group and VM, enables SSH, installs Windows Containers and Hyper-V, reboots and waits, configures NAT, prepares the test environment, clones/builds containerd and hcsshim on the VM, runs integration tests with `USE_HYPERV=1`, prepares image/config files, runs CRI integration, builds/runs critest, converts logs to JUnit XML, checks that all logical test stages reported success, and always deletes the Azure group.

## State And Persistence
Transient state includes Azure resource groups/VMs, Windows installed features, cloned source trees, built binaries, logs, JUnit XML, and remote containerd services. Cleanup deletes the Azure resource group.

## Dependencies And Integration Points
It integrates with Azure infrastructure, Windows HNS/Hyper-V, hcsshim, containerd scripts, Kubernetes cri-tools, Testgrid-style JUnit output, and periodic trigger workflow.

## Risks
The workflow uses a static `Passw0rdAdmin` value despite a comment saying it will be generated. It clones `http://github.com/containerd/containerd` on the VM rather than the checked-out commit, so tests may not match the triggering revision. Azure resource cleanup is critical. `continue-on-error` stages rely on explicit `SUCCEEDED` outputs for final failure detection.

## Test Signals
Successful integration, CRI integration, critest stages, generated JUnit XML, and resource cleanup are the primary signals.

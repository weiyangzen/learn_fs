# sources/cloud-native/containerd/.github/workflows/windows-periodic.yml

## Purpose
This reusable/manual workflow provisions an Azure Windows Server VM and runs containerd Windows integration, CRI integration, and critest suites without Hyper-V isolation.

## Important APIs, Types, And Functions
It uses Azure secrets, Azure login/CLI, SSH/SCP, Windows setup scripts, HNS NAT setup, repository Makefile targets, cri-tools, go-junit-report, `xmlstarlet`, and `actions/github-script` for final logical stage status.

## Control Flow
The job prepares artifact directories, generates SSH keys, creates an Azure VM, enables SSH, installs the Containers feature, waits for reboot, creates NAT, prepares the VM, clones and builds containerd, runs integration tests, writes image list files, runs CRI integration, builds and runs critest against a registered Windows containerd service, pulls JUnit XML logs, checks stage success outputs, and always deletes the Azure resource group.

## State And Persistence
State is transient Azure VM/resource group state, remote source/build/log files, JUnit reports, and remote containerd service registration. Cleanup removes cloud resources.

## Dependencies And Integration Points
It integrates with periodic trigger workflow, Azure Windows images, Windows container networking, containerd scripts, cri-tools, and external test reporting.

## Risks
Like the Hyper-V workflow, it uses a static admin password and clones the repository from GitHub on the VM rather than testing the checked-out commit. SSH retry logic and NAT setup can be flaky. `continue-on-error` test steps depend on explicit output checks.

## Test Signals
Integration/CRI/critest success outputs, JUnit conversion, and resource cleanup logs are key evidence.

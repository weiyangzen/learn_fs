<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/bootc.yaml -->
## sources/cloud-native/ostree/.github/workflows/bootc.yaml

### Purpose
This GitHub Actions workflow validates OSTree behavior in bootc/container operating-system contexts across CentOS Stream 9 and 10.

### APIs, Types, and Control Flow
The workflow runs on `main` pushes, PRs to `main`, and manual dispatch. Concurrency cancels prior runs per workflow/ref. `unit-tests` checks out full history, sets up bootc on Ubuntu, runs `just unitcontainer` and `just unittest` for each stream, and uploads unit logs on failure. `integration` also enables libvirt, installs `tmt[provision-virtual]`, builds with `just build`, runs `just test-tmt` with a 40 minute timeout, and always archives `/var/tmp/tmt`.

### State, Dependencies, and Integration
It depends on `bootc-dev/actions/bootc-ubuntu-setup@main`, `just`, the repository `Justfile`, TMT plans, libvirt, and bootc images. Artifacts persist unit and TMT logs for debugging.

### Risks and Test Signals
Using an action from `@main` introduces upstream drift. The workflow is integration-heavy and sensitive to virtualization, package mirrors, and bootc image availability. Test signals are stream matrix success and uploaded logs on failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/bootc.yaml -->

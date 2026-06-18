<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvme.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/nvme.rs

Purpose: Host-side NVMe CLI and libnvme helpers for connecting to Mayastor NVMf targets and finding resulting Linux NVMe devices.

Important APIs/types: `NmveConnectGuard` connects on creation and disconnects by NQN on drop. `nvme_discover()` parses `nvme discover` output into key/value maps. `nvme_connect()` runs `nvme connect` with transport/address/NQN and optional host ID/NQN env fallback. Disconnect helpers call `nvme disconnect-all` or `disconnect -n`. Device lookup filters libnvme devices by Mayastor controller model and serial. `get_nvme_resv_report()` runs `nvme resv-report -o json`.

Control flow: command helpers assert or panic when required host setup is missing unless `must_succeed` is false for connect.

State and dependencies: mutates host NVMe connections. Depends on `nvme` CLI, `/etc/nvme/hostid`, `/etc/nvme/hostnqn` or env replacements, libnvme-rs, and root/device permissions.

Risks and test signals: typo in type name (`Nmve`) is API-stable but confusing. A one-second sleep after connect handles device discovery latency. Tests should validate serial-based path lookup before issuing data I/O.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvme.rs -->

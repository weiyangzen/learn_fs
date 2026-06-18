# sources/control-plane/mayastor/scripts/block_devs.sh

Purpose: helper script creating eight 1 GiB file-backed NVMe target namespaces on localhost.

Important APIs/types/functions: uses `truncate`, `modprobe nvmet_tcp`, configfs paths under `/sys/kernel/config/nvmet`, subsystem names `replica0` through `replica7`, namespace `device_path`, `enable`, and port subsystem symlinks.

Control flow: creates `/tmp/<n>.blk` files, configures NVMe TCP port 1 at `127.0.0.1:4420`, then loops creating subsystems/namespaces and linking them into the port.

State/persistence: mutates `/tmp`, loads kernel module, and writes persistent-until-reboot configfs NVMe target state.

Dependencies/integration: useful for local NVMe-oF testing outside io-engine. Requires root privileges and Linux nvmet configfs.

Risks: not idempotent; existing configfs entries cause failures. No cleanup path. Fixed port and paths can conflict with other tests.

Test signals: after running, `nvme discover/connect` against localhost should see the eight replicas.

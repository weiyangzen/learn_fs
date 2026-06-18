## sources/control-plane/csi-driver-iscsi/cmd/iscsiplugin/main.go

Purpose: command-line entrypoint for the iSCSI CSI node plugin.

Control flow defines `--endpoint` defaulting to `unix:///csi/csi.sock` and `--nodeid`, initializes klog flags, parses flags, constructs a driver with `iscsi.NewDriver`, and blocks in `d.Run`. State is limited to parsed flags and the driver/server created by the package.

Dependencies are Go flag/os, klog, and `pkg/iscsi`. Integration points are container args in `deploy/csi-iscsi-node.yaml` and kubelet's CSI socket path. Risks include no validation that `nodeid` is non-empty before serving and unconditional `os.Exit(0)` after `handle`. Test signal is build/compile coverage; no dedicated main tests are present.

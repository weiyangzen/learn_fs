## sources/control-plane/csi-driver-nfs/test/sanity/params.yaml

Purpose: supplies the CSI sanity test volume parameters for a local NFS server. The file maps `server` to `127.0.0.1` and `share` to `/`, matching the local Docker NFS server launched by `run-test.sh`.

State is declarative and read by `csi-sanity` through `--csi.testvolumeparameters`. Dependencies are the NFS plugin's parameter schema and the local server setup. Risks include assuming loopback works from the plugin process namespace and using the root export for all sanity test volumes. Test signal is direct input for CSI RPC sanity tests.

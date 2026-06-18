## sources/control-plane/csi-driver-nfs/test/utils/nfs_log.sh

Purpose: collects useful cluster and NFS CSI driver diagnostics at the end of e2e runs. It prints nodes, default namespace pods, kube-system pods, controller logs, and node logs.

Important flow: it defaults `NS=kube-system`, `CONTAINER=nfs`, and `DRIVER=nfs`, with an optional driver name argument. It selects controller pods by `app=csi-$DRIVER-controller` and node pods by `app=csi-$DRIVER-node`, then pipes pod names into `kubectl logs --prefix -c nfs`.

State is read-only cluster log/status data. Dependencies are kubectl, awk, xargs, standard app labels, and container name `nfs`. Risks include xargs running kubectl with no pod names, missing logs from restarted containers because `--previous` is not used, and hard-coded container/namespace assumptions. Test signal is diagnostic rather than pass/fail.

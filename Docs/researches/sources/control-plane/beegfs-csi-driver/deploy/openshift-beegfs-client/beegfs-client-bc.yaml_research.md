<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-bc.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-bc.yaml

Purpose: OpenShift BuildConfig stack for producing a BeeGFS client image from the OpenShift `driver-toolkit`.

Important APIs and flow: creates an `ImageStream`, a `ConfigMap` containing `poststart.sh`, and a `BuildConfig`. The Dockerfile installs BeeGFS repository metadata, imports the BeeGFS GPG key, installs `beegfs-client`, `beegfs-utils`, and `beegfs-helperd`, clears `beegfs-mounts.conf`, disables helperd authentication, and adds the postStart script. The postStart script copies `beegfs-client.conf` and `beegfs-ctl` into `/plugin/client` and may install matching `kernel-devel`/`kernel-modules` before restarting the client.

State and persistence: produces the `beegfs-client:latest` ImageStreamTag and populates files later mounted through a hostPath by the DaemonSet.

Dependencies and integration points: requires OpenShift build APIs, `driver-toolkit:latest`, yum access/entitlements, BeeGFS release repos, and namespace `beegfs-csi`.

Risks and test signals: privileged system package installation and helperd auth changes are operationally sensitive. Test via OpenShift build logs, resulting image tag, and DaemonSet postStart behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-bc.yaml -->

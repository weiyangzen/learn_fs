<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/csi-doctor.sh -->
## sources/control-plane/juicefs-csi-driver/scripts/csi-doctor.sh

### Purpose
`csi-doctor.sh` is an operator diagnostic script for JuiceFS CSI. It discovers mount pods related to an application pod, prints debug information, locates app pods using a mount pod, collects CSI/mount/app/PV/PVC logs and YAMLs, runs `juicefs doctor` inside mount pods, and executes arbitrary commands in all mount pods.

### Important APIs, Types, And Functions
Commands include `debug`, `get-mount`, `get-oplog`, `get-app`, `collect`, `exec`, `doctor`, and `help`. Functions include `debug_app_pod`, `debug_pvc`, `get_mount_pod`, `get_oplog`, `get_app_pod`, `mount_exec`, `collect_pv`, `collect_juicefs_csi_msg`, `pd_collect`, `collect`, `doctor`, and `main`. Environment variables include `JFS_NS`, `APP_NS`, and `KBCTL`.

### Control Flow
`main` parses an action and optional app namespace. Debug flows read app pod events, PVCs, node name, PV CSI driver/volume handle, mount pod names on the same node, mount pod annotations that contain the app pod UID, mount pod logs, controller logs when PVCs are unbound, and CSI node logs. Collection flows create a temporary diagnosis directory, save app/PVC/PV/mount/CSI YAMLs, descriptions, logs, and resource usage, copy the script into a mount pod to run `doctor`, copy results back, tar the directory, and remove the temp directory. Lookup commands map app pods to mount pods or mount pods back to app pods using PV handles and reference annotations.

### State, Persistence, And Dependencies
The script reads Kubernetes state and writes local archives under the current directory after staging under `/tmp/<app>.diagnose`. It depends on `kubectl` or `KBCTL`, `timeout`, `grep -P`, `awk`, `tar`, `df`, `juicefs doctor` inside mount pods, and expected JuiceFS labels/annotations.

### Integration Points
It is a support tool for clusters running JuiceFS CSI. It depends on mount pods labeled `app.kubernetes.io/name=juicefs-mount`, CSI controller/node pod labels, PV CSI driver `csi.juicefs.com`, mount pod annotation conventions, and access log/internal file naming including `prefix-internal`.

### Risks
Many variables are unquoted, so names with unusual characters can break commands. `SHOULD_CHECK_CSI_CONRTROLLER` is misspelled but internally consistent. Some variables (`PVC_NAME`, `PV_NAME`, `diagnose_result`) are unused or referenced before assignment. Several paths call literal `kubectl` instead of `${kbctl}`. `grep -P` is not portable to all environments. The collection path assumes at least one mount pod exists before copying/running doctor. Logs and YAMLs may include secrets.

### Test Signals
Useful validation is best done with mocked kubectl output for app-to-PV-to-mount-pod discovery, unbound PVC controller-log triggering, app lookup from mount annotations, prefix-internal access-log path selection, no-mount-pod collection behavior, `KBCTL` override, and archive contents.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/csi-doctor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/auto-grow-storage.sh -->
# sources/control-plane/rook/tests/scripts/auto-grow-storage.sh

Purpose: experimental automation for responding to Ceph OSD near-full/critical-full alerts by either resizing PVCs vertically or increasing OSD counts horizontally. It also bootstraps Prometheus prerequisites used to observe Rook alerts.

Important APIs and control flow: `calculateSize` normalizes Mi/Gi/Ti values into a global numeric unit, `compareSizes` compares desired and maximum sizes, `growVertically` patches a PVC storage request, `growHorizontally` locates the owning `storageClassDeviceSet` from PVC labels and patches its count, `growOSD` loops over Alertmanager alerts and invokes the chosen growth mode, `creatingPrerequisites` applies Prometheus operator and Rook monitoring manifests, and the command dispatcher accepts `count` or `size`.

State, persistence, and integration: it creates monitoring resources, reads Alertmanager through a toolbox pod, and patches PVCs or `CephCluster` specs. Dependencies include `kubectl`, `jq`, `bc`, Prometheus, Alertmanager service on node port 30900, Rook toolbox, and PVC-based OSDs. Risks include global variables, decimal unit approximations using 1000 not 1024, unquoted JSON patches, infinite loop behavior, hard-coded namespace/service assumptions, and live capacity-changing side effects. Test signals are printed patch results and subsequent Ceph/PVC state changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/auto-grow-storage.sh -->

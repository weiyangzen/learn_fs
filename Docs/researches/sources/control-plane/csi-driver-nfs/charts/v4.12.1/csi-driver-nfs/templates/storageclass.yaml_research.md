# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template creates optional NFS `StorageClass` resources for chart 4.12.1.

## APIs, Control Flow, and State
It supports a single `storageClass` block and a list-style `storageClasses` block. Rendered classes use `driver.name` as provisioner, user-supplied NFS parameters, reclaim policy, volume binding mode, expansion settings, annotations, labels, and mount options. Multiple classes can express different NFS shares, reclaim policies, or mount behavior.

## Dependencies and Integration Points
The CSI provisioner consumes class parameters during PVC provisioning, and the NFS driver uses server/share/subDir and mount option inputs. It is unchanged from 4.12.0.

## Risks and Test Signals
Bad parameter maps fail at provisioning time rather than render time. Test default disabled rendering, single-class rendering, multi-class rendering, PVC creation, expansion, and reclaim behavior.

# sources/control-plane/ceph-csi/internal/rbd/clone.go

Purpose: Implements PVC-to-PVC RBD clone creation using temporary clones and snapshots to manage clone depth, flattening, metadata cleanup, encryption config, and QoS adjustment.

Important APIs/types/functions: Methods on `rbdVolume`: `checkCloneImage`, `generateTempClone`, `createCloneFromImage`, `doSnapClone`; helper `isTempClonedImage`.

Control flow: `checkCloneImage` reconstructs or resumes clone state by checking a temporary clone and snapshot. Missing temp snapshot triggers `createRBDClone`; missing temp clone causes parent snapshot cleanup if needed; existing temp snapshot allows final clone creation and flatten task scheduling. `createCloneFromImage` connects to the journal, performs `doSnapClone`, obtains image ID, copies encryption config, stores image ID in the journal, expands to requested size, and adjusts RBD QoS. `doSnapClone` creates a temp clone from parent, clears Kubernetes volume metadata on the temp clone, creates the final clone from a temp snapshot, and copies encryption config.

State and persistence behavior: Mutates RBD images, snapshots, clone relationships, image metadata, encryption metadata, volume journal image IDs, resize state, and QoS state. Temporary clone names append `-temp`; temporary snapshots use related image names.

Dependencies and integration points: Depends on go-ceph/librbd features, RBD journal, snapshot helpers, cleanup helpers, Kubernetes volume metadata key list, encryption config copying, and QoS adjustment paths including cgroup/NBD handling.

Risks: Clone recovery is complex and depends on recognizing partially-created temp images/snapshots. Cleanup defers depend on shared `err` and `errClone` state. Temp clone naming must remain collision-free. Clearing metadata only removes configured Kubernetes metadata keys; other metadata may propagate. QoS adjustment after resize means clone QoS behavior depends on metadata and mounter-specific handlers.

Test signals: No direct tests in this subset. Existing broader RBD tests would be needed for partial clone recovery, cleanup, metadata propagation, encryption, and QoS interactions.

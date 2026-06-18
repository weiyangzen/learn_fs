<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/singleton.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/singleton.yaml

## Purpose
Makes the BeegfsDriver API a singleton by restricting CR names to `csi-beegfs-cr`.

## Important APIs, Types, And Functions
JSON6902 add operation inserts `metadata.properties.name` schema with `pattern: ^csi-beegfs-cr$`.

## Control Flow
Kustomize applies the patch to the first CRD version schema. The API server then rejects BeegfsDriver objects with any other name.

## State And Persistence
No state itself; changes persisted CRD validation behavior.

## Dependencies And Integration Points
Used by `config/crd/kustomization.yaml`. Controller and tests assume a single CR but do not enforce the name themselves.

## Risks And Edge Cases
The patch targets `/spec/versions/0`, so adding versions or reordering versions can silently patch the wrong schema. Envtest does not load this patch, leaving a coverage gap.

## Test Signals
Controller tests cover duplicate object creation but explicitly note they do not cover the patched name restriction.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/singleton.yaml -->

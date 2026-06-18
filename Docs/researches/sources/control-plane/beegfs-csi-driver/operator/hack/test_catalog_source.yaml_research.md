<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/test_catalog_source.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/hack/test_catalog_source.yaml

## Purpose
OpenShift development CatalogSource for testing operator catalog images and upgrade flows.

## Important APIs, Types, And Functions
Defines operators.coreos.com/v1alpha1 CatalogSource `netapp-operators` in `openshift-marketplace`, sourceType `grpc`, image placeholder `docker.repo.eng.netapp.com/<username>/beegfs-csi-driver-operator-catalog:<vX.X.X>`, and registry polling every 30s.

## Control Flow
When applied, OLM watches the catalog image and refreshes it on the poll interval.

## State And Persistence
Creates persistent OpenShift marketplace catalog state until deleted.

## Dependencies And Integration Points
Depends on OLM/OpenShift and a pushed catalog image.

## Risks And Edge Cases
Contains internal registry placeholders and old NetApp naming. Polling with imagePullPolicy Always is useful for development but noisy for long-lived clusters.

## Test Signals
Manual OLM integration testing helper.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/test_catalog_source.yaml -->

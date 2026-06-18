# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/Chart.yaml

## Purpose
This metadata file identifies the v4.3.0 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It uses Helm chart API `v1` with `name: csi-driver-nfs`, the standard description, `version: v4.3.0`, and `appVersion: v4.3.0`.

## Control Flow, State, and Persistence
It has no templating control flow. Helm records these fields in chart packaging and release metadata.

## Dependencies and Integration Points
The metadata should align with v4.3.0 image tags in values. The leading `v` version style matches v4.2.0 and v4.4.0 chart metadata but differs from v4.13.x.

## Risks and Test Signals
Risks are chart/app version drift and version parser assumptions. Signals are `helm lint`, chart package inspection, and rendered nfsplugin tag validation.

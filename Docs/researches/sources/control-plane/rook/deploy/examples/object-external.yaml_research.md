# sources/control-plane/rook/deploy/examples/object-external.yaml

Purpose: registers an externally hosted RGW endpoint as a Rook `CephObjectStore`.

Important APIs/types/functions: `CephObjectStore/external-store` with `gateway.port: 80` and `gateway.externalRgwEndpoints` containing IP `192.168.39.182`.

Control flow: Rook treats the store as externally reachable and exposes/provisions bucket resources against the configured RGW endpoint rather than deploying RGW pods.

State and persistence: bucket and object state live in the external Ceph/RGW cluster; Kubernetes stores only the object store reference.

Dependencies/integration: requires network reachability to the external endpoint and compatible RGW admin credentials/configuration.

Risks: static IP must be edited for each environment, and Rook cannot control external RGW availability.

Test signals: object store status and successful S3/admin calls through the external endpoint.

# sources/control-plane/rook/deploy/examples/nvmeof-test.yaml

Purpose: provides a minimal test manifest for a Ceph NVMe-oF gateway.

Important APIs/types/functions: `CephNVMeOFGateway/nvmeof` in `rook-ceph`; the spec configures the gateway server count, pool/reference parameters, and test-friendly settings for the NVMe-oF controller.

Control flow: Rook's NVMe-oF controller reconciles the gateway CR into gateway pods/services that front Ceph RBD over NVMe/TCP.

State and persistence: desired gateway topology is persisted in the CR; exported block data remains in Ceph pools/images.

Dependencies/integration: requires the NVMe-oF CRD/controller, Ceph cluster, and kernel/userland client support for NVMe/TCP tests.

Risks: test defaults are not production sizing, and gateway availability depends on the configured replica count and service exposure.

Test signals: gateway pod ready, service reachable on the NVMe-oF port, and client subsystem discovery/connect succeeds.

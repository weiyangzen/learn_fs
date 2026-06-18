## sources/cloud-native/buildkit/util/network/cniprovider/createns_windows.go

Purpose: Windows Host Compute Network namespace lifecycle for CNI provider.

Important functions: `createNetNS`, `setNetNS`, `unmountNetNS`, `deleteNetNS`, `cleanOldNamespaces`.

Control flow: creates an HCN guest namespace and returns its ID. `setNetNS` ensures `specs.Windows` and `WindowsNetwork` exist, then sets `NetworkNamespace`. Unmount is a no-op. Delete looks up HCN namespace by ID and deletes it. Old namespace cleanup is not implemented.

State/persistence: creates/deletes Windows HCN namespaces. Dependencies: Microsoft hcsshim/hcn, OCI specs.

Integration points: Windows CNI provider support. Risks: comment in shared provider notes Windows pool cleanup is limited; stale HCN namespaces may remain after crashes. Test signals: no local Windows tests.

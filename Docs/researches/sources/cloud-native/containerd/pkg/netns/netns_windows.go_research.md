# sources/cloud-native/containerd/pkg/netns/netns_windows.go

Purpose: Windows network namespace implementation backed by HCN namespaces.

Important APIs/types/functions: `NewNetNS` creates an `hcn.HostComputeNamespace` and stores its ID as `path`; `NewNetNSFromPID` is not implemented; `LoadNetNS` wraps an existing ID; `Remove` gets the namespace by ID and deletes it, treating not-found as success; `Closed` returns true when HCN reports not found; `GetPath` returns the ID.

Control flow: create, get, delete, and not-found classification are delegated to hcsshim HCN APIs. Remove is idempotent.

State/persistence: namespace state lives in Windows HCN. `NetNS.path` is an HCN namespace ID rather than a filesystem path.

Dependencies/integration: imports `github.com/Microsoft/hcsshim/hcn`. Windows sandbox networking can use the returned ID.

Risks: pid-based loading and `Do` are unsupported. HCN errors other than not-found propagate. Naming the ID as `path` preserves API shape but can confuse callers expecting a filesystem path.

Test signals: Windows integration tests should cover create/delete/idempotent remove, closed detection, and HCN not-found handling.

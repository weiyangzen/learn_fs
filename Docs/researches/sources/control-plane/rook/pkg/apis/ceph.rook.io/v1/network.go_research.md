# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network.go

Purpose: validates and converts Ceph network configuration, especially host networking, Multus selectors, and address ranges.

Important APIs/types/functions: package variable `enforceHostNetwork`, methods `NetworkSpec.IsMultus`, `NetworkSpec.IsHost`, `NetworkSpec.NetworkHasSelection`, `NetworkSpec.GetNetworkSelection`, `AddressRangesSpec.IsEmpty`, `AddressRangesSpec.Validate`, `CIDRList.String`, functions `ValidateNetworkSpec`, `ValidateNetworkSpecUpdate`, `NetworkSelectionsToAnnotationValue`, `SetEnforceHostNetwork`, and `EnforceHostNetwork`.

Control flow: validation rejects legacy `hostNetwork` with non-default providers, requires selectors for Multus, parses public/cluster selectors with NetworkAttachmentDefinition utilities, restricts address ranges to host or Multus networking, validates CIDRs, and allows only limited provider updates involving `host`.

State and persistence: global `enforceHostNetwork` reflects operator config; network specs persist in CephCluster CRs and produce pod annotations.

Dependencies/integration: depends on Multus NAD client utilities, Go `net` CIDR parsing, JSON marshalling, and Rook network provider constants/types.

Risks: global enforce flag affects all specs in-process; legacy single-object JSON selector compatibility is intentionally hidden; update validation allows host toggles but rejects other provider changes.

Test signals: Multus selector parsing, multiple selection rejection, address range validation, host-network override, provider update policy, and annotation JSON output.

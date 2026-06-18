# sources/control-plane/ceph-csi/internal/nvmeof/util_test.go

Purpose: Unit tests for UUID normalization used during NVMe namespace device lookup.

Important APIs/types/functions: Tests `formatUUID`.

Control flow: Cases cover a compact UUID, dash-heavy UUID input, leading/trailing dashes, invalid input, and empty string. Valid inputs are normalized to standard dashed UUID form; invalid inputs are returned unchanged.

State and persistence behavior: Pure function test.

Dependencies and integration points: Uses `testify/require`. Supports `GetNamespaceDeviceByUUID` behavior in the initiator.

Risks: Does not test actual `/dev/disk/by-id` lookup or retry behavior.

Test signals: Good signal for normalization compatibility with UUID symlink naming.

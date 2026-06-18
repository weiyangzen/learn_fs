# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.h

Purpose: declares the small model object representing one CellServDB server address and comment.

Important APIs and state: `CellIp` contains `NSString *ip` and `NSString *ipComment`. It exposes initialization, deallocation, setters/getters for address and comment, and `description` for serializing back to CellServDB line format.

Control flow and persistence: persistence is indirect. `AFSPropertyManager` constructs `CellIp` instances while parsing `CellServDB`, `IpConfiguratorCommander` edits them in the IP table, and `DBCellElement description` serializes them for privileged writeback.

Dependencies and integration: imports Cocoa only. It is owned by `DBCellElement` arrays and consumed by UI table delegates.

Risks: the class performs no validation of IP address or hostname syntax. Manual retain/release means initial literal defaults and later retained strings must be handled carefully.

Test signals: construction defaults, setters with nil/non-nil values, description formatting, memory management under repeated edits, and serialization round trips through `DBCellElement`.

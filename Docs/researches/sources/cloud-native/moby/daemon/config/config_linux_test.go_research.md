<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux_test.go -->
# sources/cloud-native/moby/daemon/config/config_linux_test.go

## Purpose
Tests Linux-specific daemon configuration parsing, merging, feature flags, host gateway IP migration, legacy compatibility, and firewall mark validation.

## Important APIs, Types, And Functions
Tests cover `getConflictFreeConfiguration`, `MergeDaemonConfigurations`, `New`, `GetInitPath`, host-gateway IP options, and `validateFwMarkMask`.

## Control Flow
Table tests construct JSON config and flag sets, merge config, assert decoded platform fields, or assert precise conflict/validation errors. Host-gateway tests exercise old/new config names and flag conflicts.

## State And Persistence Behavior
Uses temp daemon JSON files and in-memory flag/config values only.

## Dependencies And Integration Points
Depends on pflag, daemon opts, netip, container API types, and gotest assertions. It guards Linux platform hooks used by common config merge.

## Risks And Test Signals
Signals include named option flattening, default ulimits/log/network opts, feature map conflicts, `docker-init` default precedence, IPv4/IPv6 host gateway cardinality, legacy skip-validate keys, and fwmark mask syntax.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux_test.go -->

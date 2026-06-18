<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api_test.go

Purpose: unit tests for `PortBindingReq.Compare`.

Important APIs/functions: `TestPortBindingReqsCompare` mutates a base TCP binding and asserts ordering relations.

Control flow: cases compare same object, mapper names, container port, protocol, host port, exact versus range, and host-port-end differences. Each comparison checks both forward and reverse sign.

State and persistence: no persistent state; pure value comparison.

Dependencies and integration points: uses `types.PortBinding`, `types.TCP/UDP`, and `gotest.tools` assertions. It protects sort behavior used before invoking port mappers.

Risks and test signals: test is focused but does not cover host IP/container IP ordering or invalid IP inputs. It gives good regression signal for the highest-level grouping fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api_test.go -->

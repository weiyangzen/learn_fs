# sources/control-plane/ceph-csi/internal/nvmeof/controller/mutable_params_test.go

Purpose: Tests parsing for CSI `mutable_parameters` consumed by NVMe-oF volumes: gateway QoS limits and external host allow lists.

Important APIs/types/functions: Exercises `parseQoSParameters`, `parseHostsParameters`, `AllowHostNQNs`, and `nvmeof.NVMeoFQosVolume`. Test helpers compare pointer-valued uint64 fields and YAML-decoded string slices.

Control flow: Table-driven QoS tests cover absent parameters, complete and partial limits, zero as an accepted unlimited value, empty strings ignored, invalid strings, negatives, overflow, floats, and mixed valid/invalid maps. Host tests distinguish absent key (`nil`, no modification), present empty key (empty slice, remove all hosts), YAML list formats, wildcard, and invalid YAML/map/string inputs.

State and persistence behavior: No persistent state. The tests encode semantic state transitions used by `ControllerModifyVolume`: nil hosts means leave current gateway hosts unchanged, empty slice means reconcile to no hosts.

Dependencies and integration points: Depends on `ghodss/yaml` behavior through the production parser and `testify` assertions. Guards the VolumeAttributesClass interface consumed by controller create/modify flows.

Risks: Tests do not validate higher-level rejection of RBD QoS on NVMe-oF volumes, nor gateway effects of parsed values. Host NQN strings are not semantically validated beyond YAML string decoding.

Test signals: Strong coverage for parser edge cases and sentinel semantics. Integration with gateway reconciliation remains untested here.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/psci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/psci.yaml

## Purpose
This schema describes ARM Power State Coordination Interface firmware nodes used by Linux to perform CPU suspend, hotplug, CPU on/off, migration, and hierarchical power-domain control.

## Important APIs, Types, And Functions
It validates `psci` node name, compatible strings for `arm,psci`, `arm,psci-0.2`, and `arm,psci-1.0`, the call `method` (`smc` or `hvc`), legacy function IDs `cpu_suspend`, `cpu_off`, `cpu_on`, `migrate`, `arm,psci-suspend-param`, and `power-domain-*` children referenced to the generic power-domain schema.

## Control Flow
An `allOf` conditional requires `cpu_off` and `cpu_on` when the legacy `arm,psci` compatible is present. PSCI 0.2 and 1.0 branches allow standardized function IDs without explicit numeric properties.

## State And Persistence
The DT stores firmware ABI selection, call conduit, optional legacy function IDs, and power-domain topology. Runtime state is managed by PSCI firmware, CPU hotplug/idle, and power-domain code.

## Dependencies And Integration Points
It integrates with CPU `enable-method = "psci"`, idle-state bindings, domain-idle-state bindings, and generic power-domain bindings.

## Risks
Wrong `method` can make every PSCI call trap to the wrong firmware conduit. Legacy and modern compatible mixing must preserve required function IDs for old kernels.

## Test Signals
`dt_binding_check` validates examples and conditionals. Runtime signals include CPU bring-up, hotplug, suspend, idle-state entry, and hierarchical power-domain operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/psci.yaml -->

# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,nspire-misc.yaml

Purpose: Schema for the TI Nspire miscellaneous system controller block, a syscon/simple-MFD register area containing at least a reboot controller child.

Important schema surface and control flow: compatible must be the ordered sequence `ti,nspire-misc`, `syscon`, `simple-mfd`; `reg` and `reboot` are required. The `reboot` child references `/schemas/power/reset/syscon-reboot.yaml`, so offset/value semantics are validated by the generic syscon reboot binding.

State, dependencies, and integration: DT state creates a syscon regmap for the MISC register window and a child reboot device that writes a reset value at a configured offset. Dependencies include syscon, simple-mfd, and syscon-reboot bindings plus reset/power drivers. Risks include wrong compatible order, incorrect reboot offset/value causing failed or unsafe reset, and omitting `simple-mfd` so the reboot child is not populated. Test signals are `dt_binding_check`, syscon-reboot child validation, and runtime reboot path testing.
